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
                email,
                created,
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
            SELECT l.servers, l.price, al.purchase_date, al.expiration_date, al.status
            FROM account_licenses al
            JOIN licenses l ON l.id = al.license_id
            WHERE al.account_id = %s
            AND al.status = 'active'
            ORDER BY l.id
        """
        return self._sql.execute(query, (account_id))

    def get_billing(self, account_id):
        query = """
            SELECT l.servers, l.price, al.purchase_date, al.expiration_date, al.status
            FROM account_licenses al
            JOIN licenses l ON l.id = al.license_id
            WHERE al.account_id = %s 
            ORDER BY l.id DESC
        """
        return self._sql.execute(query, (account_id))

    ###########
    # PROFILE #
    ###########
    def change_password(self, account):
        self._sql.execute("UPDATE accounts SET password = %s WHERE id = %s", (account['password'], account['id']))

    def change_email(self, account, email):
        self._sql.execute("UPDATE accounts SET email = %s WHERE id = %s", (email, account['id']))
    
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
