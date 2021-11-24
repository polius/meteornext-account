import stripe
from flask import Blueprint, jsonify, request

import models.account

class Stripe:
    def __init__(self, sql, conf):
        self._conf = conf
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)

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

            if event['type'] == 'invoice.paid':
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
    def invoice_paid(self, data):
        # Get common information
        account = self._account.get_by_email(data['object']['customer_email'])[0]
        account_id = account['id']
        product_id = self._account.get_products_by_stripe(data['object']['lines']['data'][0]['plan']['id'])[0]['id']

        # Remove last subscriptions
        subscriptions = stripe.Subscription.list(customer=account['stripe_id'])
        for subscription in subscriptions['data'][1:]:
            stripe.Subscription.delete(subscription['id'])

        # Update licence entry
        self._account.change_license(account_id, product_id)

        # Create entry to the payments table
        created = data['object']['created'],
        price = data['object']['amount_paid']
        status = 'success'
        error = None
        stripe_id = data['object']['payment_intent']
        invoice = data['object']['invoice_pdf']
        self._account.new_purchase(account_id,  product_id, created, price, status, error, stripe_id, invoice)

    def invoice_payment_failed(self, data):
        print(data)
        # check if it happened creating a subscription or is an automated payment.
        # automated payment --> send email.
        # "billing_reason": "subscription_create"

    def customer_source_expiring(self, data):
        print(data)
        # send notification mail.

    def payment_method_attached(self, data):
        # Get all customer payment methods
        payment_methods = stripe.PaymentMethod.list(customer=data['object']['customer'], type="card")['data'][1:]
        # Delete old payment methods
        for i in payment_methods:
            stripe.PaymentMethod.detach(i['id'])
        # Update customer's name to the current payment name
        stripe.Customer.modify(data['object']['customer'], name=data['object']['billing_details']['name'])
