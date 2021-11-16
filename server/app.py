import json
import secrets
import datetime
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_compress import Compress

import connectors
import routes.login
import routes.register
import routes.account
import routes.mfa

# Instantiate Flask App
app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_SORT_KEYS'] = False

# JWT Config
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(nbytes=64)
app.secret_key = app.config['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=12)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
jwt = JWTManager(app)

# Compress Flask application's responses with gzip, deflate or brotli
Compress(app)

# Init SQL Pool
with open('server.conf') as file_open:
    conf = json.load(file_open)
SQL = connectors.Pool(conf['sql'])

# Register blueprints
URL_PREFIX = "/api"
login = routes.login.Login(SQL)
register = routes.register.Register(SQL)
account = routes.account.Account(SQL)
mfa = routes.mfa.MFA(SQL)
app.register_blueprint(login.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(register.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(account.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(mfa.blueprint(), url_prefix=URL_PREFIX)

# Enable CORS
CORS(app)

# Run with python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001', debug=False)
