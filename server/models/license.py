from datetime import datetime

class License:
    def __init__(self, sql):
        self._sql = sql

    def get(self, email):
        query = """
            SELECT a.`email`, l.`key`, l.`expiration`, l.`resources`, l.`in_use`, l.`uuid`, `l.last_used`
            FROM `licenses` l
            JOIN `accounts` a ON a.`id` = l.`account_id`
            WHERE a.`email` = %s
        """
        return self._sql.execute(query, (email))

    def post(self, email, uuid):
        query = """
            UPDATE `licenses`
            SET `in_use` = 1,
                `uuid` = %s,
                `last_used` = %s
            WHERE `email` = %s 
        """
        return self._sql.execute(query, (uuid, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), email))
