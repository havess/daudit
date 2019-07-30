from enum import Enum

# This defines what type of message we are issuing.
class MessageType(Enum):
    RUN = 1
    HELP = 2
    ERROR = 3
    INVALID_ARGS = 4
    UNKNOWN = 5

# This defines the type of anomaly we have found in the data.
class ErrorType(Enum):
    NULL_ROWS = 1

def err_to_string(errType) -> str:
    if errType == ErrorType.NULL_ROWS:
        return "We detected a change in the proportion of NULL cells"
    return "An unknown error has occured"

# Convenient way to pass anomaly information to the message builder.
class DataError(Exception):
    def __init__(self, table: str, col: str, typ: ErrorType):
        self.table = table
        self.col = col
        self.type = typ

    def to_str(self):
        return "*TABLE*: " + self.table + "\n*COLUMN*: " + self.col + "\n" + err_to_string(self.type) 

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
        msg = ""
        for err in self.errors:
            msg = msg + err.to_str() + "\n"
        button_attachment = {
		"type": "actions",
		"block_id": "actionblock789",
		"elements": [
			{
                            "type": "button",
                            "style": "primary",
                            "text": {
                                "type": "plain_text",
                                "text": "I'm on it!"
                            },
			},
                        {
                            "type": "button",
                            "style": "danger",
                            "text": {
                                "type": "plain_text",
                                "text": "Not Useful"
                            },
			}

		]
	}
        block =  [create_block(msg), button_attachment]
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
