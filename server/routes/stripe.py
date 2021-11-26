import stripe
import datetime
from flask import Blueprint, jsonify, request

import models.account
import mail.mail

class Stripe:
    def __init__(self, sql, conf):
        self._conf = conf
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)
        # Init mail
        self._mail = mail.mail.Mail(conf)

    def blueprint(self):
        # Init blueprint
        stripe_blueprint = Blueprint('stripe', __name__, template_folder='stripe')

        @stripe_blueprint.route('/stripe/webhook', methods=['POST'])
        def stripe_webhook_method():
            try:
                sig_header = request.headers.get('stripe-signature')
                event = stripe.Webhook.construct_event(payload=request.data, sig_header=sig_header, secret=self._conf['stripe']['webhook_secret'])
            except Exception as e:
                return e

            if event['type'] == 'customer.subscription.created':
                self.subscription_created(event['data'])
            elif event['type'] == 'customer.subscription.deleted':
                self.subscription_deleted(event['data'])
            elif event['type'] == 'invoice.paid':
                self.invoice_paid(event['data'])
            elif event['type'] == 'invoice.payment_failed':
                self.invoice_payment_failed(event['data'])
            elif event['type'] == 'customer.source.expiring':
                self.customer_source_expiring(event['data'])
            elif event['type'] == 'payment_method.attached':
                self.payment_method_attached(event['data'])
            print(event['type'])

            return jsonify({'status': 'success'})

        return stripe_blueprint

    ####################
    # Internal Methods #
    ####################
    def subscription_created(self, data):
        # Remove last subscriptions
        subscriptions = stripe.Subscription.list(customer=data['object']['customer'])
        for subscription in subscriptions['data'][1:]:
            stripe.Subscription.delete(subscription['id'])

        # Create entry to the subscriptions table
        account = self._account.get_by_customer(data['object']['customer'])[0]
        product = self._account.get_products_by_stripe(data['object']['items']['data'][0]['plan']['id'])[0]
        stripe_id = data['object']['id']
        created = data['object']['created'],
        self._account.new_subscription(account['id'], product['id'], stripe_id, created)

    def subscription_deleted(self, data):
        account = self._account.get_by_customer(data['object']['customer'])[0]
        self._account.remove_subscription(account['id'])

    def invoice_paid(self, data):
        # Get common information
        account = self._account.get_by_email(data['object']['customer_email'])[0]
        product = self._account.get_products_by_stripe(data['object']['lines']['data'][0]['plan']['id'])[0]
        account_id = account['id']
        product_id = product['id']

        # Update licence entry
        self._account.change_license(account_id, product_id)

        # Create entry to the payments table
        created = data['object']['created']
        price = data['object']['amount_paid']
        status = 'success'
        error = None
        stripe_id = data['object']['id']
        invoice = data['object']['invoice_pdf']
        self._account.new_purchase(account_id,  product_id, created, price, status, error, stripe_id, invoice)

        # Send email
        email = account['email']
        price = data['object']['amount_paid'] / 100
        name = data['object']['customer_name']
        date = datetime.datetime.utcfromtimestamp(data['object']['created'])
        date = f"{date.strftime('%B')} {date.strftime('%d')}, {date.strftime('%Y')}"
        resources = product['resources']
        self._mail.send_payment_success_email(email, price, name, date, resources, stripe_id)

    def invoice_payment_failed(self, data):
        if data['object']['billing_reason'] == 'subscription_cycle':
            payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data']
            email = data['object']['customer_email']
            price = data['object']['amount_due'] / 100
            card = payment_methods[0]['card']['last4']
            self._mail.send_payment_failed_email(email, price, card)

    def customer_source_expiring(self, data):
        account = self._account.get_by_email('polius_12@hotmail.com')[0] # data['object']['owner']['email']
        # Get customer payment method
        payment_methods = stripe.Customer.list_payment_methods(account['stripe_id'], type="card")['data']
        # Send email
        email = account['email']
        card = payment_methods[0]['card']['brand'].capitalize()
        card_number = payment_methods[0]['card']['last4']
        self._mail.send_expiring_card_email(email, card, card_number)

    def payment_method_attached(self, data):
        # Get all customer payment methods
        payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data'][1:]
        # Delete old payment methods
        for i in payment_methods:
            stripe.PaymentMethod.detach(i['id'])
        # Update customer's name to the current payment name
        stripe.Customer.modify(data['object']['customer'], name=data['object']['billing_details']['name'])
