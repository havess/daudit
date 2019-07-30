import datetime
import sys
import mysql_integration.app as sql

def reset_all(db_conn, table_name):
    db_conn.reset_all(table_name)

def reset_col(db_conn, table_name, col_name):
    db_conn.reset_column(table_name, col_name)

def introduce_nulls(db_conn, table_name, col_name, start_date, end_date, null_prop):
    db_conn.add_nulls(table_name, col_name, start_date, end_date, null_prop)


if __name__ == "__main__":
    db_conn = sql.get_connection(sys.argv[2])

    if sys.argv[1] == "RESET":
        # Example Command:
        # python null_script.py RESET DEMO NYC311Data LocationType

        _, cmd, config_name, table_name, col_name = sys.argv
        reset_col(db_conn, table_name, col_name)
    elif sys.argv[1] == "RESET_ALL":
        # Example Command:
        # python null_script.py RESET_ALL DEMO NYC311Data

        _, cmd, config_name, table_name = sys.argv
        reset_all(db_conn, table_name)
    elif sys.argv[1] == "ADD_NULL":
        # Example Command:
        # python null_script.py ADD_NULL DEMO NYC311Data LocationType 0.5

        _, cmd, config_name, table_name, col_name, null_prop = sys.argv
        HARDCODE_START_DATE = datetime.datetime(2019, 6, 1, 0, 0, 0)
        HARDCODE_END_DATE = datetime.datetime(2019, 6, 2, 0, 0, 0)
        introduce_nulls(db_conn, table_name, col_name, HARDCODE_START_DATE, HARDCODE_END_DATE, null_prop)

