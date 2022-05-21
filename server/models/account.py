from datetime import datetime

class Account:
    def __init__(self, sql):
        self._sql = sql

    def get(self, account_id):
        query = """
            SELECT 
                a.id,
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
            SELECT prod.resources, IFNULL(pric.price, 0)/100 AS 'price', l.access_key, l.secret_key, l.in_use
            FROM licenses l
            JOIN products prod ON prod.id = l.product_id
            LEFT JOIN prices pric ON pric.product_id = prod.id
            WHERE l.account_id = %s
            ORDER BY l.id DESC
            LIMIT 1
        """
        return self._sql.execute(query, (account_id))[0]

    def get_payments(self, account_id):
        query = """
            SELECT pa.stripe_id AS 'invoice_id', pa.created_date, pr.resources, pa.price, pa.status, pa.invoice
            FROM payments pa
            JOIN subscriptions s ON s.id = pa.subscription_id AND s.account_id = %s
            JOIN licenses l ON l.id = s.license_id
            JOIN products pr ON pr.id = l.product_id
            ORDER BY pa.id DESC
        """
        return self._sql.execute(query, (account_id))

    ############
    # REGISTER #
    ############
    def register(self, data):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        # Create account
        query = """
            INSERT INTO accounts (email, password, ip, created_date)
            VALUES (%s, %s, %s, %s)
        """
        account_id = self._sql.execute(query, (data['email'], data['password'], data['ip'], now))

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
                p.id AS 'product_id',
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
    def change_password(self, account):
        query = """
            UPDATE accounts
            SET `password` = %s
            WHERE id = %s
        """
        self._sql.execute(query, (account['password'], account['id']))

    def change_email(self, account_id, email):
        query = """
            UPDATE accounts
            SET email = %s
            WHERE id = %s
        """
        self._sql.execute(query, (email, account_id))
    
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
            SELECT pro.*, pri.stripe_id AS 'price_stripe_id'
            FROM products pro
            LEFT JOIN prices pri ON pri.product_id = pro.id
            WHERE pro.resources = %s
        """
        return self._sql.execute(query, (resources))[0]

    def get_products_by_stripe(self, stripe_id):
        query = """
            SELECT *
            FROM products
            WHERE stripe_id = %s
        """
        return self._sql.execute(query, (stripe_id))

    def unregister_license(self, account_id):
        query = """
            UPDATE licenses
            SET in_use = 0
            WHERE account_id = %s
        """
        self._sql.execute(query, (account_id))

    def change_license(self, account_id, product_id):
        query = """
            UPDATE licenses
            SET product_id = %s
            WHERE account_id = %s
        """
        self._sql.execute(query, (product_id, account_id))

    def downgrade_license(self, stripe_subscription_id):
        query = """
            UPDATE licenses
            JOIN subscriptions s ON s.license_id = licenses.id AND s.stripe_id = %s
            SET licenses.product_id = (SELECT id FROM products WHERE resources = 1)
        """
        self._sql.execute(query, (stripe_subscription_id))

    ###########
    # BILLING #
    ###########
    def new_purchase(self, subscription_stripe, date, price, status, stripe_id, invoice):
        query = """
            INSERT INTO payments (subscription_id, created_date, price, status, stripe_id, invoice)
            SELECT
                id AS 'subscription_id',
                FROM_UNIXTIME(%s) AS 'created_date',
                %s AS 'price',
                %s AS 'status',
                %s AS 'stripe_id',
                %s AS 'invoice'
            FROM subscriptions
            WHERE stripe_id = %s
            ON DUPLICATE KEY UPDATE
                created_date = VALUES(created_date),
                price = VALUES(price),
                status = VALUES(status),
                invoice = VALUES(invoice);
        """
        self._sql.execute(query, (date, price, status, stripe_id, invoice, subscription_stripe))

    def new_subscription(self, account_id, price_id, stripe_id, date):
        query = """
            INSERT INTO subscriptions (account_id, license_id, price_id, stripe_id, start_date)
            SELECT
                %(account_id)s AS 'account_id',
                (SELECT id FROM licenses WHERE account_id = %(account_id)s LIMIT 1) AS 'license_id',
                (SELECT id FROM prices WHERE stripe_id = %(price_id)s) AS 'price_id',
                %(stripe_id)s AS 'stripe_id',
                FROM_UNIXTIME(%(date)s) AS 'start_date'
        """
        self._sql.execute(query, {"account_id": account_id, "price_id": price_id, "stripe_id": stripe_id, "date": date})

    def remove_subscription(self, stripe_subscription_id):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            UPDATE subscriptions
            SET end_date = %s
            WHERE stripe_id = %s
        """
        self._sql.execute(query, (now, stripe_subscription_id))

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
