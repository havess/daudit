import datetime
import mysql_integration.app as sql
import pandas as pd
from math import sqrt
from enum import Enum

from message_builder import MessageType
from message_builder import MessageBuilder
from message_builder import DataError
from message_builder import ErrorType
class Daudit:
    def __init__(self, table_name, config_name="default"):
        self.table_name = table_name
        self.date_col = 'CreatedDate'
        self.db_conn = sql.get_connection(config_name)
        self.cols = self.db_conn.get_columns(self.table_name)
        # self.db_conn.create_nulls(self.table_name)

    def fetch_null_profile(self, num_rows: int):
        try:
            df = pd.read_csv("profiles/" + self.table_name + ".csv", index_col=0)
            return df
        except:
            HARDCODE_DATETIME = datetime.datetime(2019, 6, 1, 0, 0, 0)
            null_proportions = self.db_conn.get_null_profile(
                self.table_name, 
                self.date_col, 
                HARDCODE_DATETIME, 
                num_rows
            )
            df = pd.DataFrame(null_proportions)
            df.to_csv("profiles/" + self.table_name + ".csv", index=False)
            return df

    def fetch_null_proportions_for_date_range(self, start_date, end_date):
        return self.db_conn.get_null_propportions_for_date_range(self.table_name, self.date_col, start_date, end_date)       
    

    def is_null_count_anomalous(self, new_null_count: int, new_total_count: int, profile_null_count: int, profile_total_count: int):
        profile_prob_null = profile_null_count/profile_total_count
        total_prob_null = (profile_null_count + new_null_count)/(profile_total_count + new_total_count)

        z = 1.96  # 95% confidence interval
        conf_interval = z * sqrt(profile_prob_null * (1 - profile_prob_null)/profile_total_count)

        if total_prob_null > profile_prob_null + conf_interval:
            return True
        return False

    def run_audit(self):
        null_profile = self.fetch_null_profile(50000)

        HARDCODE_START_DATE = datetime.datetime(2019, 6, 1, 0, 0, 0)
        HARDCODE_END_DATE = datetime.datetime(2019, 6, 2, 0, 0, 0)

        new_null_proportions = self.fetch_null_proportions_for_date_range(
            HARDCODE_START_DATE, 
            HARDCODE_END_DATE
        )

        profile_dict = {col: (data[0], data[1]) for col, data in null_profile.iterrows()}

        errs = []
        for col, null_count, total in new_null_proportions:
            if self.is_null_count_anomalous(null_count, total, profile_dict[col][0], profile_dict[col][1]):
                # Add to list of errors
                errs.append(DataError(self.table_name, col, ErrorType.NULL_ROWS)) 



        return errs
