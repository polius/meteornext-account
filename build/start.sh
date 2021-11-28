#!/bin/sh
cd /root/meteor2-account

cat >./server.conf <<EOF
{
    "sql": {
        "engine": "$SQL_ENGINE",
        "hostname": "$SQL_HOST",
        "port": "$SQL_PORT",
        "username": "$SQL_USER",
        "password": "$SQL_PASS",
        "database": "$SQL_DB"
    },
    "aws": {
        "region_name": "$AWS_REGION_NAME",
        "access_key": "$AWS_ACCESS_KEY",
        "secret_access_key": "$AWS_SECRET_ACCESS_KEY"
    },
    "stripe": {
        "api_key": "$STRIPE_API_KEY",
        "webhook_secret": "$STRIPE_WEBHOOK_SECRET"
    },
    "hcaptcha": {
        "secret": "$HCAPTCHA_SECRET"
    }
}
EOF

python3 app2.py
nginx
/bin/sh