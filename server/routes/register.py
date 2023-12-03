import json
import uuid
import bcrypt
import secrets
import stripe
import requests
from flask import request, jsonify, Blueprint

import models.account
import mail.mail

class Register:
    def __init__(self, sql, conf):
        self._conf = conf
        # Init stripe apikey
        stripe.api_key = conf['stripe']['api_key']
        # Init models
        self._account = models.account.Account(sql)
        # Init mail class
        self._mail = mail.mail.Mail(conf)

    def blueprint(self):
        # Init blueprint
        register_blueprint = Blueprint('register', __name__, template_folder='register')

        @register_blueprint.route('/register', methods=['POST'])
        def register_method():
            # return jsonify({"message": "Registrations are not yet available."}), 400
            # Check parameters
            if not request.is_json:
                return jsonify({"message": "Missing JSON in request"}), 400
            data = request.get_json()
            if 'email' not in data or 'password' not in data or 'password2' not in data or 'captcha' not in data:
                return jsonify({"message": "Invalid parameters"}), 400
            if len(data['name']) > 100:
                return jsonify({'message': 'The name exceeds the maximum length allowed.'}), 400
            if len(data['email']) > 100:
                return jsonify({'message': 'The email exceeds the maximum length allowed.'}), 400
            if len(data['password']) > 100:
                return jsonify({'message': 'The password exceeds the maximum length allowed.'}), 400

            # Check password requirements
            if data['password'] != data['password2']:
                return jsonify({'message': 'Passwords do not match'}), 400
            if len(data['password']) < 8:
                return jsonify({'message': 'The password must be at least 8 characters long'}), 400
            if not any(c.islower() for c in data['password']):
                return jsonify({'message': 'The password must contain a letter'}), 400
            if not any(c.isnumeric() for c in data['password']):
                return jsonify({'message': 'The password must contain a number'}), 400

            # Validate hcaptcha
            payload = { 'secret': self._conf['hcaptcha']['secret'], 'response': data['captcha'] }
            response = requests.post('https://hcaptcha.com/siteverify', data=payload)
            if response.status_code != 200:
                return jsonify({'message': 'An error occurred validating the captcha'}), 400
            if not json.loads(response.content)['success']:
                return jsonify({'message': 'The captcha is not valid'}), 400

            # Get account
            account = self._account.get_by_email(data['email'])

            # Check account
            if len(account) > 0:
                return jsonify({'message': 'This email is already registered. Try with another one.'}), 400

            # Hash password
            data['password'] = bcrypt.hashpw(data['password'].encode('utf8'), bcrypt.gensalt())

            # Generate license access_key & secret_key
            data['access_key'] = str(uuid.uuid4())
            data['secret_key'] = secrets.token_urlsafe(32)

            # Generate email code
            data['code'] = secrets.token_urlsafe(64)

            # Get IP
            data['ip'] = request.headers.getlist("X-Forwarded-For")[0].split(',')[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr

            # Register account
            self._account.register(data)

            # Send confirmation mail
            try:
                self._mail.send_verify_email(data['email'], data['code'])
            except Exception:
                return jsonify({'message': 'An error occurred sending the verification mail. Please try again later.'}), 400

            return jsonify({'message': 'Account successfully created'}), 200

        return register_blueprint
