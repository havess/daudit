import os
import time
import threading
import logging
import ssl as ssl_lib
import threading
import queue
import json
import sys

from flask import request, make_response
from enum import Enum

import certifi
from slackeventsapi import SlackEventAdapter
import slack

from message_builder import *

from dauditer import Dauditer
from job import Job
from scheduler.scheduler import DauditScheduler

import configparser
from mysql_integration.connector import Connector
import mysql_integration.my_sql as sql

# Remove when we go to production
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], endpoint="/slack/events")
client = slack.WebClient(os.environ["SLACK_API_TOKEN"], timeout=30)

JOBS_CONFIG_PATH = 'scheduler/jobs.json'

def log(msg):
    print("\n\n\n", file=sys.stderr)
    print(msg, file=sys.stderr)
    print("\n\n\n", file=sys.stderr)

def extract_raw_text(text):
    if len(text) == 0 or text[0] != '<':
        return text

    if '|' in text:
        # This means the text was formatted as "<url|raw>" and we need to extract just raw
        return text.split('|')[1][:-1]

    log("PARSING TEXT ERROR")
    return text


class WorkType(Enum):
    RUN_AUDIT = 1
    INCREASE_CONF_INTERVAL = 2
    ACKNOWLEDGE_ERROR = 3

auditQueue = queue.Queue()

my_daudit_scheduler = None
g_worker = None

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
    members = client.users_list()['members']
    is_bot = False
    for member in members:
        if member['id'] == user_id:
            is_bot = member['is_bot']

    if not is_bot and data.get('channel_type') == 'im':
        convo_list = client.users_conversations()
        channels = []
        for channel in convo_list['channels']:
            channels.append(channel['name'])
        builder = MessageBuilder(channel_id)
        msg = builder.build(MessageType.CONFIRMATION, DMMessageData(channels))
        send_message(msg)
    return 200



# ============== App mention Events ============= #
# When a user mentions the app in a channel, the event type will be 'app_mention'.
# Here we'll link the message callback to the 'app_mention' event.
@slack_events_adapter.on(event="app_mention")
def handle_mention(event_data):

    log("IN HANDLE MENTION")
    log(event_data)

    data = event_data.get("event")
    channel_id = data.get("channel")
    user_id = data.get("user")
    text = data.get("text")

    builder = MessageBuilder(channel_id)
    commandNArgs = text.split(' ', 1)[1].partition(' ')
    command = commandNArgs[0]
    args = commandNArgs[2]

    if command == "run_audit":
        if args != '':
            log("BEFORE OPENING CONFIG OR FORMATTING")
            log(args)

            args = extract_raw_text(args)
            with open(JOBS_CONFIG_PATH, 'r+') as config_file:
                config_json = json.load(config_file)

            log("AFTER OPENING CONFIG AND FORMATTING")
            log(args)
            log(config_json)

            if args in config_json:
                db_host, db_name, table_name = args.split("/")
                audit_job = Job(table_name, db_name, db_host, config_json[args]['date_col'])
                auditQueue.put((WorkType.RUN_AUDIT, audit_job))

                msg = builder.build(MessageType.RUN, RunMessageData(table_name))
                send_message(msg)
                msg = builder.build(MessageType.CONFIRMATION, ConfirmationMessageData("run_audit"))
            else:
                # TODO: This should inform user that they entered an invalid job, maybe prompt them for list of jobs?
                msg = builder.build(
                    MessageType.DAUDIT_ERROR,
                    DauditErrorMessageData(
                        "Specified job does not exist. Try typing 'list_jobs' to see a list of valid jobs."
                    )
                )
        else:
            msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())
    elif command == "help":
        msg = builder.build(MessageType.HELP, HelpMessageData())
    elif command == "create_job":
        host_name, db_name, table_name, time = args.split(' ')
        my_daudit.add_monitored_table(host_name, db_name, table_name)
        # TODO: Better handling of time format
        time = int(time)
        res, err_msg = my_daudit_scheduler.schedule_job(host_name, db_name, table_name, time)
        if res == True:
            msg = builder.build(MessageType.CONFIRMATION, ConfirmationMessageData("create_job"))
        else:
            msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())
    elif command == "update_job":
        job_id, time, freq = args.split(" ")
        time = int(time)
        freq = int(freq)
        res, err_msg = my_daudit_scheduler.update_job(job_id, time, freq)
        if res == True:
            msg = builder.build(MessageType.CONFIRMATION, ConfirmationMessageData("update_job"))
        else:
            msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())

    elif command == "delete_job":
        job_id = args
        res, err_msg = my_daudit_scheduler.delete_job(job_id)
        if res == True:
            msg = builder.build(MessageType.CONFIRMATION, ConfirmationMessageData("delete_job"))
        else:
            msg = builder.build(MessageType.INVALID_ARGS, InvalidArgsMessageData())
    elif command == "list_databases":
        databases = sql.get_database_list()
        msg = builder.build(MessageType.LIST, ListMessageData("Database list", databases))
    elif command == "list_jobs":
        jobs = my_daudit_scheduler.get_job_list()
        msg = builder.build(MessageType.LIST, ListMessageData("Job list", jobs))
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
    return make_response("", 200)

@slack_events_adapter.server.route("/button", methods=["GET", "POST"])
def respond():
    """
    This route listens for incoming message button actions from Slack.
    """
    slack_payload = json.loads(request.form.get("payload"))
    # get the value of the button press
    action_value = slack_payload["actions"][0].get("value")
    # handle the action
    print(slack_payload)
    return action_handler(slack_payload)

@slack_events_adapter.server.route('/daudit/jobs', methods=["GET", "POST"])
def parse_jobs():
    # Get list of jobs
    job_list = []
    for job in request.json:
        job_list.append(job)
    # Add to auditQueue
    auditQueue.put((WorkType.RUN_AUDIT, job_list))
    return make_response("", 200)

def worker_function(name):
    while True:
        while auditQueue.empty():
            # yield quantum
            time.sleep(0)
        workType, data = auditQueue.get()

        log("PULLED WORK FROM QUEUE")
        log(data)

        if workType == WorkType.RUN_AUDIT:
            channel_id = data.get("channel")
            builder = MessageBuilder(channel_id)
            dauditer = Dauditer(data)

            log("STARTING AUDIT")
            errs = dauditer.run_audit()
            log("DONE AUDIT")

            if len(errs):
                msg = builder.build(MessageType.ERROR, ErrorMessageData(errs))
                send_message(msg)
            else:
                # TODO: Inform user audit completed without errors
                pass
        elif workType == WorkType.ACKNOWLEDGE_ERROR:
            action_data = data.get("actions")[0]
            alert_id = action_data.get("block_id")
            user_name = data.get("user").get("username")
            my_daudit.acknowledge_alert(alert_id, user_name)
        elif workType == WorkType.INCREASE_CONF_INTERVAL:
            action_data = data.get("actions")[0]
            alert_id = action_data.get("block_id")
            my_daudit.alert_not_useful(alert_id)


def main():
    global my_daudit_scheduler
    global g_worker
    my_daudit_scheduler = DauditScheduler()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

    g_worker = threading.Thread(target=worker_function, args=(1,))
    g_worker.start()
    slack_events_adapter.start(port=3000, host='0.0.0.0')

if __name__ == "__main__":
    try:
        print("RUNNING")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")
