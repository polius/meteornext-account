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

        @billing_bluepring.route('/billing/method', methods=['POST'])
        @jwt_required()
        def billing_method_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Create checkout
            try:
                checkout_session = stripe.checkout.Session.create(
                    mode='setup',
                    payment_method_types=['card'],
                    customer=account['stripe_id'],
                    success_url='https://account.meteor2.io/billing',
                    cancel_url='https://account.meteor2.io/billing',
                )
                return jsonify({'url': checkout_session.url}), 200
            except Exception as e:
                return jsonify({'message': str(e)}), 400

            @billing_bluepring.route('/billing/invoice', methods=['GET'])
            @jwt_required()
            def billing_invoice_method():
                pass

        return billing_bluepring
