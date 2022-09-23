import os
from datetime import datetime
from boto3.session import Session
from sentry_sdk import capture_exception, flush

class Mail:
    def __init__(self, conf):
        # Init ses client
        session = Session(aws_access_key_id=conf['aws']['access_key'], aws_secret_access_key=conf['aws']['secret_access_key'])
        self._ses = session.client(service_name="ses", region_name=conf['aws']['region_name'])

    def send_verify_email(self, email, code):
        try:
            # Get email template
            with open(os.path.dirname(__file__) + "/verify_email.html", "r") as fopen:
                HTML_EMAIL_CONTENT = fopen.read().replace('{CODE}', code)
            # Send mail
            request = self._ses.send_email(
                Source="Meteor Next <no-reply@meteornext.io>",
                Destination={
                    "ToAddresses": [ email ],
                },
                Message={
                    "Subject": {
                        "Data": "Verify email address",
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Html": {
                            "Data": HTML_EMAIL_CONTENT,
                            "Charset": "UTF-8",
                        }
                    },
                },
            )
            if request['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception()

        except Exception as e:
            capture_exception(e)
            flush()
            raise

    def send_reset_password(self, email, code):
        try:
            # Get email template
            with open(os.path.dirname(__file__) + "/reset_password.html", "r") as fopen:
                HTML_EMAIL_CONTENT = fopen.read().replace('{CODE}', code)
            # Send mail
            request = self._ses.send_email(
                Source="Meteor Next <no-reply@meteornext.io>",
                Destination={
                    "ToAddresses": [ email ],
                },
                Message={
                    "Subject": {
                        "Data": "Reset password",
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Html": {
                            "Data": HTML_EMAIL_CONTENT,
                            "Charset": "UTF-8",
                        }
                    },
                },
            )
            if request['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception()

        except Exception as e:
            capture_exception(e)
            flush()
            raise

    def send_payment_success_email(self, email, price, name, date, resources, invoice_url):
        # Get email template
        with open(os.path.dirname(__file__) + "/payment_success.html", "r") as fopen:
            HTML_EMAIL_CONTENT = fopen.read()
        # Add parameters
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{PRICE}', str(price))
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{NAME}', name)
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{DATE}', date)
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{RESOURCES}', str(resources))
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{INVOICE_URL}', invoice_url)
        # Send mail
        request = self._ses.send_email(
            Source="Meteor Next <no-reply@meteornext.io>",
            Destination={
                "ToAddresses": [ email ],
            },
            Message={
                "Subject": {
                    "Data": "Your Meteor Next invoice",
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Html": {
                        "Data": HTML_EMAIL_CONTENT,
                        "Charset": "UTF-8",
                    }
                },
            },
        )
        if request['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()

    def send_payment_failed_email(self, email, price, card, invoice_url, next_payment_attempt):
        # Get email template
        with open(os.path.dirname(__file__) + "/payment_failed.html", "r") as fopen:
            HTML_EMAIL_CONTENT = fopen.read()
        # Add parameters
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{INVOICE_URL}', invoice_url)
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{PRICE}', str(price))
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{CARD}', str(card))
        if next_payment_attempt is None:
            HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{NEXT_PAYMENT_ATTEMPT}', 'This payment attempt was the last one. Your licence has automatically been changed to 1 Server.')
            HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{INVOICE_STYLE}', 'style="display: none"')
        else:
            next_payment_attempt = datetime.utcfromtimestamp(int(next_payment_attempt)).strftime('%a, %d %b %Y %H:%M:%S') + ' UTC+0'
            HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{NEXT_PAYMENT_ATTEMPT}', f"The next and last payment attempt will be made in 3 days ({next_payment_attempt}). If the next payment attempt does not succeed the license will be automatically changed to 1 Server.")
            HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{INVOICE_STYLE}', '')
        # Send mail
        request = self._ses.send_email(
            Source="Meteor Next <no-reply@meteornext.io>",
            Destination={
                "ToAddresses": [ email ],
            },
            Message={
                "Subject": {
                    "Data": "Your Meteor Next payment was unsuccessful",
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Html": {
                        "Data": HTML_EMAIL_CONTENT,
                        "Charset": "UTF-8",
                    }
                },
            },
        )
        if request['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()

    def send_expiring_card_email(self, email, card, card_number, code):
        # Get email template
        with open(os.path.dirname(__file__) + "/expiring_card.html", "r") as fopen:
            HTML_EMAIL_CONTENT = fopen.read()
        # Add parameters
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{CODE}', code)
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{CARD}', card)
        HTML_EMAIL_CONTENT = HTML_EMAIL_CONTENT.replace('{CARD_NUMBER}', str(card_number))
        # Send mail
        request = self._ses.send_email(
            Source="Meteor Next <no-reply@meteornext.io>",
            Destination={
                "ToAddresses": [ email ],
            },
            Message={
                "Subject": {
                    "Data": "Update your card information",
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Html": {
                        "Data": HTML_EMAIL_CONTENT,
                        "Charset": "UTF-8",
                    }
                },
            },
        )
        if request['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()
