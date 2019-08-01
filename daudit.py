import datetime
import mysql_integration.app as sql
import scipy.stats as st
from math import sqrt
from mysql_integration.connector import Connector
from message_builder import ErrorType


from message_builder import MessageType, MessageBuilder, DataError, ErrorType

class Daudit:
    def __init__(self, table_name, config_name="default"):
        self.table_name = table_name
        self.date_col = 'CreatedDate'
        self.db_conn = sql.get_connection(config_name)
        self.db_conn_internal = Connector('127.0.0.1', 'daudit_internal', 'root', 'rootroot')
        self.cols = self.db_conn.get_columns(self.table_name)
        # self.db_conn.create_nulls(self.table_name)

    def validate_table_name(self, table_name: int):
        exists = self.get_table_id(table_name)
        if (exists):
            return True
        return False

    def is_null_count_anomalous(self, new_null_count: int, new_total_count: int, profile_null_count: int, profile_total_count: int, col_name: str):

        useful_counts = self.db_conn_internal.get_useful_counts(1, self.table_name, col_name)

        if len(useful_counts) == 0:
            useful_count, not_useful_count = 0, 0
        else:
            useful_count, not_useful_count = useful_counts[0]
        profile_prob_null = profile_null_count/profile_total_count
        total_prob_null = (profile_null_count + new_null_count)/(profile_total_count + new_total_count)

        conf_interval_padding = 1 - 2*(1/2)**(not_useful_count + 1)
        conf_interval = 0.95 + 0.05 * conf_interval_padding

        z = st.norm.ppf( (1 - conf_interval)/2 + conf_interval )

        print(col_name, z, conf_interval)

        conf_interval = z * sqrt(profile_prob_null * (1 - profile_prob_null)/profile_total_count)

        if total_prob_null > profile_prob_null + conf_interval:
            return True
        return False

    def perform_null_checks(self, profile_id: int, errs: list):
        HARDCODE_START_DATE = datetime.datetime(2019, 6, 1, 0, 0, 0)
        HARDCODE_END_DATE = datetime.datetime(2019, 6, 2, 0, 0, 0)

        new_null_proportions = self.db_conn.get_null_proportions_for_date_range(
            self.table_name,
            self.date_col,
            HARDCODE_START_DATE,
            HARDCODE_END_DATE
        )

        new_proportions_dict = {col: (null_count, total) for col, null_count, total in new_null_proportions}

        null_profile = self.db_conn_internal.get_internal_null_profile(
            profile_id,
            self.table_name
        )

        for col, null_count, total in null_profile:
            if self.is_null_count_anomalous(new_proportions_dict[col][0], new_proportions_dict[col][1], \
                null_count, total, col):
                # Add to list of errors
                table_id = self.get_table_id(self.table_name)
                column_id = self.db_conn_internal.get_column_id(col, table_id)
                alert_id = self.get_alert_id(table_id, int(ErrorType.NULL_ROWS), column_id)
                if len(alert_id) == 0:
                    # add error to alert table
                    self.create_alert(table_id, int(ErrorType.NULL_ROWS), column_id)
                    alert_id = self.get_alert_id(table_id, int(ErrorType.NULL_ROWS), column_id)
                errs.append(DataError(alert_id[0], self.table_name, col, ErrorType.NULL_ROWS))

    def perform_binary_relationship_checks(self, profile_id: int, errs: list):
        pass


    def generate_null_profile(self, profile_id: int, num_rows: int):
        HARDCODE_DATETIME = datetime.datetime(2019, 6, 1, 0, 0, 0)
        null_proportions = self.db_conn.get_null_profile(
            self.table_name,
            self.date_col,
            HARDCODE_DATETIME,
            num_rows
        )

        self.db_conn_internal.create_internal_null_profile(
            profile_id,
            num_rows,
            self.table_name,
            null_proportions
        )

    def generate_binary_relationship_profile(self, profile_id: int, num_rows: int):
        pass

    def generate_profile(self):
        profile_id = self.db_conn_internal.get_profile_id(self.table_name)

        if len(profile_id):
            return profile_id[0]

        num_rows = 50000

        self.db_conn_internal.create_profile(self.table_name, num_rows)
        profile_id = self.db_conn_internal.get_profile_id(self.table_name)[0]

        self.generate_null_profile(profile_id, num_rows)
        self.generate_binary_relationship_profile(profile_id, num_rows)

        return profile_id

    def get_table_id(self, table_name: str):
        table_id = self.db_conn_internal.get_table_id(table_name)
        return table_id

    def get_alert_id(self, table_id: id, notification_id: int, col_a: int, col_b = -1):
        alert_id = self.db_conn_internal.get_alert_id(table_id, notification_id, col_a, col_b)
        return alert_id

    def create_alert(self, table_id: int, notification_id: int, col_a: int, col_b = -1):
        self.db_conn_internal.create_alert(table_id, notification_id, col_a, col_b)

    def run_audit(self):
        errs = []
        profile_id = self.generate_profile()

        self.perform_null_checks(profile_id, errs)
        self.perform_binary_relationship_checks(profile_id, errs)

        return errs
