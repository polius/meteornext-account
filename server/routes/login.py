import pyotp
import bcrypt
from flask import request, jsonify, Blueprint
from flask_jwt_extended import (create_access_token, set_access_cookies, unset_access_cookies)

import models.account
import routes.mfa

class Login:
    def __init__(self, sql):
        # Init models
        self._account = models.account.Account(sql)
        # Init routes
        self._mfa = routes.mfa.MFA(sql)

    def blueprint(self):
        # Init blueprint
        login_blueprint = Blueprint('login', __name__, template_folder='login')

        @login_blueprint.route('/login', methods=['POST'])
        def login_method():
            # Check parameters
            if not request.is_json:
                return jsonify({"message": "Missing JSON in request"}), 400
            login_json = request.get_json()

            # Get account
            account = self._account.get_by_email(login_json['email'])

            # Check email & password
            if len(account) == 0 or not bcrypt.checkpw(login_json['password'].encode('utf-8'), account[0]['password'].encode('utf-8')):
                return jsonify({"message": "Invalid credentials"}), 401
            account = account[0]

            # Check disabled
            if account['disabled']:
                return jsonify({"message": "Account disabled"}), 401

            # Check verified
            if not account['verified'] and not account['stripe_id']:
                return jsonify({"message": "Please verify your email address"}), 400

            # Check MFA
            if account['mfa']:
                account_mfa = self._account.get_mfa(account['id'])[0]
                if account['mfa'] == '2fa' and len(account_mfa) > 0:
                    if 'mfa' not in login_json:
                        return jsonify({"code": "2fa", "message": "Requesting 2FA credentials"}), 202
                    elif not pyotp.TOTP(account_mfa['2fa_hash'], interval=30).verify(login_json['mfa'], valid_window=1):
                        return jsonify({"message": "Invalid MFA Code"}), 400
                elif account['mfa'] == 'webauthn':
                    try:
                        if 'mfa' not in login_json:
                            return jsonify({"code": "webauthn", "data": self._mfa.get_webauthn_login(account_mfa), "message": "Requesting Webauthn credentials"}), 202
                        else:
                            self._mfa.post_webauthn_login(account, account_mfa)
                    except Exception as e:
                        return jsonify({'message': str(e)}), 400

            # Generate access tokens
            access_token = create_access_token(identity=account['id'])

            # Update user data
            ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
            self._account.login({"id": account['id'], "ip": ip})

            # Build return data
            resp = jsonify({'data': { 'email': account['email'] }})
            set_access_cookies(resp, access_token, 12*60*60)
            return resp, 200

        @login_blueprint.route('/logout', methods=['POST'])
        def logout_method():
            resp = jsonify({'message': 'Bye'})
            unset_access_cookies(resp)
            return resp

        return login_blueprint
