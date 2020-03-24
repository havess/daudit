from enum import Enum, IntEnum

# This defines what type of message we are issuing.
class MessageType(Enum):
    RUN             = 1
    HELP            = 2
    ERROR           = 3
    INVALID_ARGS    = 4
    CONFIG          = 5
    UNKNOWN         = 6
    CONFIRMATION    = 7
    LIST            = 8
    DAUDIT_ERROR    = 9


# This defines the type of anomaly we have found in the data.
class ErrorType(IntEnum):
    NULL_ROWS = 1
    BINARY_RELATIONS_ANOMALY = 2

# Convenient way to pass anomaly information to the message builder.
class DataError(Exception):
    def __init__(self, alert_id: int, table: str, cols: list, typ: ErrorType, errorMsg: str):
        self.alert_id = alert_id
        self.table = table
        self.cols = cols
        self.type = typ
        self.errorMsg = errorMsg

    def to_str(self):
        table_str = "*TABLE*: " + self.table
        columns_str = "*COLUMN*:"
        for col in self.cols:
            columns_str += " "  + col
        return table_str + "\n" + columns_str + "\n" + self.errorMsg

# All messages in slack are markdown format, this creates a section block.
def create_block(message: str):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                message
            ),
        },
    }


def create_button_id(dataError):
    return str(int(dataError.alert_id))



# All types of messages might have their own arbitrary data to display. For convenience they should all be
# of type MessageData.
class MessageData:
    def to_notification_text(self) -> str:
        return "Unimplemented to_nofication_text function. Please file a bug."
    def to_markdown_block(self) -> str:
        return [create_block("Unimplemented to_markdown_block function. Please file a bug.")]

class RunMessageData(MessageData):
    def __init__(self, table: str):
        self.table = table
    def to_notification_text(self):
        return "Starting audit."
    def to_markdown_block(self):
        return [create_block("Starting an audit on table " + str(self.table) + ". \nYou will be notified when the audit has completed.")]

class HelpMessageData(MessageData):
    def to_notification_text(self):
        return "Daudit help."
    def to_markdown_block(self):
        return  [create_block("The following commands are supported by Daudit: \n\n" +
                "*run_audit <job>* - Initiate a full audit. \n" +
                "*create_job <db_host> <db_name> <table_name> <time>* - Create job to run periodically. \n" +
                "*update_job <db_host>/<db_name>/<table_name> <time> <frequency_in_days>* - Update scheduled job parameters. \n" +
                "*delete_job <db_host>/<db_name>/<table_name>* - Delete scheduled job. \n" +
                "*list_databases* - List databases. \n" +
                "*list_jobs* - Initiate a full audit.")]

class DMMessageData(MessageData):
    def __init__(self, channels):
        self._channels = channels
    def to_notification_text(self):
        return "Daudit does not support DMs."
    def to_markdown_block(self):
        channel_str = " "
        for ch in self._channels:
            channel_str += "#" + ch + " "
        return [create_block("Daudit does not currently support DMs, please mention daudit in one of the following channels:" + channel_str)]

class ErrorMessageData(MessageData):
    def __init__(self, errs):
        self.errors = errs
    def to_notification_text(self):
        return "Daudit audit complete."
    def to_markdown_block(self):
        block = []
        for err in self.errors:
            msg = err.to_str() + "\n"
            button_attachment = {
                    "type": "actions",
                    "block_id": create_button_id(err),
                    "elements": [
                            {
                                "type": "button",
                                "style": "primary",
                                "text": {
                                    "type": "plain_text",
                                    "text": "I'm on it!"
                                },
                                "action_id": "OnIt"
                            },
                            {
                                "type": "button",
                                "style": "danger",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Not Useful"
                                },
                                "action_id": "NotUseful"
                            }

                    ]
            }
            block +=  [create_block(msg), button_attachment]
        return block

class InvalidArgsMessageData(MessageData):
    def to_notification_text(self):
        return "Daudit invalid arguments."
    def to_markdown_block(self):
        return [create_block("Invalid arguments, try typing 'help' for argument info. \n\n")]

class DauditErrorMessageData(MessageData):
    def __init__(self, msg):
        self.msg = msg
    def to_notification_text(self):
        return "Daudit Error Message."
    def to_markdown_block(self):
        return [create_block(self.msg)]

class ConfirmationMessageData(MessageData):
    def __init__(self, confirmed):
        self._confirmed = confirmed
    def to_notification_text(self):
        return "Daudit operation " + self._confirmed + " completed successfully."
    def to_markdown_block(self):
        return [create_block("Operation `" + self._confirmed + "` completed successfully.\n\n")]

class UnknownCommandMessageData(MessageData):
    def to_notification_text(self):
        return "Invalid Daudit command."
    def to_markdown_block(self):
        return [create_block("Invalid command, try typing 'help'. \n\n")]

class DatabaseListMessageData(MessageData):
    def __init__(self, dbs):
        self._dbs = dbs
    def to_notification_text(self):
        return "Daudit database list request completed."
    def to_markdown_block(self):
        list_str  = ""
        for db in self._dbs:
            list_str += "➕\n" + "\t*Host*: " + db[0] + "\n\t*Name:* " + db[1] + "\n\t*ID:* " + db[0] + "/" + db[1] + "\n\n"
        list_str += "➕\n"
        return [create_block("Database List\n\n" + list_str)]

class JobListMessageData(MessageData):
    def __init__(self, jobs):
        self._jobs = jobs
    def to_notification_text(self):
        return "Daudit job list request completed."
    def to_markdown_block(self):
        list_str  = ""
        for job in self._jobs:
            list_str += "➕\n" + \
                        "\t*Job ID:* " + job[0] + "\n" + \
                        "\t*Hour of Day:* " + job[1] + "\n" + \
                        "\t*Freq in Days:* " + job[2] + "\n" + \
                        "\t*Date Created:* " + job[3] + "\n" + \
                        "\t*Last Ran:* "  + job[4] + "\n\n" 

        list_str += "➕\n"
        return [create_block("Job List\n\n" + list_str)]

class MessageBuilder:
    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.username = "daudit"
        self.timestamp = ""

    # This is the function you call to get a message object to pass to the slack API.
    def build(self, msgType: MessageType, messageData):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "text": messageData.to_notification_text(),
            "username": self.username,
            "blocks": messageData.to_markdown_block(),
        }

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]
