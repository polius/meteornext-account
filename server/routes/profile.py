import bcrypt
import stripe
import secrets
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import models.account
import mail.mail

class Profile:
    def __init__(self, sql, conf):
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)
        # Init mail class
        self._mail = mail.mail.Mail(conf)

    def blueprint(self):
        # Init blueprint
        profile_blueprint = Blueprint('profile', __name__, template_folder='profile')

        @profile_blueprint.route('/profile', methods=['POST'])
        @jwt_required()
        def profile_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Get Request Json
            data = request.get_json()

            # Check parameters
            if 'name' not in data or 'email' not in data:
                return jsonify({'message': 'Insufficient parameters'}), 400
            if len(data['name']) > 100:
                return jsonify({'message': 'The name exceeds the maximum length allowed.'}), 400
            if len(data['email']) > 100:
                return jsonify({'message': 'The email exceeds the maximum length allowed.'}), 400

            # Check email
            account2 = self._account.get_by_email(data['email'])
            if len(account2) > 0 and account2[0]['id'] != account['id']:
                return jsonify({'message': 'This email is already registered.'}), 400

            # Check vat number
            company_name = None if data['company_name'].strip() == '' else data['company_name']
            vat_number = None if data['vat_number'].strip() == '' else data['vat_number']
            if not vat_number:
                # Delete previous customer vat number
                tax_ids = stripe.Customer.list_tax_ids(account['stripe_id'])['data']
                for tax_id in tax_ids:
                    stripe.Customer.delete_tax_id(account['stripe_id'], tax_id['id'])
                self._account.remove_vat(account['id'])
                # Update customer to apply taxes
                stripe.Customer.modify(account['stripe_id'], tax_exempt='none')
            elif not (vat_number == account['vat_number'] and account['vat_status'] == 'verified'):
                # Delete previous customer vat number
                tax_ids = stripe.Customer.list_tax_ids(account['stripe_id'])['data']
                for tax_id in tax_ids:
                    stripe.Customer.delete_tax_id(account['stripe_id'], tax_id['id'])
                self._account.remove_vat(account['id'])
                # Update customer to apply taxes
                stripe.Customer.modify(account['stripe_id'], tax_exempt='none')
                # Assign new vat number to customer
                try:
                    stripe.Customer.create_tax_id(account['stripe_id'], type="eu_vat", value=vat_number)
                except Exception as e:
                    return jsonify({'message': 'Invalid EU VAT number.'}), 400
                else:
                    self._account.add_vat(account['id'], vat_number)

            # Change profile
            self._account.change_profile(account['id'], data['name'], company_name)

            # Change Stripe account name
            if data['name'] != account['name']:
                try:
                    stripe.Customer.modify(account['stripe_id'], name=data['name'])
                except Exception:
                    return jsonify({'message': 'An error occurred changing the name. Please try again later.'}), 400

            # Send confirmation mail
            if data['email'] != account['email']:
                try:
                    code = secrets.token_urlsafe(64)
                    self._account.create_mail(account['id'], 'verify_email', code, data['email'])
                    self._mail.send_verify_email(data['email'], code)
                except Exception:
                    return jsonify({'message': 'An error occurred sending the verification mail. Please try again later.'}), 400

            # Send confirmation message
            return jsonify({'message': 'Profile saved.'}), 200

        @profile_blueprint.route('/profile/password', methods=['POST'])
        @jwt_required()
        def profile_password_method():
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
            if len(data['new']) > 100:
                return jsonify({'message': 'The new password exceeds the maximum length allowed.'}), 400

            # Change password
            try:
                self.change_password(account, data['current'], data['new'], data['repeat'])
                return jsonify({'message': 'Password successfully changed'}), 200
            except Exception as e:
                return jsonify({'message': str(e)}), 400

        return profile_blueprint

    ####################
    # Internal Methods #
    ####################
    def change_password(self, account, current, new, repeat):
        # Check current password
        if not bcrypt.checkpw(current.encode('utf-8'), account['password'].encode('utf-8')):
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
