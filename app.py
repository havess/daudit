import os
import time
import threading
import logging
import ssl as ssl_lib

import certifi
from slackeventsapi import SlackEventAdapter
import slack

from message_builder import MessageType
from message_builder import MessageData
from message_builder import RunMessageData
from message_builder import HelpMessageData
from message_builder import ErrorMessageData
from message_builder import InvalidArgsMessageData
from message_builder import UnknownCommandMessageData

from message_builder import MessageType
from message_builder import MessageBuilder
from message_builder import DataError

from daudit import Daudit

import configparser
from mysql_integration.connector import Connector

# Remove when we go to production
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, endpoint="/slack/events")
client = slack.WebClient(os.environ["SLACK_API_TOKEN"], timeout=30)


my_daudit = None

def set_config(args: str):
    args = args.lower()
    configList = args.split(' ')

    if len(configList) != 2:
        raise Exception()

    key = configList[0]
    val = configList[1]

    valid_options = ["database", "table"]
    if key not in valid_options:
        raise Exception()

    config = configparser.ConfigParser()
    config.read("config.ini")
    config.set("DEFAULT", key, val)

    with open("config.ini", "w") as configfile:
        config.write(configfile)


def send_message(msg):
    # Post the message in Slack
    response = client.chat_postMessage(**msg)

    # Capture the timestamp of the message we've just posted.
    #builder.timestamp = response["ts"]

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on(event="message")
def handle_message(event_data):
    data = event_data.get("event")
    channel_id = data.get("channel")
    user_id = data.get("user")
    text = data.get("text")
    builder = MessageBuilder(channel_id)
    print("GOT MESSAGE")
    print(event_data)
    print(data)

    if text and user_id is not None:
        print("THERE IS TEXT")
        lower = text.lower()
        commandNArgs = lower.partition(' ')
        command = commandNArgs[0]
        args = commandNArgs[2]
        if command == "run":
            errs = my_daudit.run_audit()
            print("DONE AUDIT")
            if len(errs):
                msg = builder.build(MessageType.ERROR, ErrorMessageData(errs))
                return send_message(msg)

        elif command == "help":
            msg = builder.build(MessageType.HELP, HelpMessageData())
            return send_message(msg)

        elif command == "set":
            try:
                return set_config(args)
            except BaseException:
                msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())
                return send_message(msg)

        else:
            msg = builder.build(MessageType.UNKNOWN, UnknownCommandMessageData())
            return send_message(msg)


def main():
    global my_daudit
    my_daudit = Daudit('NYC311Data', 'demo')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

    # SETUP DATABASE CONNECTOR
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_name = config["DEFAULT"]["USER_NAME"]
    password = config["DEFAULT"]["PASSWORD"]
    database = config["DEFAULT"]["DATABASE"]
    table = config["DEFAULT"]["TABLE"]
    host = config["DEFAULT"]["HOST"]
    #conn = Connector(host, database, user_name, password)

    slack_events_adapter.start(port=3000),

if __name__ == "__main__":
    try:
        print("RUNNING")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")
