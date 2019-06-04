from enum import Enum

class ErrorType(Enum):
    NULL_ROWS = 1

def err_to_string(errType) -> str:
    if errType == ErrorType.NULL_ROWS:
        return "We detected a change in the proportion of NULL cells"
    return "An unknown error has occured"

class DataError(Exception):
    def __init__(self, table: str, typ: ErrorType):
        self.table = table
        self.type = typ

    def to_str(self):
        return "*TABLE*: " + self.table + "\n" + err_to_string(self.type) 


class Auditer:
    def __init__(self, table: str, ticks: int):
        self.ticks = ticks
        self.table = table

    async def run(self) :
        for i in range(self.ticks):
            continue

        raise DataError(self.table, ErrorType.NULL_ROWS)
