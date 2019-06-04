from enum import Enum
from auditer import DataError

class MessageType(Enum):
    RUN = 1
    HELP = 2
    ERROR = 3
    UNKNOWN = 4

class MessageBuilder:
    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Welcome to Daudit. I am your point of contact for all your data auditing needs.\n\n"
            ),
        },
    }

    RUN_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Starting a test run.\n\n"
            ),
        },
    }


    HELP_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "The following commands are supported by Daudit: \n\n"
                "*run* - Initiate a full audit."
            ),
        },
    }

    UNSUPPORTED_COMMAND_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Invalid command, try typing 'help'. \n\n"
            ),
        },
    }


    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel, msgType):
        self.channel = channel
        self.username = "daudit"
        self.timestamp = ""
        self.message_type = msgType

    def get_run_message(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "blocks": [
                self.RUN_BLOCK,
                self.DIVIDER_BLOCK,
            ],
        }

    def get_help_message(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username" : self.username,
            "blocks": [
                self.HELP_BLOCK,
                self.DIVIDER_BLOCK,
            ]
        }

    def get_unsupported_message(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username" : self.username,
            "blocks": [
                self.UNSUPPORTED_COMMAND_BLOCK,
                self.DIVIDER_BLOCK,
            ]
        }

    def get_err_message(self, err : DataError): 
        msg = err.to_str()
        return {
                "ts": self.timestamp,
                "channel": self.channel,
                "username": self.username,
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "*!!!! WARNING !!!!*\n"
                            "" + msg
                        ),
                    },
                }],
        }


    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]
