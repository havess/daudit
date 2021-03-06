import configparser
import os
from mysql_integration.connector import Connector

PATH =  os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            'configs', 
            'db_config.ini'
        )

def get_db_descriptor(db_host, db_name):
    return db_host + ":" + db_name

def get_connection(db_descriptor):
    config = configparser.ConfigParser()

    config.read(PATH)

    user_name = config[db_descriptor]["USERNAME"]
    password = config[db_descriptor]["PASSWORD"]
    database = config[db_descriptor]["DATABASE"]
    host = config[db_descriptor]["HOST"]

    return Connector(host, database, user_name, password)

def get_database_list():
    config = configparser.ConfigParser()
    
    config.read(PATH)
    dbs = []
    for db in config:
        if db == 'DEFAULT':
            continue
        host, name = db.split(":")
        dbs.append((host, name))

    return dbs

def get_internal_connection():
    return Connector('127.0.0.1', 'daudit_internal', 'root', 'rootroot')

def add_config(host_name, db_name, username, password):
    config = configparser.ConfigParser()
    
    config.read(PATH)

    desc = get_db_descriptor(host_name, db_name)
    
    if desc in config:
        return False

    config[desc] = {
            'DATABASE' : db_name,
            'HOST' : host_name,
            'USERNAME' : username,
            'PASSWORD' : password
            }

    with open(PATH, "a") as configfile:
        config.write(configfile)

    return True

def modify_config(host_name, db_name, username, password):
    config = configparser.ConfigParser()
    config.read(PATH)
    desc = get_db_descriptor(host_name, db_name)
    
    if not (desc in config):
        return False

    config.set(desc, 'username', username)
    config.set(desc, 'password', password)
    
    with open(PATH, "w") as configfile:
        config.write(configfile)

    return True


