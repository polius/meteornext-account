import bcrypt
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
                pricing = self._account.get_pricing()
                return jsonify({'profile': profile, 'license': license, 'billing': billing, 'pricing': pricing}), 200

            # Delete account
            elif request.method == 'DELETE':
                self._account.delete(get_jwt_identity())
                return jsonify({'message': 'Account successfully deleted.'}), 200

        @account_blueprint.route('/account/license', methods=['GET','POST'])
        @jwt_required()
        def account_license_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            if request.method == 'GET':
                license = self._account.get_license(get_jwt_identity())
                pricing = self._account.get_pricing()
                return jsonify({'license': license, 'pricing': pricing}), 200

            if request.method == 'POST':
                # Check parameters
                data = request.get_json()
                if 'resources' not in data:
                    return jsonify({'message': 'Insufficient parameters'}), 400
                try:
                    if int(data['resources']) not in [1,5,10,25,50,100,200,300,400,500,750,1000,2000,3000,4000,5000,-1]:
                        raise Exception()
                except Exception:
                    return jsonify({'message': 'License value is not valid'}), 400

                # Change license value
                self._account.change_license(get_jwt_identity(), data['resources'])
                return jsonify({'message': 'License successfully changed'}), 200

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

        @account_blueprint.route('/account/change', methods=['POST'])
        @jwt_required()
        def account_change_method():
            # Get account
            account = self._account.get(get_jwt_identity())[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Check parameters
            data = request.get_json()
            if 'resources' not in data:
                return jsonify({'message': 'Insufficient parameters'}), 400
            try:
                if int(data['resources']) not in [1,5,10,25,50,100,200,300,400,500,750,1000,2000,3000,4000,5000,-1]:
                    raise Exception()
            except Exception:
                return jsonify({'message': 'License value is not valid'}), 400

            # Change license value
            self._account.change_license(get_jwt_identity(), data['resources'])
            return jsonify({'message': 'License successfully changed'}), 200

        return account_blueprint

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
            raise Exception('The password must contain a number')
        if not any(c.isnumeric() for c in new):
            raise Exception('The password must contain a number')

        # Change password
        encrypted_passw = bcrypt.hashpw(new.encode('utf8'), bcrypt.gensalt())
        self._account.change_password({'id': get_jwt_identity(), 'password': encrypted_passw})
