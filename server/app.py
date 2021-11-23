import json
import secrets
import datetime
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_compress import Compress

from cron import Cron
import connectors
import routes.login
import routes.register
import routes.account
import routes.license
import routes.profile
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
sql = connectors.Pool(conf['sql'])

# Init cron
Cron(app, sql)

# Register blueprints
URL_PREFIX = "/api"
login = routes.login.Login(sql, conf)
register = routes.register.Register(sql, conf)
account = routes.account.Account(sql, conf)
license = routes.license.License(sql, conf)
profile = routes.profile.Profile(sql, conf)
mfa = routes.mfa.MFA(sql)
app.register_blueprint(login.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(register.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(account.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(license.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(profile.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(mfa.blueprint(), url_prefix=URL_PREFIX)

# Enable CORS
CORS(app)

# Run with python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001', debug=False)
