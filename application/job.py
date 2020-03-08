class Job:
    def __init__(self, table_name: str, db_name : str, db_host : str, date_col: str):
        self.table_name = table_name
        self.db_name = db_name
        self.db_host = db_host
        self.date_col = date_col # String name of the column in the table for which dates are stored
