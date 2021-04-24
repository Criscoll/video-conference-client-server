from enum import Enum

FORMAT = "utf-8"
HEADER = 64
DISCONNECTED = "Connection was dropped"

# ------------------ Authentication --------------------
AUTHENTICATED = "[Authentication] Success"
ATTEMPTS_EXCEEDED = (
    "[Authentication] Invalid password. Too many attempts made, please try again later"
)
INCORRECT_CREDENTIALS = (
    "[Authentication] Incorrect username or password, please try again..."
)


BLOCKED = "[Authentication] Your account is blocked due to multiple login failures. Please try again later"
REQUEST_AUTHENTICATION = "[Authentication] Authentication required..."


# ------------------ Logging --------------------
USER_NOT_FOUND = "[Active User Log] Could not find the specified user"


# ------------------ COMMANDS --------------------
class Commands(Enum):
    MSG = "MSG"
    DLT = "DLT"
    EDT = "EDT"
    RDM = "RDM"
    ATU = "ATU"
    OUT = "OUT"
    UDP = "UDP"


INVALID_COMMAND = (
    "[Invalid Input] Please begin your message with one of the outlined commands"
)
MISSING_ARGUMENTS = "[Invalid Input] Please include an argument in your command"

SUCCESS = "Command Successfully run"
# ------------------ DLT and EDT Command --------------------
MSG_NOT_FOUND = "[Command] Unable to find the specified message in the logs"
NOT_AUTHORISED_DLT = "[Command] Not authorised to DLT this message"
NOT_AUTHORISED_EDT = "[Command] Not authorised to EDT this message"
# ------------------ RDM Command --------------------
NO_NEW_MSG = "[RDM] There are no new messages after this timestamp"
DATE_FORMAT_ERROR = "[RDM] Incorrect format for date provided"


# ------------------ ATU Command --------------------
NO_ACTIVE_USERS = "There are currently no active users online"
