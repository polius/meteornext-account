from datetime import datetime

class Account:
    def __init__(self, sql):
        self._sql = sql

    def get(self, user_id):
        query = """
            SELECT 
                a.id,
                a.email,
                a.password,
                a.disabled,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id 
            WHERE a.id = %s
        """
        return self._sql.execute(query, (user_id))

    def get_profile(self, user_id):
        query = """
            SELECT
                email,
                created,
                CASE
                    WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                    ELSE NULL
                END AS 'mfa'
            FROM accounts a
            LEFT JOIN accounts_mfa mfa ON mfa.account_id = a.id
            WHERE id = %s
        """
        return self._sql.execute(query, (user_id))

    def get_license(self, user_id):
        query = """
            SELECT l.servers, l.price, al.purchase_date, al.expiration_date, al.status
            FROM account_licenses al
            JOIN licenses l ON l.id = al.license_id
            WHERE al.account_id = %s
            AND al.status = 'active'
            ORDER BY l.id
        """
        return self._sql.execute(query, (user_id))

    def get_billing(self, user_id):
        query = """
            SELECT l.servers, l.price, al.purchase_date, al.expiration_date, al.status
            FROM account_licenses al
            JOIN licenses l ON l.id = al.license_id
            WHERE al.account_id = %s 
            ORDER BY l.id DESC
        """
        return self._sql.execute(query, (user_id))

    def change_password(self, user):
        self._sql.execute("UPDATE accounts SET password = %s WHERE id = %s", (user['password'], user['id']))

    def post(self, user_id, user):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._sql.execute("INSERT INTO users (username, password, email, coins, group_id, admin, disabled, change_password, created_by, created_at, password_at) SELECT %s, %s, %s, %s, id, %s, %s, %s, %s, %s, %s FROM groups WHERE name = %s", (user['username'], user['password'], user['email'], user['coins'], user['admin'], user['disabled'], user['change_password'], user_id, now, now, user['group']))

    def put(self, user_id, user):
        self._sql.execute("UPDATE users SET username = %s, password = COALESCE(%s, password), email = %s, coins = %s, admin = %s, disabled = %s, change_password = %s, group_id = (SELECT id FROM groups WHERE `name` = %s), updated_by = %s, updated_at = %s WHERE username = %s", (user['username'], user['password'], user['email'], user['coins'], user['admin'], user['disabled'], user['change_password'], user['group'], user_id, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), user['current_username']))

    def put_last_login(self, data):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._sql.execute("UPDATE users SET ip = %s, user_agent = %s, last_login = %s, last_ping = %s WHERE username = %s", (data['ip'], data['user_agent'], now, now, data['username']))

    def put_last_ping(self, user_id):
        self._sql.execute("UPDATE users SET last_ping = %s WHERE id = %s", (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), user_id))

    def delete(self, id):
        pass

    def exist(self, email):
        return self._sql.execute("SELECT EXISTS ( SELECT * FROM users WHERE username = %s) AS exist", (username))[0]['exist'] == 1
