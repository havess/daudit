import mysql.connector
import datetime

class Connector:
    def __init__(self, database_host: str, database_name: str, database_user: str, password: str):
        self.database_host = database_host
        self.database_name = database_name
        self.database_user = database_user
        self.password = password
        self.cnx = mysql.connector.connect(user = self.database_user, password = self.password,
                                                  host = self.database_host, database = self.database_name)

    def get_null_proportion(self, table_name: str, column_name: str, date: datetime.date):
        query = ("select %s from %s where created_at > %s")
        cursor = self.cnx.cursor()
        cursor.execute(query, (column_name, table_name, date))
        null_count = 0
        row_count = 0
        for (column_name) in cursor:
            row_count += 1
            if (column_name is None):
                null_count += 1
        return null_count/row_count

    def get_null_proportion(self, table_name:str, column_name: str, date: datetime.date, num_rows: int):
        query = ("select %s from %s where created_at < %s limit %s")
        cursor = self.cnx.cursor()
        cursor.execute(query, (column_name, table_name, date, num_rows))
        null_count = 0
        row_count = 0
        for (column_name) in cursor:
            row_count += 1
            if (column_name is None):
                null_count += 1
        return null_count/row_count
