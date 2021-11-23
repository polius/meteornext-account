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
                a.disabled,
                a.stripe_id,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id 
            WHERE a.id = %s
        """
        return self._sql.execute(query, (account_id))

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
            SELECT l.resources, p.price, l.expiration, l.key, l.in_use
            FROM licenses l
            JOIN products p ON p.id = l.product_id
            WHERE l.account_id = %s
            ORDER BY l.id DESC
            LIMIT 1
        """
        return self._sql.execute(query, (account_id))[0]

    def get_billing(self, account_id):
        query = """
            SELECT id, date, resources, price, status, error
            FROM billing
            WHERE account_id = %s
            ORDER BY id DESC
        """
        return self._sql.execute(query, (account_id))

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

    def change_email(self, account, email):
        query = """
            UPDATE accounts
            SET email = %s
            WHERE id = %s
        """
        self._sql.execute(query, (email, account['id']))
    
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
    def get_products(self, resources=None):
        if resources:
            query = """
                SELECT price, stripe_id
                FROM products
                WHERE resources = %s
            """
            return self._sql.execute(query, (resources))
        else:
            query = """
                SELECT resources, price
                FROM products
                ORDER BY id
            """
            return self._sql.execute(query)

    def unregister_license(self, account_id):
        query = """
            UPDATE licenses
            SET in_use = 0
            WHERE account_id = %s
        """
        self._sql.execute(query, (account_id))

    def change_license(self, account_id, resources):
        query = """
            UPDATE licenses
            SET resources = %s
            WHERE account_id = %s
        """
        self._sql.execute(query, (resources, account_id))

    def create_customer(self, account_id, customer_id):
        query = """
            UPDATE accounts
            SET stripe_id = %s
            WHERE id = %s
        """
        self._sql.execute(query, (customer_id, account_id))

    ###########
    # BILLING #
    ###########
    def new_purchase(self, account_id, date, resources, price, status, error, stripe_id):
        query = """
            INSERT INTO billing (account_id, date, resources, price, status, error, stripe_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self._sql.execute(query, (account_id, date, resources, price, status, error, stripe_id))

    ########
    # MAIL #
    ########
    def get_mail(self, action, code):
        query = """
            SELECT account_id, action, code
            FROM mail
            WHERE action = %s
            AND code = %s
        """
        return self._sql.execute(query, (action, code))

    def reset_password(self, email, code):
        query = """
            DELETE m
            FROM mail m
            JOIN accounts a ON a.id = m.account_id AND a.email = %s
        """
        self._sql.execute(query, (email))

        query = """
            INSERT INTO mail (account_id, action, code, created)
            SELECT
                id AS 'account_id',
                'reset_password' AS 'action',
                %s AS 'code',
                %s AS 'created'
            FROM accounts
            WHERE email = %s
        """
        self._sql.execute(query, (code, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), email))

    def clean_mail(self, account_id, action):
        query = """
            DELETE FROM mail
            WHERE account_id = %s 
            AND action = %s
        """
        self._sql.execute(query, (account_id, action))
