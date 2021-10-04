from datetime import datetime

class Profile:
    def __init__(self, sql):
        self._sql = sql

    def get(self, user_id=None):
        if username is None:
            query = """
                SELECT
                    u.id, u.username, g.name AS `group`, u.email, u.ip, u.user_agent, u2.username AS 'created_by', u.created_at, u3.username AS 'updated_by', u.updated_at, u.last_login, u.coins, u.admin, u.disabled, u.change_password, u.last_ping,
                    CASE
                        WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                        WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
                        ELSE NULL
                    END AS 'mfa'
                FROM users u
                LEFT JOIN user_mfa mfa ON mfa.user_id = u.id
                JOIN groups g ON g.id = u.group_id
                LEFT JOIN users u2 ON u2.id = u.created_by
                LEFT JOIN users u3 ON u3.id = u.updated_by
                ORDER BY u.last_login DESC, u.username ASC
            """
            return self._sql.execute(query)
        else:
            query = """
                SELECT
                    u.*,
                    g.name AS `group`,
                    go.user_id IS NOT NULL AS 'owner',
                    g.inventory_enabled, g.inventory_secured, g.deployments_enabled, g.deployments_basic, g.deployments_pro, g.monitoring_enabled, g.utils_enabled, g.client_enabled, g.coins_execution, g.coins_day,
                    CASE
                        WHEN mfa.2fa_hash IS NOT NULL THEN '2fa'
                        WHEN mfa.webauthn_ukey IS NOT NULL THEN 'webauthn'
                        ELSE NULL
                    END AS 'mfa'
                FROM users u
                LEFT JOIN user_mfa mfa ON mfa.user_id = u.id
                JOIN groups g ON g.id = u.group_id
                LEFT JOIN group_owners go ON go.group_id = g.id AND go.user_id = u.id
                WHERE u.username = %s
            """
            return self._sql.execute(query, (username))

    def post(self, user_id, user):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._sql.execute("INSERT INTO users (username, password, email, coins, group_id, admin, disabled, change_password, created_by, created_at, password_at) SELECT %s, %s, %s, %s, id, %s, %s, %s, %s, %s, %s FROM groups WHERE name = %s", (user['username'], user['password'], user['email'], user['coins'], user['admin'], user['disabled'], user['change_password'], user_id, now, now, user['group']))

    def put(self, user_id, user):
        self._sql.execute("UPDATE users SET username = %s, password = COALESCE(%s, password), email = %s, coins = %s, admin = %s, disabled = %s, change_password = %s, group_id = (SELECT id FROM groups WHERE `name` = %s), updated_by = %s, updated_at = %s WHERE username = %s", (user['username'], user['password'], user['email'], user['coins'], user['admin'], user['disabled'], user['change_password'], user['group'], user_id, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), user['current_username']))

    def change_password(self, user):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._sql.execute("UPDATE users SET password = %s, password_at = %s, change_password = 0 WHERE username = %s", (user['password'], now, user['username']))

    def put_last_login(self, data):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._sql.execute("UPDATE users SET ip = %s, user_agent = %s, last_login = %s, last_ping = %s WHERE username = %s", (data['ip'], data['user_agent'], now, now, data['username']))

    def put_last_ping(self, user_id):
        self._sql.execute("UPDATE users SET last_ping = %s WHERE id = %s", (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), user_id))

    def delete(self, id):
        pass

    def exist(self, email):
        return self._sql.execute("SELECT EXISTS ( SELECT * FROM users WHERE username = %s) AS exist", (username))[0]['exist'] == 1
