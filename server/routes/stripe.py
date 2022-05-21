import stripe
import secrets
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

    def subscription_deleted(self, data):
        self._account.remove_subscription(data['object']['id'])
        if data['object']['status'] == 'unpaid':
            self._account.downgrade_license(data['object']['id'])

    def invoice_paid(self, data):
        # Get common information
        account = self._account.get_by_email(data['object']['customer_email'])[0]
        product = self._account.get_products_by_stripe(data['object']['lines']['data'][0]['plan']['product'])[0]
        subscription_stripe = data['object']['subscription']
        account_id = account['id']
        product_id = product['id']

        # Update licence entry
        self._account.change_license(account_id, product_id)

        # Create entry to the subscriptions table
        account = self._account.get_by_customer(data['object']['customer'])[0]
        stripe_id = data['object']['subscription']
        price_id = data['object']['lines']['data'][0]['price']['id']
        created = data['object']['created'],
        self._account.new_subscription(account['id'], price_id, stripe_id, created)

        # Create entry to the payments table
        price = data['object']['amount_paid']
        status = 'success'
        stripe_id = data['object']['id']
        invoice = data['object']['invoice_pdf']
        self._account.new_purchase(subscription_stripe, created, price, status, stripe_id, invoice)

        # Send email
        email = account['email']
        payment_method = stripe.Subscription.retrieve(data['object']['subscription'])['default_payment_method']
        name = stripe.PaymentMethod.retrieve(payment_method)['billing_details']['name']
        date = datetime.datetime.utcfromtimestamp(data['object']['created'])
        date = f"{date.strftime('%B')} {date.strftime('%d')}, {date.strftime('%Y')}"
        resources = product['resources']
        self._mail.send_payment_success_email(email, price, name, date, resources, stripe_id)

    def invoice_payment_failed(self, data):
        # if data['object']['billing_reason'] == 'subscription_cycle':
        # Get common information
        account = self._account.get_by_customer(data['object']['customer'])[0]
        subscription_stripe = data['object']['subscription']
        # Create entry to the payments table
        account_id = account['id']
        created = data['object']['created']
        price = data['object']['amount_due']
        status = 'error'
        stripe_id = data['object']['id']
        invoice = None
        self._account.new_purchase(subscription_stripe, created, price, status, stripe_id, invoice)
        # Add entry to mail table
        code = secrets.token_urlsafe(64)
        self._account.create_mail(account_id, 'update_payment', code)
        # Send email
        payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data']
        email = data['object']['customer_email']
        card = payment_methods[0]['card']['last4']
        self._mail.send_payment_failed_email(email, price, card, code)

    def customer_source_expiring(self, data):
        account = self._account.get_by_email(data['object']['owner']['email'])[0]
        # Get customer payment method
        payment_methods = stripe.Customer.list_payment_methods(account['stripe_id'], type="card")['data']
        # Add entry to mail table
        code = secrets.token_urlsafe(64)
        self._account.create_mail(account['id'], 'update_payment', code)
        # Send email
        email = account['email']
        card = payment_methods[0]['card']['brand'].capitalize()
        card_number = payment_methods[0]['card']['last4']
        self._mail.send_expiring_card_email(email, card, card_number, code)

    def payment_method_attached(self, data):
        # Get all customer payment methods
        payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data'][1:]
        # Delete old payment methods
        for i in payment_methods:
            stripe.PaymentMethod.detach(i['id'])
        # Update customer's name and assign the current payment method to him/her
        stripe.Customer.modify(data['object']['customer'], name=data['object']['billing_details']['name'], invoice_settings={"default_payment_method":data['object']['id']})
        # Expire mail codes
        account = self._account.get_by_customer(data['object']['customer'])[0]
        self._account.clean_mail(account['id'], 'update_payment')
