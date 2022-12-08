from datetime import datetime

class Account:
    def __init__(self, sql):
        self._sql = sql

    def get(self, account_id):
        query = """
            SELECT 
                a.id,
                a.name,
                a.email,
                a.password,
                m.account_id IS NULL AS 'verified',
                a.disabled,
                a.stripe_id,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_pub_key IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            LEFT JOIN mail m ON m.account_id = a.id AND m.action = 'verify_email'
            WHERE a.id = %s
        """
        return self._sql.execute(query, (account_id))
    
    def get_by_email(self, email):
        query = """
            SELECT 
                a.id,
                a.name,
                a.email,
                a.password,
                m.account_id IS NULL AS 'verified',
                a.disabled,
                a.stripe_id,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_pub_key IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            LEFT JOIN mail m ON m.account_id = a.id AND m.action = 'verify_email'
            WHERE a.email = %s
            AND a.deleted_date IS NULL;
        """
        return self._sql.execute(query, (email))

    def get_by_customer(self, customer_id):
        query = """
            SELECT 
                a.id,
                a.name,
                a.email,
                a.password,
                m.account_id IS NULL AS 'verified',
                a.disabled,
                a.stripe_id,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_pub_key IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            LEFT JOIN mail m ON m.account_id = a.id AND m.action = 'verify_email'
            WHERE a.stripe_id = %s
        """
        return self._sql.execute(query, (customer_id))

    def get_profile(self, account_id):
        query = """
            SELECT
                a.name,
                a.email,
                a.created_date,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_pub_key IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            WHERE id = %s
        """
        return self._sql.execute(query, (account_id))

    def get_license(self, account_id):
        query = """
            SELECT p.resources, IFNULL(l.price, 0) AS 'price', l.access_key, l.secret_key, l.in_use, l.unregistered_date
            FROM licenses l
            JOIN products p ON p.id = l.product_id
            WHERE l.account_id = %s
        """
        return self._sql.execute(query, (account_id))[0]

    def get_invoices(self, account_id):
        query = """
            SELECT i.created_date, p.resources, i.price, i.status, i.invoice_url
            FROM invoices i
            JOIN subscriptions s ON s.id = i.subscription_id AND s.account_id = %s
            JOIN licenses l ON l.id = s.license_id
            JOIN products p ON p.id = s.product_id
            ORDER BY i.id DESC
        """
        return self._sql.execute(query, (account_id))

    ############
    # REGISTER #
    ############
    def register(self, data):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        # Create account
        query = """
            INSERT INTO accounts (name, email, password, ip, created_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        account_id = self._sql.execute(query, (data['name'], data['email'], data['password'], data['ip'], now))

        # Enable sentry
        query = """
            INSERT INTO accounts_sentry (account_id, sentry_enabled)
            VALUES (%s, 1)
        """
        self._sql.execute(query, (account_id))

        # Create email code
        query = """
            INSERT INTO mail (account_id, action, code, created_date)
            VALUES (%s, 'verify_email', %s, %s)
        """
        self._sql.execute(query, (account_id, data['code'], now))

        # Create license
        query = """
            INSERT INTO `licenses` (`account_id`, `product_id`, `access_key`, `secret_key`)
            SELECT
                %s AS 'account_id',
                id AS 'product_id',
                %s AS 'access_key',
                %s AS 'secret_key'
            FROM products
            WHERE resources = 1
        """
        self._sql.execute(query, (account_id, data['access_key'], data['secret_key']))

    #########
    # LOGIN #
    #########
    def login(self, data):
        query = """
            UPDATE accounts
            SET
                ip = %s,
                last_login = %s
            WHERE id = %s
        """
        self._sql.execute(query, (data['ip'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), data['id']))

    ###########
    # PROFILE #
    ###########
    def change_name(self, account_id, name):
        query = """
            UPDATE accounts
            SET name = %s
            WHERE id = %s
        """
        self._sql.execute(query, (name, account_id))

    def change_email(self, account_id, email):
        query = """
            UPDATE accounts
            SET email = %s
            WHERE id = %s
        """
        self._sql.execute(query, (email, account_id))

    def change_password(self, account):
        query = """
            UPDATE accounts
            SET `password` = %s
            WHERE id = %s
        """
        self._sql.execute(query, (account['password'], account['id']))
    
    def delete(self, account_id):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            UPDATE accounts
            SET deleted_date = %s
            WHERE id = %s
        """
        self._sql.execute(query, (now, account_id))

    def get_mfa(self, account_id):
        query = """
            SELECT 2fa_hash, webauthn_pub_key, webauthn_credential_id, webauthn_sign_count, webauthn_rp_id, created_date
            FROM accounts_mfa
            WHERE account_id = %s
        """
        return self._sql.execute(query, (account_id))

    def disable_mfa(self, account_id):
        query = """
            DELETE FROM accounts_mfa
            WHERE account_id = %s
        """
        return self._sql.execute(query, (account_id))

    def enable_2fa(self, data):
        self.disable_mfa(data['account_id'])
        query = """
            INSERT INTO accounts_mfa (account_id, 2fa_hash, created_date)
            VALUES (%s, %s, %s)
        """
        self._sql.execute(query, (data['account_id'], data['2fa_hash'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    def enable_webauthn(self, data):
        self.disable_mfa(data['account_id'])
        query = """
            INSERT INTO accounts_mfa (account_id, webauthn_pub_key, webauthn_credential_id, webauthn_sign_count, webauthn_rp_id, created_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self._sql.execute(query, (data['account_id'], data['webauthn_pub_key'], data['webauthn_credential_id'], data['webauthn_sign_count'], data['webauthn_rp_id'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    def put_webauthn_sign_count(self, data):
        query = """
            UPDATE accounts_mfa
            SET webauthn_sign_count = %s
            WHERE account_id = %s
        """
        self._sql.execute(query, (data['webauthn_sign_count'], data['account_id']))

    def put_customer(self, data):
        query = """
            UPDATE accounts
            SET stripe_id = %s
            WHERE id = %s
        """
        self._sql.execute(query, (data['stripe_id'], data['account_id']))

    ###########
    # LICENSE #
    ###########   
    def get_product_by_resources(self, resources):
        query = """
            SELECT pri.stripe_id AS 'price_stripe_id'
            FROM products pro
            LEFT JOIN prices pri ON pri.product_id = pro.id AND pri.is_default = 1
            WHERE pro.resources = %s
            ORDER BY pri.id DESC
            LIMIT 1
        """
        return self._sql.execute(query, (resources))[0]

    def unregister_license(self, account_id):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            UPDATE licenses
            SET in_use = 0,
                unregistered_date = %s
            WHERE account_id = %s
        """
        self._sql.execute(query, (now, account_id))

    def change_license(self, account_id, product_id, price_id, price):
        query = """
            UPDATE licenses
            SET
                product_id = (SELECT id FROM products WHERE stripe_id = %s),
                price_id = (SELECT id FROM prices WHERE stripe_id = %s),
                price = %s
            WHERE account_id = %s
        """
        self._sql.execute(query, (product_id, price_id, price, account_id))

    def downgrade_license(self, stripe_subscription_id):
        query = """
            UPDATE licenses
            JOIN subscriptions s ON s.license_id = licenses.id AND s.stripe_id = %s
            SET
                licenses.product_id = (SELECT id FROM products WHERE resources = 1),
                licenses.price_id = NULL
        """
        self._sql.execute(query, (stripe_subscription_id))

    ###########
    # BILLING #
    ###########
    def new_purchase(self, subscription_id, created_date, price, status, stripe_id, next_payment_attempt, invoice_url):
        query = """
            INSERT INTO invoices (subscription_id, created_date, price, status, stripe_id, next_payment_attempt, invoice_url)
            SELECT
                id AS 'subscription_id',
                FROM_UNIXTIME(%s) AS 'created_date',
                %s AS 'price',
                %s AS 'status',
                %s AS 'stripe_id',
                %s AS 'next_payment_attempt',
                %s AS 'invoice_url'
            FROM subscriptions
            WHERE stripe_id = %s
            ON DUPLICATE KEY UPDATE
                created_date = VALUES(created_date),
                status = VALUES(status),
                next_payment_attempt = VALUES(next_payment_attempt);
        """
        self._sql.execute(query, (created_date, price, status, stripe_id, next_payment_attempt, invoice_url, subscription_id))

    def new_subscription(self, account_id, product_id, price_id, stripe_id, date):
        query = """
            INSERT IGNORE INTO subscriptions (account_id, license_id, product_id, price_id, stripe_id, start_date)
            SELECT
                %(account_id)s AS 'account_id',
                (SELECT id FROM licenses WHERE account_id = %(account_id)s LIMIT 1) AS 'license_id',
                (SELECT id FROM products WHERE stripe_id = %(product_id)s) AS 'product_id',
                (SELECT id FROM prices WHERE stripe_id = %(price_id)s) AS 'price_id',
                %(stripe_id)s AS 'stripe_id',
                FROM_UNIXTIME(%(start_date)s) AS 'start_date'
        """
        self._sql.execute(query, {"account_id": account_id, "product_id": product_id, "price_id": price_id, "stripe_id": stripe_id, "start_date": date})

    def remove_subscription(self, stripe_subscription_id):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            UPDATE subscriptions
            SET end_date = %s
            WHERE stripe_id = %s
        """
        self._sql.execute(query, (now, stripe_subscription_id))

    def expire_invoice(self, stripe_invoice_id):
        query = """
            UPDATE invoices
            SET status = 'expired',
                invoice_url = NULL
            WHERE stripe_id = %s
        """
        self._sql.execute(query, (stripe_invoice_id))

    ########
    # MAIL #
    ########
    def get_mail(self, action, code):
        query = """
            SELECT account_id, action, code, data
            FROM mail
            WHERE action = %s
            AND code = %s
        """
        return self._sql.execute(query, (action, code))

    def create_mail(self, account_id, action, code, data=None):
        query = """
            INSERT INTO mail (account_id, action, code, data, created_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                code = VALUES(code),
                data = VALUES(data),
                created_date = VALUES(created_date);
        """
        self._sql.execute(query, (account_id, action, code, data, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    def clean_mail(self, account_id, action):
        query = """
            DELETE FROM mail
            WHERE account_id = %s 
            AND action = %s
        """
        self._sql.execute(query, (account_id, action))
