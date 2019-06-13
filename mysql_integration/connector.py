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
        self.cursor = self.cnx.cursor()

    def get_columns(self, table_name: str):
        query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = "%s";
        """ % (table_name)

        self.cursor.execute(query)

        return [c[0] for c in self.cursor.fetchall()]

    def create_nulls(self, table_name: str):

        cols = self.get_columns(table_name)

        for c in cols:
            if c != "CreatedDate" and c != "ClosedDate":
                query = """
                    UPDATE %s
                    SET %s = NULL 
                    WHERE %s = "";
                """ % (table_name, c, c)           
                self.cursor.execute(query)
                self.cnx.commit()
                print(c, self.cursor.rowcount, "record(s) affected")

    def get_null_profile(self, table_name: str, date_col: str, date: datetime.date, num_rows: int):
        sql_date = date.strftime('%Y-%m-%d %H:%M:%S')
        cols = self.get_columns(table_name)
        res = []

        for c in cols:
            if c != date_col:
                query = """
                    WITH q1 AS (
                        SELECT 
                            %s,
                            %s,
                            row_number() OVER (ORDER BY %s) AS rn 
                        FROM %s
                    ), q2 AS (
                        SELECT 
                            MAX(rn) AS max_rn 
                        FROM q1 
                        WHERE %s < '%s'
                    )
                    SELECT COUNT(*)
                    FROM q1, q2
                    WHERE 
                        CAST(max_rn AS SIGNED) - CAST(rn AS SIGNED) < %s
                        AND max_rn > rn
                        AND %s IS NULL;
                """ % (date_col, c, date_col, table_name, date_col, sql_date, str(num_rows), c)
                self.cursor.execute(query)
                res.append((c, self.cursor.fetchall()[0][0], num_rows))
        
        return res

    def get_null_propportions_for_date_range(self, table_name: str, date_col: str, start_date: datetime.date, end_date: datetime.date):
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        cols = self.get_columns(table_name)
        res = []

        for c in cols:
            if c != date_col:
                query = """
                    SELECT
                        SUM(IF(%s IS NULL, 1, 0)),
                        COUNT(*)
                    FROM
                        %s
                    WHERE
                        %s BETWEEN '%s' AND '%s'
                """ % (c, table_name, date_col, start_date, end_date)

                self.cursor.execute(query)
                a, b = self.cursor.fetchall()[0]
                res.append((c, a, b))

        return res