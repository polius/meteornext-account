from datetime import datetime

class Login:
    def __init__(self, sql):
        self._sql = sql

    def get(self, email):
        query = """
            SELECT 
                a.id,
                a.email,
                a.password,
                ae.account_id IS NULL AS 'verified',
                a.disabled,
                a.deleted,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            LEFT JOIN accounts_email ae ON ae.account_id = a.id AND ae.action = 'verify_email'
            WHERE a.email = %s
            AND a.deleted = 0
        """
        return self._sql.execute(query, (email))

    def get_mfa(self, account_id):
        query = """
            SELECT *
            FROM accounts_mfa
            WHERE account_id = %s
        """
        return self._sql.execute(query, (account_id))

    def put_last_login(self, data):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._sql.execute("UPDATE accounts SET ip = %s, last_login = %s WHERE id = %s", (data['ip'], now, data['id']))
