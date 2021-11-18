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