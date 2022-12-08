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
            elif event['type'] == 'customer.subscription.updated':
                self.subscription_updated(event['data'])
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
        subscriptions = stripe.Subscription.list(customer=data['object']['customer'])
        for subscription in subscriptions['data'][1:]:
            # Expire unpaid payments and mark unpaid invoices to 'void'
            invoices = stripe.Invoice.list(subscription=subscription['id'])['data']
            for invoice in invoices:
                if invoice['status'] == 'open':
                    stripe.Invoice.void_invoice(invoice['id'])
                    self._account.expire_invoice(invoice['id'])
            # Remove last subscription
            stripe.Subscription.delete(subscription['id'])
            self._account.remove_subscription(subscription['id'])

    def subscription_updated(self, data):
        if data['object']['status'] == 'unpaid':
            stripe.Invoice.void_invoice(data['object']['latest_invoice'])
            stripe.Subscription.delete(data['object']['id'])
            self._account.expire_invoice(data['object']['latest_invoice'])
            self._account.remove_subscription(data['object']['id'])
            self._account.downgrade_license(data['object']['id'])

    def invoice_paid(self, data):
        # Create entry to the subscriptions table
        account = self._account.get_by_customer(data['object']['customer'])[0]
        stripe_id = data['object']['subscription']
        product_id = data['object']['lines']['data'][0]['price']['product']
        price_id = data['object']['lines']['data'][0]['price']['id']
        created_date = data['object']['created'],
        self._account.new_subscription(account['id'], product_id, price_id, stripe_id, created_date)

        # Create entry to the payments table
        subscription_id = data['object']['subscription']
        price = data['object']['amount_paid'] / 100
        status = 'paid'
        stripe_id = data['object']['id']
        next_payment_attempt = data['object']['next_payment_attempt']
        invoice_url = data['object']['hosted_invoice_url']
        self._account.new_purchase(subscription_id, created_date, price, status, stripe_id, next_payment_attempt, invoice_url)

        # Update licence entry
        price_excluding_tax = data['object']['total_excluding_tax'] / 100
        self._account.change_license(account['id'], product_id, price_id, price_excluding_tax)

        # Send email
        email = account['email']
        name = account['name']
        date = datetime.datetime.utcfromtimestamp(data['object']['created'])
        date = f"{date.strftime('%B')} {date.strftime('%d')}, {date.strftime('%Y')}"
        resources = self._account.get_license(account['id'])['resources']
        self._mail.send_payment_success_email(email, price, name, date, resources, invoice_url)

    def invoice_payment_failed(self, data):
        if data['object']['billing_reason'] == 'subscription_cycle':
            # Create entry to the payments table
            subscription_id = data['object']['subscription']
            created_date = data['object']['created']
            price = data['object']['amount_due'] / 100
            status = 'unpaid'
            stripe_id = data['object']['id']
            next_payment_attempt = data['object']['next_payment_attempt']
            invoice_url = data['object']['hosted_invoice_url']
            self._account.new_purchase(subscription_id, created_date, price, status, stripe_id, next_payment_attempt, invoice_url)

            # Send email
            payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data']
            email = data['object']['customer_email']
            card = payment_methods[0]['card']['last4']
            self._mail.send_payment_failed_email(email, price, card, invoice_url, next_payment_attempt)

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
        payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data']
        # Delete old payment methods
        latest_payment = max(payment_methods, key=lambda x: x['created'])['id']
        for i in payment_methods:
            if i['id'] != latest_payment:
                stripe.PaymentMethod.detach(i['id'])
        # Update customer's name and assign the current payment method as a default
        stripe.Customer.modify(data['object']['customer'], name=data['object']['billing_details']['name'], invoice_settings={"default_payment_method":data['object']['id']})
        # Expire mail codes
        account = self._account.get_by_customer(data['object']['customer'])[0]
        self._account.clean_mail(account['id'], 'update_payment')
