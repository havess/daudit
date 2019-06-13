import configparser
import os
from mysql_integration.connector import Connector

if __name__ == "__main__":
    config = configparser.ConfigParser()

    config.read(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            'configs', 
            'default.ini'
        )
    )

    user_name = config["USER_NAME"]
    password = config["PASSWORD"]
    database = config["DATABASE"]
    table = config["TABLE"]
    host = config["HOST"]

    conn = Connector(host, database, user_name, password)


def get_connection(config_name: str):
    config = configparser.ConfigParser()

    config.read(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            'configs', 
            config_name + '.ini'
        )
    )

    user_name = config['DEFAULT']["USER_NAME"]
    password = config['DEFAULT']["PASSWORD"]
    database = config['DEFAULT']["DATABASE"]
    table = config['DEFAULT']["TABLE"]
    host = config['DEFAULT']["HOST"]

    return Connector(host, database, user_name, password)