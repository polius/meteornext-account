import bcrypt
import stripe
import secrets
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
                billing = self._account.get_billing(get_jwt_identity())
                products = self._account.get_products()
                return jsonify({'profile': profile, 'license': license, 'billing': billing, 'products': products}), 200

            # Delete account
            elif request.method == 'DELETE':
                # Delete data from stripe
                if account['stripe_id']:
                    stripe.Customer.delete(account['stripe_id'])
                # Delete account from database
                self._account.delete(get_jwt_identity())
                return jsonify({'message': 'Account successfully deleted'}), 200

        @account_blueprint.route('/account/password', methods=['PUT'])
        @jwt_required()
        def account_password_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Get Request Json
            data = request.get_json()

            # Check parameters
            if 'current' not in data or 'new' not in data or 'repeat' not in data:
                return jsonify({'message': 'Insufficient parameters'}), 400

            # Change password
            try:
                self.change_password(account, data['new'], data['repeat'], data['current'])
                return jsonify({'message': 'Password successfully changed'}), 200
            except Exception as e:
                return jsonify({'message': str(e)}), 400

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
                    # Generate email code
                    code = secrets.token_urlsafe(64)
                    # Create an entry to the "mail" table
                    self._account.reset_password(data['email'], code)
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
                        account = {'id': mail[0]['account_id']}
                        self.change_password(account, data['password'], data['password2'])
                    except Exception as e:
                        return jsonify({'message': str(e)}), 400

                    # Remove entry from 'mail'
                    self._account.clean_mail(mail[0]['account_id'], 'reset_password')
                    return jsonify({'message': 'Password updated'}), 200

        @account_blueprint.route('/account/email', methods=['PUT'])
        @jwt_required()
        def account_email_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Get Request Json
            data = request.get_json()

            # Check parameters
            if 'email' not in data:
                return jsonify({'message': 'Insufficient parameters'}), 400

            # Change email
            self._account.change_email(account, data['email'])
            return jsonify({'message': 'Email successfully changed'}), 200

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

            # Verify email
            self._account.clean_mail(mail[0]['account_id'], 'verify_email')

            # Create stripe customer
            account = self._account.get(mail[0]['account_id'])[0]
            customer = stripe.Customer.create(email=account['email'])
            data = {'account_id': mail[0]['account_id'], 'stripe_id': customer['id']}
            self._account.put_customer(data)

            # Return response
            return jsonify({'message': 'Email verified'}), 200

        @account_blueprint.route('/account/unregister', methods=['POST'])
        @jwt_required()
        def account_unregister_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Unregister license
            self._account.unregister_license(get_jwt_identity())
            return jsonify({'message': 'License successfully unregistered'}), 200

        return account_blueprint

    ####################
    # Internal Methods #
    ####################
    def change_password(self, account, new, repeat, current=None):
        # Check current password
        if current and not bcrypt.checkpw(current.encode('utf-8'), account['password'].encode('utf-8')):
            raise Exception("The current password is not valid.")

        # Check password requirements
        if new != repeat:
            raise Exception('Passwords do not match')
        if current == new:
            raise Exception("The new password can't be the same as the current")
        if len(new) < 8:
            raise Exception('The password must be at least 8 characters long')
        if not any(c.islower() for c in new):
            raise Exception('The password must contain a letter')
        if not any(c.isnumeric() for c in new):
            raise Exception('The password must contain a number')

        # Change password
        encrypted_passw = bcrypt.hashpw(new.encode('utf8'), bcrypt.gensalt())
        self._account.change_password({'id': account['id'], 'password': encrypted_passw})
