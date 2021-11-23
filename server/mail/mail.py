import os
import boto3

class Mail:
    def __init__(self, conf):
        # Init client
        self._ses = boto3.client("ses", region_name=conf['aws']['region_name'], aws_access_key_id=conf['aws']['access_key'], aws_secret_access_key=conf['aws']['secret_access_key'])

    def send_verify_email(self, email, code):
        # Get email template
        with open(os.path.dirname(__file__) + "/verify_email.html", "r") as fopen:
            HTML_EMAIL_CONTENT = fopen.read().replace('{CODE}',code)
        # Send mail
        request = self._ses.send_email(
            Source="Meteor Next <no-reply@meteor2.io>",
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

    def send_reset_password(self, email, code):
        # Get email template
        with open(os.path.dirname(__file__) + "/reset_password.html", "r") as fopen:
            HTML_EMAIL_CONTENT = fopen.read().replace('{CODE}',code)
        # Send mail
        request = self._ses.send_email(
            Source="Meteor Next <no-reply@meteor2.io>",
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