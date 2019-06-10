import configparser
from connector import Connector

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_name = config["DEFAULT"]["USER_NAME"]
    password = config["DEFAULT"]["PASSWORD"]
    database = config["DEFAULT"]["DATABASE"]
    table = config["DEFAULT"]["TABLE"]
    host = config["DEFAULT"]["HOST"]
    conn = Connector(host, database, user_name, password)
