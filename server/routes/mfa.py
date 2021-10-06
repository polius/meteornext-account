import pyotp
import bcrypt
import secrets
import webauthn
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
                return jsonify({'message': 'Accouunt Disabled'}), 401

            if request.method == 'GET':
                # Get 2FA challenge
                mfa = self._account.get_mfa(get_jwt_identity())
                return_data = { 'mfa': None, 'created': None }
                if len(mfa) > 0:
                    return_data['mode'] = '2fa' if mfa[0]['2fa_hash'] is not None else 'webauthn' if mfa[0]['webauthn_ukey'] is not None else None
                    return_data['created'] = mfa[0]['created_at']
                return jsonify({'data': return_data}), 200
            elif request.method == 'DELETE':
                # Clean the account MFA
                self._account.disable_mfa(get_jwt_identity())
                return jsonify({'message': 'MFA successfully disabled'}), 200

        @mfa_blueprint.route('/mfa/2fa', methods=['GET','POST'])
        @jwt_required()
        def mfa_2fa_method():
            # Get Account
            account = self._account.get(get_jwt_identity())[0]

            # Check account privileges
            if account['disabled']:
                return jsonify({'message': 'Accouunt Disabled'}), 401

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
                return jsonify({'message': 'Accouunt Disabled'}), 401

            if request.method == 'GET':              
                # Generate webauthn challenge
                return jsonify(self.get_webauthn_register(account))

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
        # Clear session variables prior to starting a new registration
        session.pop('register_ukey', None)
        session.pop('register_username', None)
        session.pop('register_display_name', None)
        session.pop('challenge', None)
        session['register_username'] = account['email']
        session['register_display_name'] = account['email']

        # Generate challenge and store it to the user session
        challenge = self.__generate_challenge(32)
        ukey = self.__generate_ukey()
        rp_id = request.host
        session['challenge'] = challenge.rstrip('=')
        session['register_ukey'] = ukey

        # Make credentials
        make_credential_options = webauthn.WebAuthnMakeCredentialOptions(challenge, 'Meteor Next - Account', rp_id, ukey, account['email'], account['email'], 'https://www.w3.org', attestation='none')
        return make_credential_options.registration_dict

    def post_webauthn_register(self, account, data):
        # Get session data
        challenge = session['challenge']
        username = session['register_username']
        display_name = session['register_display_name']
        ukey = session['register_ukey']
        
        # Build webauthn registration response
        rp_id = request.host
        origin = 'https://' + request.host
        registration_response = data['credential']
        trust_anchor_dir = ''
        trusted_attestation_cert_required = False
        self_attestation_permitted = True
        none_attestation_permitted = True
        webauthn_registration_response = webauthn.WebAuthnRegistrationResponse(
            rp_id,
            origin,
            registration_response,
            challenge,
            trust_anchor_dir,
            trusted_attestation_cert_required,
            self_attestation_permitted,
            none_attestation_permitted,
            uv_required=False
        )
        # Verify webauthn registration response
        webauthn_credential = webauthn_registration_response.verify()

        # Store webauthn credentials
        if 'store' in data and data['store'] is True:
            storage = {
                'account_id': account['id'],
                'webauthn_ukey': ukey,
                'webauthn_pub_key': webauthn_credential.public_key,
                'webauthn_credential_id': webauthn_credential.credential_id,
                'webauthn_sign_count': webauthn_credential.sign_count,
                'webauthn_rp_id': rp_id
            }
            self._account.enable_webauthn(storage)

    def get_webauthn_login(self, account, user_mfa):
        session.pop('challenge', None)
        challenge = self.__generate_challenge(32)
        session['challenge'] = challenge.rstrip('=')
        webauthn_user = webauthn.WebAuthnUser(
            user_mfa['webauthn_ukey'],
            account['email'],
            account['email'],
            'https://www.w3.org',
            user_mfa['webauthn_credential_id'],
            user_mfa['webauthn_pub_key'],
            user_mfa['webauthn_sign_count'],
            user_mfa['webauthn_rp_id']
        )
        webauthn_assertion_options = webauthn.WebAuthnAssertionOptions(webauthn_user, challenge)
        return webauthn_assertion_options.assertion_dict

    def post_webauthn_login(self, account, user_mfa):
        # Get request data
        data = request.get_json()
        # Parse data
        origin = 'https://' + request.host
        challenge = session.get('challenge')
        assertion_response = data['mfa']
        webauthn_user = webauthn.WebAuthnUser(
            user_mfa['webauthn_ukey'],
            account['email'],
            account['email'],
            'https://www.w3.org',
            user_mfa['webauthn_credential_id'],
            user_mfa['webauthn_pub_key'],
            user_mfa['webauthn_sign_count'],
            user_mfa['webauthn_rp_id']
        )
        webauthn_assertion_response = webauthn.WebAuthnAssertionResponse(
            webauthn_user,
            assertion_response,
            challenge,
            origin,
            uv_required=False
        )
        # Verify webauthn login response
        sign_count = webauthn_assertion_response.verify()

        # Update sign_count
        self._account.put_webauthn_sign_count({'webauthn_sign_count': sign_count, 'account_id': account['id']})

    def __generate_challenge(self, challenge_len=32):
        return secrets.token_urlsafe(challenge_len)

    def __generate_ukey(self):
        return self.__generate_challenge(20)

    def check_login(self, data):
        # Get User from Database
        user = self._users.get(data['username'])
        # Check user & password
        if len(user) == 0 or not bcrypt.checkpw(data['password'].encode('utf-8'), user[0]['password'].encode('utf-8')):
            return []
        # Login successfully
        return user
