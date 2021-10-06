import json
import bcrypt
import string
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import models.account

class Account:
    def __init__(self, sql):
        self._license = license
        # Init models
        self._account = models.account.Account(sql)

    def blueprint(self):
        # Init blueprint
        account_blueprint = Blueprint('account', __name__, template_folder='profile')

        @account_blueprint.route('/account', methods=['GET'])
        @jwt_required()
        def account_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Get data
            profile = self._account.get_profile(get_jwt_identity())[0]
            license = self._account.get_license(get_jwt_identity())
            billing = self._account.get_billing(get_jwt_identity())
            return jsonify({'profile': profile, 'license': license, 'billing': billing}), 200

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
                self.change_password(account, data['current'], data['new'], data['repeat'])
                return jsonify({'message': 'Password successfully changed'}), 200
            except Exception as e:
                return jsonify({'message': str(e)}), 400

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

        @account_blueprint.route('/account', methods=['DELETE'])
        @jwt_required()
        def account_delete_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Delete account
            self._account.delete(get_jwt_identity())
            return jsonify({'message': 'Account successfully deleted.'}), 200

        return account_blueprint

    ####################
    # Internal Methods #
    ####################
    def change_password(self, account, current, new, repeat):
        # Check current password
        if not bcrypt.checkpw(current.encode('utf-8'), account['password'].encode('utf-8')):
            raise Exception("The current password is not valid.")

        # Check repeat password
        if new != repeat:
            raise Exception("The new password does not match")

        # Check Password Policy
        if len(new) < 8:
            raise Exception(f"The password must be at least 8 characters long.")

        # Change password
        encrypted_passw = bcrypt.hashpw(new.encode('utf8'), bcrypt.gensalt())
        self._account.change_password({'id': get_jwt_identity(), 'password': encrypted_passw})
        return encrypted_passw
