import mysql.connector
import datetime

class Connector:
    def __init__(self, database_host: str, database_name: str, database_user: str, password: str):
        self.database_host = database_host
        self.database_name = database_name
        self.database_user = database_user
        self.password = password
        self.config = {
            'user': self.database_user,
            'password': self.password,
            'host': self.database_host,
            'database': self.database_name,
        }

    def get_columns(self, table_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = "%s";
        """ % (table_name)

        cursor.execute(query)

        res = [c[0] for c in cursor.fetchall()]
        cnx.close()
        return res

    def reset_column(self, table_name: str, col_name: str):
        """
        Used to reset a column in a table to its original state for demo/testing purposes.
        There's a copy of the table called 'table_name'+'Source' that we used to reset.
        """

        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        source_table_name = table_name + 'Source'

        query = """
            UPDATE %s AS t1
            SET t1.%s = (
                SELECT %s
                FROM %s AS t2
                WHERE t1.id = t2.id
            );
        """ % (table_name, col_name, col_name, source_table_name)

        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def reset_all(self, table_name: str):
        """
        Used to reset all columns of a table.
        """
        for c in self.get_columns(table_name):
            self.reset_column(table_name, c)


    def add_nulls(self, table_name: str, col_name: str, start_date: datetime.date, end_date: datetime.date, null_prop: float):
        """
        Add nulls to a column in a table in the rows between start_date and end_date.
        """
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        query = """
            UPDATE %s
            SET %s = NULL
            WHERE
                RAND() < %s
                AND CreatedDate BETWEEN '%s' AND '%s';
        """ % (table_name, col_name, str(null_prop), start_date, end_date)

        cursor.execute(query)
        cnx.commit()
        cnx.close()


    def add_paired_data(self, table_name: str,  col0_name: str, col0_val: str, col1_name: str, col1_val : str, paired_prop: float, start_date: datetime.date, end_date: datetime.date):
        """
        Add nulls to a column in a table in the rows between start_date and end_date.
        """
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        query = """
            UPDATE %s
            SET %s = "%s", %s = "%s"
            WHERE
                RAND() < %s
                AND CreatedDate BETWEEN '%s' AND '%s';
        """ % (table_name, col0_name, col0_val, col1_name, col1_val, str(paired_prop), start_date, end_date)

        cursor.execute(query)
        cnx.commit()
        cnx.close()


    def create_nulls(self, table_name: str):
        """
        Just used to clean data and convert empty strings to NULL.
        """

        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        cols = self.get_columns(table_name)

        for c in cols:
            if c != "CreatedDate" and c != "ClosedDate":
                query = """
                    UPDATE %s
                    SET %s = NULL
                    WHERE %s = "";
                """ % (table_name, c, c)
                cursor.execute(query)
                cnx.commit()
                print(c, cursor.rowcount, "record(s) affected")

        cnx.close()

    def get_null_profile(self, table_name: str, date_col: str, date: datetime.date, num_rows: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
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
                cursor.execute(query)
                res.append((c, cursor.fetchall()[0][0], num_rows))

        cnx.close()
        return res

    def get_null_proportions_for_date_range(self, table_name: str, date_col: str, start_date: datetime.date, end_date: datetime.date):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
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

                cursor.execute(query)
                a, b = cursor.fetchall()[0]
                res.append((c, a, b))

        cnx.close()
        return res

    def get_table_id(self, table_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT table_id
            FROM monitored_tables
            WHERE
                table_name = '%s';
        """ % (table_name)

        cursor.execute(query)
        res = cursor.fetchall()[0][0]
        cnx.close()
        return res

    def validate_table_id(self, table_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT table_id
            FROM monitored_tables
            WHERE
                table_name = '%s';
        """ % (table_name)

        cursor.execute(query)
        res = len(cursor.fetchall())
        cnx.close()
        return res

    def create_column_id(self, col_name: str, table_id: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            INSERT INTO column_table (column_name, table_id)
            VALUES ('%s', %s)
        """ % (col_name, table_id)

        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def get_column_id(self, col_name: str, table_id: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT column_id
            FROM column_table
            WHERE
                column_name = '%s' AND
                table_id = %s;
        """ % (col_name, table_id)

        cursor.execute(query)

        try:
            res = cursor.fetchall()[0][0]
            cnx.close()
            return res
        except:
            cnx.close()
            self.create_column_id(col_name, table_id)
            return self.get_column_id(col_name, table_id)


    def get_alert_id(self, table_id: int, notification_id: int, col_a: int, col_b: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            SELECT ID
            FROM ALERT_TABLE
            WHERE TABLE_ID = %s AND NOTIFICATION_ID = %s AND column_id_a = %s AND column_id_b = %s;
            """% (table_id, notification_id, col_a, col_b)

        cursor.execute(query)
        alert_id = [c[0] for c in cursor.fetchall()]
        cnx.close()
        print(alert_id)
        return alert_id

    def create_alert(self, table_id: int, notification_id: int, col_a: int, col_b: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
            insert into alert_table (table_id, notification_id, start_date, column_id_a, column_id_b, is_acknowledged)
            values (%s, %s, '%s', %s, %s, 0)
            """ %(table_id, notification_id, current_date, col_a, col_b)
        print(query)
        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def create_profile(self, table_name: str, num_rows: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Expiry date is 30 days in the future:
        expiry_date = (datetime.datetime.now() + datetime.timedelta(30)).strftime('%Y-%m-%d %H:%M:%S')
        table_id = self.get_table_id(table_name)

        query = """
            INSERT INTO profile_table (table_id, num_rows, created_date, expiry_date)
            VALUES (%s, %s, '%s', '%s')
        """ % (table_id, str(num_rows), current_date, expiry_date)

        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def get_profile_id(self, table_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        table_id = self.get_table_id(table_name)

        query = """
            SELECT profile_id
            FROM profile_table
            WHERE
                table_id = %s AND
                expiry_date > '%s';
        """ % (table_id, current_date)

        cursor.execute(query)
        res = [c[0] for c in cursor.fetchall()]
        cnx.close()
        return res

    def create_internal_null_profile(self, profile_id: int, num_rows: int, table_name: str, null_data: list):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        table_id = self.get_table_id(table_name)

        for col_name, num_null_rows, _ in null_data:
            col_id = self.get_column_id(col_name, table_id)
            query = """
                INSERT INTO null_profile_table (profile_id, table_id, column_id, num_null_rows)
                VALUES (%s, %s, %s, %s)
            """ % (profile_id, table_id, col_id, num_null_rows)
            cursor.execute(query)

        cnx.commit()
        cnx.close()

    def get_internal_null_profile(self, profile_id: int, table_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT
                c.column_name,
                np.num_null_rows,
                p.num_rows
            FROM
                null_profile_table np
            JOIN
                monitored_tables m ON m.table_id = np.table_id
            JOIN
                column_table c ON c.column_id = np.column_id
            JOIN
                profile_table p ON p.profile_id = np.profile_id
            WHERE
                table_name = '%s' AND
                np.profile_id = %s;
        """ % (table_name, profile_id)

        cursor.execute(query)
        res = [c for c in cursor.fetchall()]
        cnx.close()
        return res

    def get_useful_counts(self, notification_id: int, table_name: str, col_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT
                useful_count,
                not_useful_count
            FROM
                notification_threshold nt
            JOIN
                monitored_tables m ON m.table_id = nt.table_id
            JOIN
                column_table c ON c.column_id = nt.column_id
            WHERE
                m.table_name = '%s' AND
                c.column_name = '%s';
        """ % (table_name, col_name)

        cursor.execute(query)
        res = [c for c in cursor.fetchall()]
        cnx.close()
        return res

    def get_binary_relationship_profile(self, table_name: str, date_col: str, date: datetime.date, num_rows: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        sql_date = date.strftime('%Y-%m-%d %H:%M:%S')
        cols = self.get_columns(table_name)
        res = []

        for x in range(len(cols)):
            for y in range(x + 1, len(cols)):
                col_a = cols[x]
                col_b = cols[y]
                # TODO: Remove this hardcoding and fix query
                if col_a == 'ComplaintType' and col_b == 'City' and col_a != date_col and col_b != date_col:
                    query = """
                        WITH q1 AS (
                            SELECT
                                %s,
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
                        SELECT
                            %s,
                            %s,
                            COUNT(*)
                        FROM q1, q2
                        WHERE
                            CAST(max_rn AS SIGNED) - CAST(rn AS SIGNED) < %s
                            AND max_rn > rn
                        GROUP BY
                            %s, %s
                        HAVING
                            COUNT(*) > 100;
                    """ % (date_col, col_a, col_b, date_col, table_name, date_col, sql_date, col_a, col_b, str(num_rows), col_a, col_b)

                    cursor.execute(query)

                    for a, b, count in cursor.fetchall():
                        res.append((col_a, col_b, a, b, count, num_rows))

        cnx.close()
        return res

    def create_internal_binary_relationship_profile(self, profile_id: int, num_rows: int, table_name: str, binary_relation_data: list):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        table_id = self.get_table_id(table_name)

        for col_a, col_b, a_content, b_content, count, _ in binary_relation_data:
            col_id_a = self.get_column_id(col_a, table_id)
            col_id_b = self.get_column_id(col_b, table_id)
            query = """
                INSERT INTO binary_relations_profile_table (profile_id, table_id, column_id_a, column_id_b, a_content, b_content, count)
                VALUES (%s, %s, %s, %s, '%s', '%s', %s)
            """ % (profile_id, table_id, col_id_a, col_id_b, a_content, b_content, count)
            cursor.execute(query)

        cnx.commit()
        cnx.close()

    def get_binary_relationships_for_date_range(self, table_name: str, date_col: str, start_date: datetime.date, end_date: datetime.date):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        cols = self.get_columns(table_name)
        res = []

        query = """
            SELECT 
                COUNT(*)
            FROM %s
            WHERE
                %s BETWEEN '%s' AND '%s';
        """ % (table_name, date_col, start_date, end_date)
        cursor.execute(query)
        num_rows = cursor.fetchall()[0][0]

        for x in range(len(cols)):
            for y in range(x + 1, len(cols)):
                col_a = cols[x]
                col_b = cols[y]
                # TODO: Remove this hardcoding and fix query
                if col_a == 'ComplaintType' and col_b == 'City' and col_a != date_col and col_b != date_col:
                    query = """
                        SELECT
                            %s,
                            %s,
                            COUNT(*)
                        FROM %s
                        WHERE
                            %s BETWEEN '%s' AND '%s'
                        GROUP BY
                            %s, %s;
                    """ % (col_a, col_b, table_name, date_col, start_date, end_date, col_a, col_b)

                    cursor.execute(query)

                    for a, b, count in cursor.fetchall():
                        res.append((col_a, col_b, a, b, count, num_rows))

        cnx.close()
        return res

    def get_internal_binary_relationship_profile(self, profile_id: int, table_name: str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        query = """
            SELECT
                c.column_name AS col_a_name,
                c2.column_name AS col_b_name,
                a_content,
                b_content,
                count,
                p.num_rows
            FROM
                binary_relations_profile_table brp
            JOIN
                monitored_tables m ON m.table_id = brp.table_id
            JOIN
                column_table c ON c.column_id = brp.column_id_a
            JOIN
                column_table c2 ON c2.column_id = brp.column_id_b
            JOIN
                profile_table p ON p.profile_id = brp.profile_id
            WHERE
                table_name = '%s' AND
                brp.profile_id = %s;
        """ % (table_name, profile_id)

        cursor.execute(query)
        res = [c for c in cursor.fetchall()]
        cnx.close()
        return res

    def acknowledge_alert(self, alert_id:int, user_name:str):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            update alert_table
            set is_acknowledged=1, acknowledged_by_user='%s'
            where id=%s
            """ % (user_name, alert_id)
        print(query)
        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def get_alert_info(self, alert_id: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            select table_id, notification_id, start_date, end_date, column_id_a, column_id_b, is_acknowledged, acknowledged_by_user
            from alert_table where id =%s
            """ %(alert_id)
        cursor.execute(query)
        res = [c for c in cursor.fetchall()]
        cnx.close()
        return res

    def get_threshold_info(self, table_id: int, notification_id: int, column_id: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            select id, useful_count, not_useful_count from notification_threshold where
            table_id = %s and notification_id = %s and column_id = %s
        """ %(table_id, notification_id, column_id)
        cursor.execute(query)
        res = [c for c in cursor.fetchall()]
        cnx.close()
        return res

    def insert_notification_threshold(self, table_id: int, notification_id: int, column_id: int, useful_count: int, not_useful_count: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            insert into notification_threshold(table_id, notification_id, column_id, useful_count, not_useful_count)
            values (%s, %s, %s, %s, %s)
        """ %(table_id, notification_id, column_id, useful_count, not_useful_count)
        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def update_notification_useful_count(self, id: int, useful_count: int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            update notification_threshold set useful_count = %s where id=%s
        """ %(useful_count, id)
        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def update_notification_not_useful_count(self, id:int, not_useful_count:int):
        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()
        query = """
            update notification_threshold set not_useful_count = %s where id=%s
        """ %(not_useful_count, id)
        cursor.execute(query)
        cnx.commit()
        cnx.close()
