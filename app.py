import os
import time
import threading
import logging
import asyncio
import ssl as ssl_lib

import certifi
import slack

from message_builder import MessageType
from message_builder import MessageBuilder

from daudit import DataError
from daudit import Daudit

import configparser
from mysql_integration.connector import Connector


my_daudit = None

"""This file serves as an example for how to create the same app, but running asynchronously."""

async def set_config(args : str):
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

    
# For simplicity we'll store our app data in-memory with the following data structure.
# messages_sent = {"channel": {"user_id": MessageBuilder}}
messages_sent = {}

async def get_message(web_client: slack.WebClient, user_id: str, channel: str, msgType: MessageType, errs = []):
    # Create a new message
    builder = MessageBuilder(channel, MessageType.HELP)

    # Get the message payload.
    message = {}
    if msgType == MessageType.RUN:
        message = builder.get_run_message()
    elif msgType == MessageType.HELP:
        message = builder.get_help_message()
    elif msgType == MessageType.ERROR:
        message = builder.get_err_message(errs)
    elif msgType == MessageType.INVALID_ARGS:
        message = builder.get_invalid_args_message()
    elif msgType == MessageType.UNKNOWN:
        message = builder.get_unsupported_message() 

    # Post the message in Slack
    response = await web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted.
    builder.timestamp = response["ts"]

    # Store the message sent in messages_sent.
    if channel not in messages_sent:
        messages_sent[channel] = {}
    messages_sent[channel][user_id] = builder


# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
@slack.RTMClient.run_on(event="team_join")
async def welcome_message(**payload):
    """Create and send an welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # Get WebClient so you can communicate back to Slack.
    web_client = payload["web_client"]

    # Get the id of the Slack user associated with the incoming event
    user_id = payload["data"]["user"]["id"]

    # Open a DM with the new user.
    response = web_client.im_open(user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    await get_message(web_client, user_id, channel, MessageType.HELP)


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack.RTMClient.run_on(event="message")
async def message(**payload):
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    user_id = data.get("user")
    text = data.get("text")

    if text and not user_id == None:
        lower = text.lower()
        commandNArgs = lower.partition(' ')
        command = commandNArgs[0]
        args = commandNArgs[2]
        if command == "run":
            errs = await my_daudit.run_audit()
            print("DONE AUDIT")
            if len(errs):
                return await get_message(web_client, user_id, channel_id, MessageType.ERROR, errs)

        elif command == "help":
            return await get_message(web_client, user_id, channel_id, MessageType.HELP)
        
        elif command == "set":
            try:
                return await set_config(args)
            except: 
                return await get_message(web_client, user_id, channel_id, MessageType.INVALID_ARGS)

        else:
            return await get_message(web_client, user_id, channel_id, MessageType.UNKNOWN)


async def audit():
    i = 0
    while i < 3:
        await asyncio.sleep(5)
        i  = i + 1


async def main():
    global my_daudit
    my_daudit = Daudit('NYC311Data', 'demo')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    loop = asyncio.get_event_loop()


    # SETUP DATABASE CONNECTOR
    config = configparser.ConfigParser()
    config.read("config.ini")
    user_name = config["DEFAULT"]["USER_NAME"]
    password = config["DEFAULT"]["PASSWORD"]
    database = config["DEFAULT"]["DATABASE"]
    table = config["DEFAULT"]["TABLE"]
    host = config["DEFAULT"]["HOST"]
    #conn = Connector(host, database, user_name, password)
    
    # INIT SLACK CLIENT
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    rtm_client = slack.RTMClient(
        token=slack_token, ssl=ssl_context, run_async=True, loop=loop
    )

    await asyncio.gather(
        #audit(),
        rtm_client.start(),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("INTERRUPT")
