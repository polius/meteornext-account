import time
import schedule
import threading
import traceback

class Cron:
    def __init__(self, app, sql):
        self._app = app
        self._sql = sql

        @app.before_first_request
        def start():
            # One-Time Tasks
            self.__one_time()
            # Schedule Tasks
            schedule.every().day.at("00:00").do(self.__run_threaded, self.__clean_mails)

            # Start Cron Listener
            t = threading.Thread(target=self.__run_schedule)
            t.start()

    def __one_time(self):
        pass

    def __run_threaded(self, job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    def __run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def __clean_mails(self):
        try:
            query = """
                SELECT a.*
                FROM accounts a 
                JOIN accounts_email ae ON a.id = ae.account_id AND ae.action = 'verify_email'
                WHERE DATE_ADD(a.created_at, INTERVAL 1 DAY) <= CURRENT_DATE
            """
            print(self._sql.execute(query))
            # query = """
            #     DELETE a
            #     FROM accounts a 
            #     JOIN accounts_email ae ON a.id = ae.account_id AND ae.action = 'verify_email'
            #     WHERE DATE_ADD(a.created_at, INTERVAL 1 DAY) <= CURRENT_DATE
            # """
            # self._sql.execute(query)

            query = """
                DELETE FROM accounts_email
                WHERE action = 'reset_password'
                AND DATE_ADD(created, INTERVAL 1 DAY) <= CURRENT_DATE
            """
            self._sql.execute(query)

        except Exception:
            traceback.print_exc()
