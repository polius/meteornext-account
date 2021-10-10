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
                a.deleted,
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
                a.created_at,
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
            SELECT l.resources, b.price, l.expiration, l.key, l.in_use
            FROM licenses l
            LEFT JOIN billing b ON b.license_id = l.id
            WHERE l.account_id = %s
            AND (b.status = 'success' OR b.license_id IS NULL)
            ORDER BY l.id DESC
            LIMIT 1
        """
        return self._sql.execute(query, (account_id))[0]

    def get_billing(self, account_id):
        query = """
            SELECT l.resources, b.price, b.purchase_date, b.status
            FROM billing b
            JOIN licenses l ON l.id = b.license_id AND l.account_id = %s 
            ORDER BY b.id DESC
        """
        return self._sql.execute(query, (account_id))

    ###########
    # PROFILE #
    ###########
    def change_password(self, account):
        self._sql.execute("UPDATE accounts SET password = %s WHERE id = %s", (account['password'], account['id']))

    def change_email(self, account, email):
        self._sql.execute("UPDATE accounts SET email = %s WHERE id = %s", (email, account['id']))
    
    def delete(self, account_id):
        self._sql.execute("UPDATE accounts SET deleted = 1, deleted_at = %s WHERE id = %s", (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), account_id))

    def get_mfa(self, account_id):
        query = """
            SELECT 2fa_hash, webauthn_ukey, webauthn_pub_key, webauthn_credential_id, webauthn_sign_count, webauthn_rp_id, created_at
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
            INSERT INTO accounts_mfa (account_id, 2fa_hash, created_at)
            VALUES (%s, %s, %s)
        """
        self._sql.execute(query, (data['account_id'], data['2fa_hash'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    def enable_webauthn(self, data):
        self.disable_mfa(data['account_id'])
        query = """
            INSERT INTO accounts_mfa (account_id, webauthn_ukey, webauthn_pub_key, webauthn_credential_id, webauthn_sign_count, webauthn_rp_id, created_at)
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

    ###########
    # LICENSE #
    ###########
    def get_pricing(self):
        query = """
            SELECT units, price
            FROM pricing
            ORDER BY id
        """
        return self._sql.execute(query)

    def unregister_license(self, account_id):
        query = """
            UPDATE licenses
            JOIN (
                SELECT l.id
                FROM licenses l
                LEFT JOIN billing b ON b.license_id = l.id
                WHERE l.account_id = %s
                AND (b.status = 'success' OR b.license_id IS NULL)
                ORDER BY l.id DESC
                LIMIT 1
            ) t USING (id)
            SET in_use = 0
        """
        self._sql.execute(query, (account_id))
