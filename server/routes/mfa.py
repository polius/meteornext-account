import json
import pyotp
import bcrypt
import secrets
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
)
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    RegistrationCredential,
    UserVerificationRequirement,
    AuthenticationCredential,
)
from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import (jwt_required, get_jwt_identity)

import models.account

class MFA:
    def __init__(self, sql):
        self._account = models.account.Account(sql)

    def blueprint(self):
        # Init blueprint
        mfa_blueprint = Blueprint('mfa', __name__, template_folder='mfa')

        @mfa_blueprint.route('/mfa', methods=['GET','DELETE'])
        @jwt_required()
        def mfa_method():
            # Get Account
            account = self._account.get(get_jwt_identity())[0]

            # Check account privileges
            if account['disabled']:
                return jsonify({'message': 'Account Disabled'}), 401

            if request.method == 'GET':
                # Get 2FA challenge
                mfa = self._account.get_mfa(get_jwt_identity())
                return_data = { 'mode': None, 'created': None }
                if len(mfa) > 0:
                    return_data['mode'] = '2fa' if mfa[0]['2fa_hash'] is not None else 'webauthn' if mfa[0]['webauthn_pub_key'] is not None else None
                    return_data['created'] = mfa[0]['created']
                return jsonify({'data': return_data}), 200
            elif request.method == 'DELETE':
                # Clean the account MFA
                self._account.disable_mfa(get_jwt_identity())
                return jsonify({'message': 'MFA successfully disabled'}), 200

        @mfa_blueprint.route('/2fa', methods=['GET','POST'])
        @jwt_required()
        def mfa_2fa_method():
            # Get Account
            account = self._account.get(get_jwt_identity())[0]

            # Check account privileges
            if account['disabled']:
                return jsonify({'message': 'Account Disabled'}), 401

            if request.method == 'GET':
                # Get 2FA hash
                mfa_hash = pyotp.random_base32()
                mfa_uri = pyotp.TOTP(mfa_hash, interval=30).provisioning_uri(account['email'], issuer_name="Meteor Next - Account")
                return jsonify({"mfa_hash": mfa_hash, "mfa_uri": mfa_uri}), 200

            elif request.method == 'POST':
                data = request.get_json()
                # Store 2FA
                mfa = pyotp.TOTP(data['hash'], interval=30)
                if 'value' not in data or len(data['value']) == 0 or not mfa.verify(data['value'], valid_window=1):
                    return jsonify({'message': 'Invalid MFA Code'}), 400
                self._account.enable_2fa({'account_id': get_jwt_identity(), '2fa_hash': data['hash']})
                return jsonify({'message': 'MFA successfully enabled'}), 200

        @mfa_blueprint.route('/mfa/webauthn/register', methods=['GET','POST'])
        @jwt_required()
        def mfa_webauthn_register_method():
            # Get request data
            data = request.args if request.method == 'GET' else request.get_json()

            # Get Account
            account = self._account.get(get_jwt_identity())[0]

            # Check account privileges
            if account['disabled']:
                return jsonify({'message': 'Account Disabled'}), 401

            if request.method == 'GET':              
                # Generate webauthn challenge
                return self.get_webauthn_register(account)

            elif request.method == 'POST':
                # Validate challenge & Register webauthn credential
                try:
                    self.post_webauthn_register(account, data)
                    if 'store' in data and data['store']:
                        return jsonify({'message': 'MFA successfully enabled'}), 200
                    return jsonify({"message": 'Credentials validated'}), 200
                except Exception as e:
                    return jsonify({'message': str(e)}), 400

        return mfa_blueprint
        
    ####################
    # Internal Methods #
    ####################
    def get_webauthn_register(self, account):
        # Generate challenge and store it to the user session
        session['challenge'] = self.__generate_challenge()

        # Generate registration options
        registration_options = generate_registration_options(
            rp_id=request.host,
            rp_name="Meteor Next - Account",
            user_id=account['email'],
            user_name=account['email'],
            user_display_name=account['email'],
            challenge=session['challenge'],
        )
        return options_to_json(registration_options)

    def post_webauthn_register(self, account, data):
        # Registration Response Verification
        registration_verification = verify_registration_response(
            credential=RegistrationCredential.parse_raw(json.dumps(data['credential'])),
            expected_challenge=session['challenge'],
            expected_origin='https://' + request.host,
            expected_rp_id=request.host,
            require_user_verification=False,
        )

        # Store webauthn credentials
        if 'store' in data and data['store'] is True:
            storage = {
                'account_id': account['id'],
                'webauthn_pub_key': bytes_to_base64url(registration_verification.credential_public_key),
                'webauthn_credential_id': data['credential']['id'],
                'webauthn_sign_count': 0,
                'webauthn_rp_id': request.host
            }
            self._account.enable_webauthn(storage)

    def get_webauthn_login(self, user_mfa):
        # Generate a new challenge
        session['challenge'] = self.__generate_challenge()

        # Generate authentification options
        authentication_options = generate_authentication_options(
            rp_id=request.host,
            challenge=session['challenge'],
            allow_credentials=[PublicKeyCredentialDescriptor(id=base64url_to_bytes(user_mfa['webauthn_credential_id']))],
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        return options_to_json(authentication_options)

    def post_webauthn_login(self, account, user_mfa):
        # Get request data
        data = request.get_json()

        # Authentication Response Verification
        authentication_verification = verify_authentication_response(
            credential=AuthenticationCredential.parse_raw(json.dumps(data['mfa'])),
            expected_challenge=session['challenge'],
            expected_rp_id=request.host,
            expected_origin='https://' + request.host,
            credential_public_key=base64url_to_bytes(user_mfa['webauthn_pub_key']),
            credential_current_sign_count=user_mfa['webauthn_sign_count'],
            require_user_verification=False,
        )

        # Update sign_count
        self._account.put_webauthn_sign_count({'webauthn_sign_count': authentication_verification.new_sign_count, 'account_id': account['id']})

    def __generate_challenge(self, length=64):
        return secrets.token_bytes(length)

    def check_login(self, data):
        # Get User from Database
        user = self._users.get(data['username'])
        # Check user & password
        if len(user) == 0 or not bcrypt.checkpw(data['password'].encode('utf-8'), user[0]['password'].encode('utf-8')):
            return []
        # Login successfully
        return user
