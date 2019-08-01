from enum import Enum, IntEnum

# This defines what type of message we are issuing.
class MessageType(Enum):
    RUN = 1
    HELP = 2
    ERROR = 3
    INVALID_ARGS = 4
    UNKNOWN = 5

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
    def to_markdown_block(self) -> str:
        return [create_block("Unimplemented to_markdown_block function")]

class RunMessageData(MessageData):
    def __init__(self, table: str):
        self.table = table
    def to_markdown_block(self):
        return [create_block("Starting an audit on table " + str(self.table) + ". \nYou will be notified when the audit has completed.")]

class HelpMessageData(MessageData):
    def to_markdown_block(self):
        return  [create_block("The following commands are supported by Daudit: \n\n" +
                "*run* - Initiate a full audit. \n" +
                "*set* <key> <value> - Initiate a full audit.")]

class ErrorMessageData(MessageData):
    def __init__(self, errs):
        self.errors = errs

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
    def to_markdown_block(self):
        return [create_block("Invalid arguments, try typing 'help' for argument info. \n\n")]


class UnknownCommandMessageData(MessageData):
    def to_markdown_block(self):
        return [create_block("Invalid command, try typing 'help'. \n\n")]


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
            "username": self.username,
            "blocks": messageData.to_markdown_block(),
        }

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]
