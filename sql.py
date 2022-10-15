import sqlite3


class SQLighter:

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.execute = self.connection.cursor().execute

    def save_sql(self, result, date, city):
        with self.connection:
            return self.execute("INSERT INTO `log` (`result`,`date`,`city`) VALUES (?,?,?)", (result, date, city,))

    def close(self):
        self.connection.close()
