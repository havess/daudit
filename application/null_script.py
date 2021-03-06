import datetime
import sys
import mysql_integration.my_sql as sql

def reset_all(db_conn, table_name):
    db_conn.reset_all(table_name)

def reset_col(db_conn, table_name, col_name):
    db_conn.reset_column(table_name, col_name)

def introduce_nulls(db_conn, table_name, col_name, start_date, end_date, null_prop):
    db_conn.add_nulls(table_name, col_name, start_date, end_date, null_prop)

def introduce_paired_data(db_conn, table_name,  col0_name, col0_val, col1_name, col1_val, paired_prop, start_date, end_date):
    db_conn.add_paired_data(table_name, col0_name, col0_val, col1_name, col1_val, paired_prop, start_date, end_date)


if __name__ == "__main__":
    db_conn = sql.get_connection("ec2-34-236-66-104.compute-1.amazonaws.com:daudit")

    if sys.argv[1] == "RESET":
        # Example Command:
        # python null_script.py RESET demo NYC311Data LocationType

        _, cmd, config_name, table_name, col_name = sys.argv
        reset_col(db_conn, table_name, col_name)
    elif sys.argv[1] == "RESET_ALL":
        # Example Command:
        # python null_script.py RESET_ALL demo NYC311Data

        _, cmd, config_name, table_name = sys.argv
        reset_all(db_conn, table_name)
    elif sys.argv[1] == "ADD_NULL":
        # Example Command:
        # python null_script.py ADD_NULL demo NYC311Data LocationType 0.1

        _, cmd, config_name, table_name, col_name, null_prop = sys.argv
        HARDCODE_START_DATE = datetime.datetime(2019, 6, 1, 0, 0, 0)
        HARDCODE_END_DATE = datetime.datetime(2019, 6, 2, 0, 0, 0)
        introduce_nulls(db_conn, table_name, col_name, HARDCODE_START_DATE, HARDCODE_END_DATE, null_prop)
    
    elif sys.argv[1] == "ADD_PAIRED":
        # Example Command:
        # python null_script.py ADD_PAIRED demo NYC311Data City BROOKLYN ComplaintType 'Noise - Residential' 1.0

        _, cmd, config_name, table_name, col0_name, col0_val, col1_name, col1_val, paired_prop = sys.argv
        HARDCODE_START_DATE = datetime.datetime(2019, 6, 1, 0, 0, 0)
        HARDCODE_END_DATE = datetime.datetime(2019, 6, 2, 0, 0, 0)
        introduce_paired_data(db_conn, table_name, col0_name, col0_val, col1_name, col1_val, paired_prop, HARDCODE_START_DATE, HARDCODE_END_DATE)


