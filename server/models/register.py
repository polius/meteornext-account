from datetime import datetime

class Register:
    def __init__(self, sql):
        self._sql = sql

    def get(self, email):
        query = """
            SELECT a.account_id, u.account_id IS NULL AS 'validated'
            FROM accounts a
            LEFT JOIN accounts_url u ON u.account_id = a.id AND u.mode = 'validate_email'
            WHERE a.email = %s
        """
        return self._sql.execute(query, (email))

    def post(self, data):
        query = """
            INSERT INTO accounts (name, email, password, created_at)
            VALUES (%s, %s, %s, %s)
        """
        result = self._sql.execute(query, (data['name'], data['email'], data['password'], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

        query = """
            INSERT INTO accounts_url (account_id, mode, code)
            VALUES (%s, 'validate_email', %s)
        """
        self._sql.execute(query, (result, data['code']))
