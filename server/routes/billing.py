import stripe
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import models.account

class Billing:
    def __init__(self, sql, conf):
        self._conf = conf
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)

    def blueprint(self):
        # Init blueprint
        billing_bluepring = Blueprint('billing', __name__, template_folder='billing')

        @billing_bluepring.route('/billing/method', methods=['POST','DELETE'])
        @jwt_required()
        def billing_method_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            if request.method == 'POST':
                # Create checkout
                try:
                    checkout_session = stripe.checkout.Session.create(
                        mode='setup',
                        payment_method_types=['card'],
                        customer=account['stripe_id'],
                        success_url='https://account.meteornext.io/billing',
                        cancel_url='https://account.meteornext.io/billing',
                    )
                    return jsonify({'url': checkout_session.url}), 200
                except Exception as e:
                    return jsonify({'message': str(e)}), 400

            elif request.method == 'DELETE':
                # Get customer subscription
                subscription = stripe.Subscription.list(customer=account['stripe_id'])['data']
                if len(subscription) > 0:
                    return jsonify({'message': "The current payment method is already being used in a subscription. First change your license to 1 server."}), 400
                else:
                    payment_methods = stripe.Customer.list_payment_methods(account['stripe_id'], type="card")
                    for method in payment_methods: 
                        stripe.PaymentMethod.detach(method['id'])
                    return jsonify({'message': "Payment method removed"}), 200

            @billing_bluepring.route('/billing/invoice', methods=['GET'])
            @jwt_required()
            def billing_invoice_method():
                pass

        return billing_bluepring
