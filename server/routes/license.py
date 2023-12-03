import stripe
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import models.account

class License:
    def __init__(self, sql, conf):
        self._conf = conf
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)

    def blueprint(self):
        # Init blueprint
        license_blueprint = Blueprint('license', __name__, template_folder='license')

        @license_blueprint.route('/license', methods=['GET','POST'])
        @jwt_required()
        def license_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            if request.method == 'GET':
                license = self._account.get_license(get_jwt_identity())
                return jsonify({'license': license}), 200

            if request.method == 'POST':
                # Check parameters
                data = request.get_json()
                if 'resources' not in data:
                    return jsonify({'message': 'Insufficient parameters'}), 400
                if int(data['resources']) < 1 or int(data['resources']) > 500 or int(data['resources']) in [2,3,4]:
                    return jsonify({'message': 'Enter a valid number of servers (5 - 500).'}), 400

                # Get new product
                product = self._account.get_product_by_resources(resources=data['resources'])

                if data['resources'] == 1:
                    # Remove current subscription
                    subscriptions = stripe.Subscription.list(customer=account['stripe_id'])
                    for subscription in subscriptions['data']:
                        # Expire last invoice
                        invoice = stripe.Invoice.retrieve(subscription['latest_invoice'])
                        if invoice['status'] == 'open':
                            stripe.Invoice.void_invoice(subscription['latest_invoice'])
                            self._account.expire_invoice(subscription['latest_invoice'])
                        # Remove subscription
                        stripe.Subscription.delete(subscription['id'])
                        self._account.remove_subscription(subscription['id'])
                        # Downgrade license
                        self._account.downgrade_license(subscription['id'])
                    return jsonify({'url': "https://account.meteornext.io/license/change/success"}), 200
                else:
                    # Create checkout
                    checkout_session = stripe.checkout.Session.create(
                        line_items=[
                            {
                                'price': product['price_stripe_id'],
                                'quantity': 1,
                            }
                        ],
                        mode='subscription',
                        customer=account['stripe_id'],
                        customer_update={'address': 'auto'},
                        success_url='https://account.meteornext.io/license/change/success',
                        cancel_url='https://account.meteornext.io/license',
                        allow_promotion_codes=True,
                        automatic_tax={'enabled': True}
                    )
                    return jsonify({'url': checkout_session.url}), 200

        @license_blueprint.route('/license/unregister', methods=['POST'])
        @jwt_required()
        def license_unregister_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Check unregistered date
            license = self._account.get_license(get_jwt_identity())
            if license['unregistered_date'] is not None:
                diff = datetime.utcnow() - license['unregistered_date']
                if diff.seconds < 3600:
                    mod = divmod(3600 - diff.seconds, 60) 
                    return jsonify({'message': f"This license has already been unregistered in the last hour. Wait {mod[0]} minutes and {mod[1]} seconds before unregistering again."}), 400

            # Unregister license
            self._account.unregister_license(get_jwt_identity())
            return jsonify({'message': 'License successfully unregistered'}), 200

        return license_blueprint
