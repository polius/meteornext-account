import bcrypt
import stripe
import secrets
import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import models.account
import mail.mail

class Account:
    def __init__(self, sql, conf):
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)
        # Init mail class
        self._mail = mail.mail.Mail(conf)

    def blueprint(self):
        # Init blueprint
        account_blueprint = Blueprint('account', __name__, template_folder='account')

        @account_blueprint.route('/account', methods=['GET','DELETE'])
        @jwt_required()
        def account_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Get account
            if request.method == 'GET':
                profile = self._account.get_profile(get_jwt_identity())[0]
                license = self._account.get_license(get_jwt_identity())
                billing = {
                    "details": {},
                    "payments": self._account.get_payments(get_jwt_identity())
                }

                # Get billing card details
                payment_methods = stripe.Customer.list_payment_methods(account['stripe_id'], type="card")['data']
                if len(payment_methods) > 0:
                    billing['details'] = {
                        'card': payment_methods[0]['card']['brand'].upper(),
                        'last4': payment_methods[0]['card']['last4'],
                        'expiration': f"{payment_methods[0]['card']['exp_month']}/{payment_methods[0]['card']['exp_year']}",
                    }
                    try:
                        upcoming_invoice = stripe.Invoice.upcoming(customer=account['stripe_id'])
                        license['next'] = datetime.datetime.fromtimestamp(upcoming_invoice['lines']['data'][0]['period']['start'])
                    except stripe.error.InvalidRequestError:
                        pass

                # Return data
                return jsonify({'profile': profile, 'license': license, 'billing': billing}), 200

            # Delete account
            elif request.method == 'DELETE':
                # Delete data from stripe
                if account['stripe_id']:
                    stripe.Customer.delete(account['stripe_id'])
                # Delete account from database
                self._account.delete(get_jwt_identity())
                return jsonify({'message': 'Account successfully deleted'}), 200

        @account_blueprint.route('/account/password/reset', methods=['GET','POST'])
        def account_password_reset_method():
            if request.method == 'GET':
                # Get data
                data = request.args

                # Check parameters
                if 'code' not in data:
                    return jsonify({"message": "Invalid parameters"}), 400

                # Get mail data
                mail = self._account.get_mail('reset_password', data['code'])
                
                # Check if code exists
                if len(mail) == 0:
                    return jsonify({'message': 'This code is not valid'}), 400

                # Return data
                return jsonify({'message': 'Success'}), 200

            elif request.method == 'POST':
                # Check parameters
                if not request.is_json:
                    return jsonify({"message": "Missing JSON in request"}), 400

                # Get data
                data = request.get_json()

                # Check parameters
                if 'code' not in data and 'email' not in data:
                    return jsonify({"message": "Invalid parameters"}), 400

                if 'email' in data:
                    # Get account
                    account = self._account.get_by_email(data['email'])
                    if len(account) == 0:
                        return jsonify({'message': 'Email sent'}), 200
                    # Generate email code
                    code = secrets.token_urlsafe(64)
                    # Create an entry to the "mail" table
                    self._account.create_mail(account[0]['id'], 'reset_password', code)
                    # Send email to reset password
                    try:
                        self._mail.send_reset_password(data['email'], code)
                        return jsonify({'message': 'Email sent'}), 200
                    except Exception:
                        return jsonify({'message': 'An error occurred sending the verification mail'}), 400

                elif 'code' in data:
                    # Check parameters
                    if 'password' not in data or 'password2' not in data:
                        return jsonify({"message": "Invalid parameters"}), 400

                    # Get mail data
                    mail = self._account.get_mail('reset_password', data['code'])
                    
                    # Check if code exists
                    if len(mail) == 0:
                        return jsonify({'message': 'This code is not valid'}), 400

                    # Change password
                    try:
                        self.change_password(mail[0]['account_id'], data['password'], data['password2'])
                    except Exception as e:
                        return jsonify({'message': str(e)}), 400

                    # Remove entry from 'mail'
                    self._account.clean_mail(mail[0]['account_id'], 'reset_password')
                    return jsonify({'message': 'Password updated'}), 200

        @account_blueprint.route('/account/email/verify', methods=['POST'])
        def account_email_verify_method():
            # Check parameters
            if not request.is_json:
                return jsonify({"message": "Missing JSON in request"}), 400
            data = request.get_json()
            if 'code' not in data:
                return jsonify({"message": "Invalid parameters"}), 400

            # Get mail data
            mail = self._account.get_mail('verify_email', data['code'])
            
            # Check if code exists
            if len(mail) == 0:
                return jsonify({'message': 'This code is not valid'}), 400

            # Get account
            account = self._account.get(mail[0]['account_id'])[0]
            
            # Check if account was already verified and user is performing a change email.
            if account['stripe_id']:
                # Change stripe customer email
                stripe.Customer.modify(account['stripe_id'], email=mail[0]['data'])
                # Change email
                self._account.change_email(account['id'], mail[0]['data'])
            else:
                # Create stripe customer
                account = self._account.get(mail[0]['account_id'])[0]
                customer = stripe.Customer.create(email=account['email'])
                data = {'account_id': mail[0]['account_id'], 'stripe_id': customer['id']}
                self._account.put_customer(data)

            # Expire mail code
            self._account.clean_mail(mail[0]['account_id'], 'verify_email')

            # Return response
            return jsonify({'message': 'Email verified'}), 200

        @account_blueprint.route('/account/billing/update', methods=['POST'])
        def account_billing_update_method():
            # Check parameters
            if not request.is_json:
                return jsonify({"message": "Missing JSON in request"}), 400
            data = request.get_json()
            if 'code' not in data:
                return jsonify({"message": "Invalid parameters"}), 400

            # Get mail data
            mail = self._account.get_mail('update_payment', data['code'])

            # Check if code exists
            if len(mail) == 0:
                return jsonify({'message': 'This link has expired'}), 400

            # Get account
            account = self._account.get(mail[0]['account_id'])[0]
            
            # Create checkout
            try:
                checkout_session = stripe.checkout.Session.create(
                    mode='setup',
                    payment_method_types=['card'],
                    customer=account['stripe_id'],
                    success_url='https://account.meteornext.io/update/ok',
                    cancel_url='https://account.meteornext.io/billing',
                )
                return jsonify({'url': checkout_session.url}), 200
            except Exception as e:
                return jsonify({'message': str(e)}), 400

        @account_blueprint.route('/account/email/resend', methods=['POST'])
        def account_email_resend_method():
            # Check parameters
            if not request.is_json:
                return jsonify({"message": "Missing JSON in request"}), 400
            data = request.get_json()

            # Get account
            account = self._account.get_by_email(data['email'])[0]

            # Resend email
            code = secrets.token_urlsafe(64)
            self._account.create_mail(account['id'], 'verify_email', code, data['email'])
            self._mail.send_verify_email(data['email'], code)

            # Return response
            return jsonify({'message': 'Please verify your email address'}), 200

        return account_blueprint

    ####################
    # Internal Methods #
    ####################
    def change_password(self, account_id, new, repeat):
        # Check password requirements
        if new != repeat:
            raise Exception('Passwords do not match')
        if len(new) < 8:
            raise Exception('The password must be at least 8 characters long')
        if not any(c.islower() for c in new):
            raise Exception('The password must contain a letter')
        if not any(c.isnumeric() for c in new):
            raise Exception('The password must contain a number')

        # Change password
        encrypted_passw = bcrypt.hashpw(new.encode('utf8'), bcrypt.gensalt())
        self._account.change_password({'id': account_id, 'password': encrypted_passw})
