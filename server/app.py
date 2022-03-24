import os
import json
import uuid
import hashlib
import datetime
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_compress import Compress

# Build config
current_dir = os.path.dirname(os.path.realpath(__file__))
if os.path.isfile(f"{current_dir}/server.conf"):
    with open(f"{current_dir}/server.conf") as fopen:
        conf = json.load(fopen)
else:
    conf = {
        "sql": {
            "engine": os.getenv('SQL_ENGINE'),
            "hostname": os.getenv('SQL_HOSTNAME'),
            "port": os.getenv('SQL_PORT'),
            "username": os.getenv('SQL_USERNAME'),
            "password": os.getenv('SQL_PASSWORD'),
            "database": os.getenv('SQL_DATABASE')
        },
        "aws": {
            "region_name": os.getenv('AWS_REGION'),
            "access_key": os.getenv('AWS_ACCESS_KEY'),
            "secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY')
        },
        "stripe": {
            "api_key": os.getenv('STRIPE_API_KEY'),
            "webhook_secret": os.getenv('STRIPE_WEBHOOK_SECRET')
        },
        "hcaptcha": {
            "secret": os.getenv('HCAPTCHA_SECRET')
        },
        "sentry": {
            "dsn": os.getenv('SENTRY_DSN'),
            "environment": os.getenv('SENTRY_ENV')
        },
        "jwt": {
            "secret_key": os.getenv('JWT_SECRET_KEY')
        }
    }

# Instantiate Flask App
app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_SORT_KEYS'] = False

# JWT Config
app.config['JWT_SECRET_KEY'] = conf['jwt']['secret_key'] if os.getenv('JWT_SECRET_KEY') else hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()
app.secret_key = app.config['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=12)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
jwt = JWTManager(app)

# Compress Flask application's responses with gzip, deflate or brotli
Compress(app)

# Init Sentry
sentry_sdk.init(dsn=conf['sentry']['dsn'], environment=conf['sentry']['environment'], traces_sample_rate=0, integrations=[FlaskIntegration()])

# Init app routes
from cron import Cron
import connectors
import routes.login
import routes.register
import routes.account
import routes.license
import routes.billing
import routes.profile
import routes.stripe
import routes.mfa
import routes.health

# Init SQL Pool
sql = connectors.Pool(conf['sql'])

# Init cron
Cron(app, sql)

# Register blueprints
URL_PREFIX = "/api"
login = routes.login.Login(sql)
register = routes.register.Register(sql, conf)
account = routes.account.Account(sql, conf)
license = routes.license.License(sql, conf)
billing = routes.billing.Billing(sql, conf)
profile = routes.profile.Profile(sql, conf)
stripe = routes.stripe.Stripe(sql, conf)
mfa = routes.mfa.MFA(sql)
health = routes.health.Health(sql)
app.register_blueprint(login.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(register.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(account.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(license.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(billing.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(profile.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(stripe.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(mfa.blueprint(), url_prefix=URL_PREFIX)
app.register_blueprint(health.blueprint(), url_prefix=URL_PREFIX)

# Enable CORS
CORS(app)

# Run with python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001', debug=False)
