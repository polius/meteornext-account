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
                    WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
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
                    WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            LEFT JOIN mail m ON m.account_id = a.id AND m.action = 'verify_email'
            WHERE a.email = %s
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
                    WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
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
                a.created,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            WHERE id = %s
        """
        return self._sql.execute(query, (account_id))

    def get_license(self, account_id):
        query = """
            SELECT p.resources, p.price, l.key, l.in_use
            FROM licenses l
            JOIN products p ON p.id = l.product_id
            WHERE l.account_id = %s
            ORDER BY l.id DESC
            LIMIT 1
        """
        return self._sql.execute(query, (account_id))[0]

    def get_payments(self, account_id):
        query = """
            SELECT pa.date, pr.resources, pa.price, pa.status, pa.error, pa.invoice
            FROM payments pa
            JOIN products pr ON pr.id = pa.product_id
            WHERE pa.account_id = %s
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
            INSERT INTO accounts (email, password, ip, created)
            VALUES (%s, %s, %s, %s)
        """
        account_id = self._sql.execute(query, (data['email'], data['password'], data['ip'], now))

        # Create email code
        query = """
            INSERT INTO mail (account_id, action, code, created)
            VALUES (%s, 'verify_email', %s, %s)
        """
        self._sql.execute(query, (account_id, data['code'], now))

        # Create license
        query = """
            INSERT INTO `licenses` (`account_id`, `product_id`, `key`)
            VALUES (%s, 1, %s)
        """
        self._sql.execute(query, (account_id, data['key']))

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
            SET password = %s
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
        query = """
            DELETE FROM accounts
            WHERE id = %s
        """
        self._sql.execute(query, (account_id))

    def get_mfa(self, account_id):
        query = """
            SELECT 2fa_hash, webauthn_ukey, webauthn_pub_key, webauthn_credential_id, webauthn_sign_count, webauthn_rp_id, created
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
            INSERT INTO accounts_mfa (account_id, 2fa_hash, created)
            VALUES (%s, %s, %s)
        """
        self._sql.execute(query, (data['account_id'], data['2fa_hash'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    def enable_webauthn(self, data):
        self.disable_mfa(data['account_id'])
        query = """
            INSERT INTO accounts_mfa (account_id, webauthn_ukey, webauthn_pub_key, webauthn_credential_id, webauthn_sign_count, webauthn_rp_id, created)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self._sql.execute(query, (data['account_id'], data['webauthn_ukey'], data['webauthn_pub_key'], data['webauthn_credential_id'], data['webauthn_sign_count'], data['webauthn_rp_id'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

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
    def get_products(self):
        query = """
            SELECT resources, price
            FROM products
            ORDER BY id
        """
        return self._sql.execute(query)
    
    def get_products_by_resources(self, resources):
        query = """
            SELECT *
            FROM products
            WHERE resources = %s
        """
        return self._sql.execute(query, (resources))

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

    ###########
    # BILLING #
    ###########
    def new_purchase(self, account_id, product_id, date, price, status, error, stripe_id, invoice):
        query = """
            INSERT INTO payments (account_id, product_id, date, price, status, error, stripe_id, invoice)
            VALUES (%s, %s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s)
        """
        self._sql.execute(query, (account_id, product_id, date, price, status, error, stripe_id, invoice))

    def new_subscription(self, account_id, product_id, stripe_id, date):
        query = """
            DELETE FROM subscriptions
            WHERE account_id = %s
        """
        self._sql.execute(query, (account_id))

        query = """
            INSERT INTO subscriptions (account_id, product_id, stripe_id, date)
            VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
        """
        self._sql.execute(query, (account_id, product_id, stripe_id, date))

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
            INSERT INTO mail (account_id, action, code, data, created)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                code = VALUES(code),
                data = VALUES(data),
                created = VALUES(created);
        """
        self._sql.execute(query, (account_id, action, code, data, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    def clean_mail(self, account_id, action):
        query = """
            DELETE FROM mail
            WHERE account_id = %s 
            AND action = %s
        """
        self._sql.execute(query, (account_id, action))
