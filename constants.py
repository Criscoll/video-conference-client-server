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
MISSING_ARGUMENTS = "[Invalid Input] Please include an argument in your MSG command"

SUCCESS = "Command Successfully run"
# ------------------ DLT Command --------------------
MSG_NOT_FOUND = "[Command Err] Unable to find the specified message in the logs"

# ------------------ DLT Command --------------------
