import datetime
import mysql_integration.my_sql as sql
import scipy.stats as st
from math import sqrt
from mysql_integration.connector import Connector
from message_builder import ErrorType

from message_builder import MessageType, MessageBuilder, DataError, ErrorType

class Dauditer:
    def __init__(self, job):
        self._job = job
        self.table_name = job.table_name
        self.date_col = job.date_col
        self.db_host = job.db_host
        self.db_name = job.db_name

        self.db_conn = sql.get_connection(sql.get_db_descriptor(job.db_host, job.db_name))
        self.db_conn_internal = sql.get_internal_connection()
        self.cols = self.db_conn.get_columns(self.table_name)

        self.NUM_ROWS = 50000;
        # self.db_conn.create_nulls(self.table_name)

    def validate_table_name(self):
        exists = self.db_conn_internal.validate_table_id(self.db_host, self.db_name, self.table_name)
        if (exists):
            self.table_id = self.db_conn_internal.get_table_id(self.db_host, self.db_name, self.table_name)
            return True
        return False

    def is_null_count_anomalous(self, new_null_count: int, new_total_count: int, profile_null_count: int, profile_total_count: int, col_name: str):

        useful_counts = self.db_conn_internal.get_useful_counts(1, self.table_id, col_name)

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

    def perform_null_checks(self, errs: list):
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
            self.profile_id,
            self.table_id
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
                errs.append(DataError(alert_id[0], self.table_name, [col], ErrorType.NULL_ROWS,
                    "We detected a change in the proportion of NULL cells."))

    def is_binary_relation_anomalous(self, new_rel_count: int, new_total_count: int, profile_rel_count: int, profile_total_count: int, col_a: str, col_b: str):

        col_a_useful_counts = self.db_conn_internal.get_useful_counts(1, self.table_id, col_a)
        col_b_useful_counts = self.db_conn_internal.get_useful_counts(1, self.table_id, col_b)

        if len(col_a_useful_counts) == 0:
            col_a_useful_count, col_a_not_useful_count = 0, 0
        else:
            col_a_useful_count, col_a_not_useful_count = col_a_useful_counts[0]

        if len(col_b_useful_counts) == 0:
            col_b_useful_count, col_b_not_useful_count = 0, 0
        else:
            col_b_useful_count, col_b_not_useful_count = col_b_useful_counts[0]

        profile_rel_prop = profile_rel_count/profile_total_count
        total_prob_rel = (profile_rel_count + new_rel_count)/(profile_total_count + new_total_count)

        conf_interval_padding_a = 1 - 2*(1/2)**(col_a_not_useful_count + 1)
        conf_interval_a = 0.999999 + 0.05 * conf_interval_padding_a

        conf_interval_padding_b = 1 - 2*(1/2)**(col_b_not_useful_count + 1)
        conf_interval_b = 0.999999 + 0.05 * conf_interval_padding_b

        conf_interval = (conf_interval_a + conf_interval_b)/2

        z = st.norm.ppf( (1 - conf_interval)/2 + conf_interval )

        conf_interval = z * sqrt(profile_rel_prop * (1 - profile_rel_prop)/profile_total_count)

        if total_prob_rel > profile_rel_prop + conf_interval:
            return True
        return False

    def perform_binary_relationship_checks(self, errs: list):
        HARDCODE_START_DATE = datetime.datetime(2019, 6, 1, 0, 0, 0)
        HARDCODE_END_DATE = datetime.datetime(2019, 6, 2, 0, 0, 0)

        new_binary_relations = self.db_conn.get_binary_relationships_for_date_range(
            self.table_name,
            self.date_col,
            HARDCODE_START_DATE,
            HARDCODE_END_DATE
        )

        new_binary_relations_dict = {(col_a, col_b, a, b): (count, num_rows) for col_a, col_b, a, b, count, num_rows in new_binary_relations}

        binary_relationship_profile = self.db_conn_internal.get_internal_binary_relationship_profile(
            self.profile_id,
            self.table_id
        )

        for col_a, col_b, a, b, count, num_rows in binary_relationship_profile:

            if (col_a, col_b, a, b) in new_binary_relations_dict:
                if self.is_binary_relation_anomalous(new_binary_relations_dict[(col_a, col_b, a, b)][0], new_binary_relations_dict[(col_a, col_b, a, b)][1], \
                    count, num_rows, col_a, col_b):

                    print("WE HAVE A BINARY RELATIONSHIP ANOMALY")
                    print(col_a, col_b, a, b)
                    print(new_binary_relations_dict[(col_a, col_b, a, b)][0], new_binary_relations_dict[(col_a, col_b, a, b)][1], count, num_rows)

                    table_id = self.get_table_id(self.table_name)
                    column_id_a = self.db_conn_internal.get_column_id(col_a, table_id)
                    columb_id_b = self.db_conn_internal.get_column_id(col_b, table_id)
                    alert_id = self.get_alert_id(table_id, int(ErrorType.BINARY_RELATIONS_ANOMALY), column_id_a, columb_id_b)
                    if len(alert_id) == 0:
                        # add error to alert table
                        self.create_alert(table_id, int(ErrorType.BINARY_RELATIONS_ANOMALY), column_id_a, columb_id_b)
                        alert_id = self.get_alert_id(table_id, int(ErrorType.BINARY_RELATIONS_ANOMALY), column_id_a, columb_id_b)
                    errs.append(DataError(alert_id[0], self.table_name, [col_a, col_b], ErrorType.BINARY_RELATIONS_ANOMALY,
                        "We detected a binary relationship anomaly with values (" + a + " " + b + ")"))
                    
                    break

    def generate_null_profile(self):
        HARDCODE_DATETIME = datetime.datetime(2019, 6, 1, 0, 0, 0)
        null_proportions = self.db_conn.get_null_profile(
            self.table_name,
            self.date_col,
            HARDCODE_DATETIME,
            self.NUM_ROWS
        )

        self.db_conn_internal.create_internal_null_profile(
            self.profile_id,
            self.NUM_ROWS,
            self.table_id,
            null_proportions
        )

    def generate_binary_relationship_profile(self):
        HARDCODE_DATETIME = datetime.datetime(2019, 6, 1, 0, 0, 0)
        binary_relationship_profile = self.db_conn.get_binary_relationship_profile(
            self.table_name,
            self.date_col,
            HARDCODE_DATETIME,
            self.NUM_ROWS
        )

        self.db_conn_internal.create_internal_binary_relationship_profile(
            self.profile_id,
            self.NUM_ROWS,
            self.table_id,
            binary_relationship_profile
        )

    def generate_profile(self):
        profile_id = self.db_conn_internal.get_profile_id(
            self.table_id 
        )

        if profile_id != -1:
            self.profile_id = profile_id
            return profile_id

        self.db_conn_internal.create_profile(
            self.table_id,
            self.NUM_ROWS
        )

        self.profile_id = self.db_conn_internal.get_profile_id(
            self.table_id 
        )

        self.generate_null_profile()
        self.generate_binary_relationship_profile()

        return profile_id

    def get_table_id(self, table_name: str):
        return self.table_id

    def get_alert_id(self, table_id: id, notification_id: int, col_a: int, col_b = -1):
        alert_id = self.db_conn_internal.get_alert_id(table_id, notification_id, col_a, col_b)
        return alert_id

    def create_alert(self, table_id: int, notification_id: int, col_a: int, col_b = -1):
        self.db_conn_internal.create_alert(table_id, notification_id, col_a, col_b)

    def acknowledge_alert(self, alert_id: int, user_name: str):
        self.db_conn_internal.acknowledge_alert(alert_id, user_name)
        alert_res = self.db_conn_internal.get_alert_info(alert_id)
        table_id = alert_res[0][0]
        notification_id = alert_res[0][1]
        column_id_a = alert_res[0][4]
        column_id_b = alert_res[0][5]
        notif_res = self.db_conn_internal.get_threshold_info(table_id, notification_id, column_id_a)
        if not notif_res:
            self.db_conn_internal.insert_notification_threshold(table_id, notification_id, column_id_a, 1, 0)
        else:
            id = notif_res[0][0]
            useful_count = notif_res[0][1]
            self.db_conn_internal.update_notification_useful_count(id, useful_count+1)
        if column_id_b != -1:
            notif_res = self.db_conn_internal.get_threshold_info(table_id, notification_id, column_id_b)
            if not notif_res:
                self.db_conn_internal.insert_notification_threshold(table_id, notification_id, column_id_b, 1, 0)
            else:
                id = notif_res[0][0]
                useful_count = notif_res[0][1]
                self.db_conn_internal.update_notification_useful_count(id, useful_count+1)

    def alert_not_useful(self, alert_id: int):
        alert_res = self.db_conn_internal.get_alert_info(alert_id)
        table_id = alert_res[0][0]
        notification_id = alert_res[0][1]
        column_id_a = alert_res[0][4]
        column_id_b = alert_res[0][5]
        notif_res = self.db_conn_internal.get_threshold_info(table_id, notification_id, column_id_a)
        if not notif_res:
            self.db_conn_internal.insert_notification_threshold(table_id, notification_id, column_id_a, 0, 1)
        else:
            id = notif_res[0][0]
            not_useful_count = notif_res[0][2]
            self.db_conn_internal.update_notification_not_useful_count(id, not_useful_count+1)
        if column_id_b != -1:
            notif_res = self.db_conn_internal.get_threshold_info(table_id, notification_id, column_id_b)
            if not notif_res:
                self.db_conn_internal.insert_notification_threshold(table_id, notification_id, column_id_b, 0, 1)
            else:
                id = notif_res[0][0]
                useful_count = notif_res[0][1]
                self.db_conn_internal.update_notification_not_useful_count(id, not_useful_count+1)


    def run_audit(self):
        errs = []

        if not self.validate_table_name():
            # TODO: Return some sort of error saying table does not exist?
            return []

        profile_id = self.generate_profile()

        self.perform_null_checks(errs)
        self.perform_binary_relationship_checks(errs)
        
        return errs