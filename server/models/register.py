from datetime import datetime

class Register:
    def __init__(self, sql):
        self._sql = sql

    def get(self, email):
        query = """
            SELECT id
            FROM accounts
            WHERE deleted = 0
            AND email = %s
        """
        return self._sql.execute(query, (email))

    def post(self, data):
        # Create account
        query = """
            INSERT INTO accounts (email, password, ip, created_at)
            VALUES (%s, %s, %s, %s)
        """
        account_id = self._sql.execute(query, (data['email'], data['password'], data['ip'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

        # Create email code
        query = """
            INSERT INTO accounts_email (account_id, action, code, created)
            VALUES (%s, 'verify_email', %s, %s)
        """
        self._sql.execute(query, (account_id, data['code'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

        # Create license
        query = """
            INSERT INTO `licenses` (`account_id`, `key`)
            VALUES (%s, %s)
        """
        self._sql.execute(query, (account_id, data['key']))
