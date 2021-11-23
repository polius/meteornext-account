from datetime import datetime

class Register:
    def __init__(self, sql):
        self._sql = sql

    def get(self, email):
        query = """
            SELECT id
            FROM accounts
            WHERE email = %s
        """
        return self._sql.execute(query, (email))

    def post(self, data):
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
