import os
import sys
import time
import threading
import logging
import ssl as ssl_lib
import threading
import queue
import json

from flask import request, make_response
from enum import Enum

import certifi
from slackeventsapi import SlackEventAdapter
import slack

from message_builder import MessageType, MessageData, RunMessageData, HelpMessageData, ErrorMessageData, \
    InvalidArgsMessageData, \
    UnknownCommandMessageData, MessageBuilder, DataError

from daudit import Daudit

import configparser
from mysql_integration.connector import Connector

# Remove when we go to production
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, endpoint="/slack/events")
client = slack.WebClient(os.environ["SLACK_API_TOKEN"], timeout=30)


class WorkType(Enum):
    RUN_AUDIT = 1
    INCREASE_CONF_INTERVAL = 2
    ACKNOWLEDGE_ERROR = 3
    SHOW_REPORTS = 4


auditQueue = queue.Queue()

my_daudit = None
g_worker = None


def set_config(args: str):
    args = args.text()
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
    # builder.timestamp = response["ts"]


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on(event="message")
def handle_message(event_data):
    data = event_data.get("event")
    channel_id = data.get("channel")
    user_id = data.get("username")
    text = data.get("text")
    builder = MessageBuilder(channel_id)
    print("GOT MESSAGE")
    print(event_data)
    print(data)
    print("USERNAME")
    print(user_id)
    print(user_id == "daudit")

    if text and data.get("subtype") is None:
        print("\n\nSENDING MESSAGE\n\n")
        commandNArgs = text.partition(' ')
        command = commandNArgs[0]
        args = commandNArgs[2]
        if command == "run":
            if my_daudit.validate_table_name(args):
                msg = builder.build(MessageType.RUN, RunMessageData(args))
                send_message(msg)
                auditQueue.put((WorkType.RUN_AUDIT, data))
            else:
                msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())
                send_message(msg)

        elif command == "help":
            msg = builder.build(MessageType.HELP, HelpMessageData())
            send_message(msg)

        elif command == "set":
            try:
                return set_config(args)
            except BaseException:
                msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())
                send_message(msg)

        else:
            msg = builder.build(MessageType.UNKNOWN, UnknownCommandMessageData())
            send_message(msg)
    return 200


@slack_events_adapter.on(event="action")
def action_handler(payload):
    print("A button was clicked!")
    action_data = payload.get("actions")[0]
    if action_data.get("action_id") == "OnIt":
        auditQueue.put((WorkType.ACKNOWLEDGE_ERROR, payload))
    elif action_data.get("action_id") == "NotUseful":
        auditQueue.put((WorkType.INCREASE_CONF_INTERVAL, payload))
    elif action_data.get("action_id") == "ShowReports":
        auditQueue.put((WorkType.SHOW_REPORTS, payload))
    return make_response("", 200)


'''
- This route listens for incoming message button actions from Slack.
'''


@slack_events_adapter.server.route("/button", methods=["GET", "POST"])
def respond():
    slack_payload = json.loads(request.form.get("payload"))
    # get the value of the button press
    action_value = slack_payload["actions"][0].get("value")
    # handle the action
    print(slack_payload)
    return action_handler(slack_payload)


'''
- A function that watches the message queue to perform work.
- Runs on it's own thread.
'''


def worker_function(name):
    while True:
        while auditQueue.empty():
            continue
        workType, data = auditQueue.get()
        if workType == WorkType.RUN_AUDIT:
            channel_id = data.get("channel")
            builder = MessageBuilder(channel_id)
            print("STARTING AUDIT")
            errs = my_daudit.run_audit()
            print("DONE AUDIT")
            if len(errs):
                msg = builder.build(MessageType.ERROR, ErrorMessageData(errs))
                send_message(msg)
        elif workType == WorkType.ACKNOWLEDGE_ERROR:  # User acknowledged the error message on slack
            print(data)
            action_data = data.get("actions")[0]
            alert_id = action_data.get("block_id")
            user_name = data.get("user").get("username")
            my_daudit.acknowledge_alert(alert_id, user_name)
            print("Acknowledgeing error")
        elif workType == WorkType.INCREASE_CONF_INTERVAL:  # User clicked slack alert was not useful/serious enough
            print(data)
            action_data = data.get("actions")[0]
            alert_id = action_data.get("block_id")
            my_daudit.alert_not_useful(alert_id)
            print("Increasing confidence interval")
        elif workType == WorkType.SHOW_REPORTS:
            print(data)
            user_name = data.get("user").get("username")
            my_daudit.show_reports(user_name)


def main():
    # Check if specific data to test provided
    data = 'NYC311Data'
    if len(sys.argv) == 2:
        data = sys.argv[1]

    print("Initializing Daudit with dataset: " + data)

    global my_daudit
    global g_worker
    my_daudit = Daudit(data, 'demo')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

    g_worker = threading.Thread(target=worker_function, args=(1,))
    g_worker.start()
    slack_events_adapter.start(port=3000),


if __name__ == "__main__":
    try:
        print("RUNNING")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")
