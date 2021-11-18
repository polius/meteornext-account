from datetime import datetime

class Mail:
    def __init__(self, sql):
        self._sql = sql

    def get(self, action, code):
        query = """
            SELECT account_id, action, code
            FROM accounts_email
            WHERE action = %s
            AND code = %s
        """
        return self._sql.execute(query, (action, code))

    def verify_email(self, account_id):
        query = """
            DELETE FROM accounts_email
            WHERE account_id = %s
            AND action = 'verify_email'
        """
        self._sql.execute(query, (account_id))

    def reset_password(self, email, code):
        query = """
            DELETE ae
            FROM accounts_email ae
            JOIN accounts a ON a.id = ae.account_id AND a.email = %s
        """
        self._sql.execute(query, (email))

        query = """
            INSERT INTO accounts_email (account_id, action, code, created)
            SELECT
                id AS 'account_id',
                'reset_password' AS 'action',
                %s AS 'code',
                %s AS 'created'
            FROM accounts
            WHERE email = %s
        """
        self._sql.execute(query, (code, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), email))

    def unlink_password(self, account_id):
        query = """
            DELETE FROM accounts_email
            WHERE action = 'reset_password'
            AND account_id = %s
        """
        self._sql.execute(query, (account_id))
