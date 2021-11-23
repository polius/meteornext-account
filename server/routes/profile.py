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

            # Change password
            try:
                self.change_password(account, data['current'], data['new'], data['repeat'])
                return jsonify({'message': 'Password successfully changed'}), 200
            except Exception as e:
                return jsonify({'message': str(e)}), 400

        @profile_blueprint.route('/profile/email', methods=['POST'])
        @jwt_required()
        def profile_email_method():
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

            # Check email
            if account['email'] == data['email']:
                return jsonify({'message': 'The new email can not be the same as the current one'}), 400
            account2 = self._account.get_by_email(data['email'])
            if len(account2) > 0 and account2['id'] != account['id']:
                return jsonify({'message': 'This mail is already registered'}), 400

            # Send confirmation mail
            try:
                code = secrets.token_urlsafe(64)
                self._account.create_mail(account['id'], 'verify_email', code, data['email'])
                self._mail.send_verify_email(data['email'], code)
            except Exception:
                return jsonify({'message': 'An error occurred sending the verification mail'}), 400

            return jsonify({'message': 'Please verify your email address'}), 200

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
