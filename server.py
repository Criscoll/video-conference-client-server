import socket, threading, sys, time, errno, pickle
from helpers import (
    send,
    recieve,
    send_pickle,
    get_formatted_date,
    get_blocked_timestamps,
    update_blocked_timestamps,
    get_time_since,
    next_message_no,
    log_message,
    delete_message,
    edit_message,
    read_messages,
    log_active_user,
    unlog_disconnected_user,
    get_active_users,
)
from constants import *


# ---------------- server config  ----------------

# checks if the allowable fails argument is valid.
if not sys.argv[2].isnumeric() or int(sys.argv[2]) not in [1, 2, 3, 4, 5]:
    print(
        f"[Invalid Arguments] Invalid number of allowed failed consecutive attempts: {sys.argv[2]}. The valid value is an integer between 1 and 5"
    )
    sys.exit(1)


PORT = int(sys.argv[1])  # PORT number
CONSECUTIVE_FAILS = int(sys.argv[2])  # Number of allowed fails during authentication

SERVER = socket.gethostbyname(socket.gethostname())  # The IP address of the server
ADDR = (SERVER, PORT)  # The endpoint of the server


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The server socket
server_socket.setsockopt(
    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
)  # server socket config

# ---------------- handle authentication ----------------

# prompt client for username and password and verify whether
# these match with any entries in credentials.txt
def handle_authentication(conn, addr):
    def verify_credentials(username, password):
        with open("credentials.txt", "r") as f:
            for line in f:
                u_name, p_word = line.split(" ")
                if username == u_name and password == p_word.rstrip():
                    return True

        return False

    attempts = 0  # keeps track of user login attempts
    authenticated = False
    time_blocked_map = get_blocked_timestamps()

    if addr[0] in time_blocked_map and get_time_since(time_blocked_map[addr[0]]) <= 10:
        send(conn, BLOCKED)
        return None
    else:
        send(conn, REQUEST_AUTHENTICATION)
        while not authenticated:
            send(conn, "[Authentication] Please enter your username: ")
            username = recieve(conn)
            send(conn, "[Authentication] Please enter your password: ")
            password = recieve(conn)

            if verify_credentials(username, password):
                send(conn, AUTHENTICATED)
                return username

            attempts += 1

            if attempts == CONSECUTIVE_FAILS:
                update_blocked_timestamps(time_blocked_map, addr[0])
                send(conn, ATTEMPTS_EXCEEDED)
                return None

            send(conn, INCORRECT_CREDENTIALS)


# ---------------- handle client ----------------

# the moment as client establishes a connection with the server, the server hands
# off the client to their own thread where any interaction with the server is handled.
# This should handle any asynchronous behaviour as each client is essentially handed their
# own little environment to make requests within. Most client handling is done here and
# the handle function for each command is defined near the top.
def handle_client(conn, addr, lock):
    def handle_msg_command(username, args):
        if len(args) == 0:
            send(conn, MISSING_ARGUMENTS)
            return

        msg = " ".join(args)
        msg_no = next_message_no()
        date = get_formatted_date()
        lock.acquire()
        log_message(msg_no, date, username, msg, "no")
        lock.release()

        print(f'{username} posted MSG #{msg_no} "{msg}" at {date}.')
        send(conn, f"Message #{msg_no} posted at {date}.")

    def handle_dlt_command(username, args):
        if len(args) == 0:
            send(conn, MISSING_ARGUMENTS)
            return

        msg_no = args[0].strip("#")
        args.pop(0)
        timestamp = " ".join(args)

        lock.acquire()
        result = delete_message(msg_no, timestamp, username)
        lock.release()

        if result != SUCCESS:
            send(conn, result)
            print(f"> {username} attempts to delete message #{msg_no}. Delete fails.")
        else:
            send(conn, f"Message #{msg_no} deleted at {get_formatted_date()}")
            print(f"> {username} deletes message #{msg_no}")

    def handle_edt_command(username, args):
        if len(args) == 0:
            send(conn, MISSING_ARGUMENTS)
            return

        msg_no = args[0].strip("#")
        timestamp = " ".join(args[1:5])
        new_msg = " ".join(args[5:])

        lock.acquire()
        result = edit_message(msg_no, timestamp, new_msg, username)
        lock.release()

        if result != SUCCESS:
            send(conn, result)
            print(f"{username} attempts to edit message #{msg_no}. Edit fails.")
        else:
            send(conn, f"Message #{msg_no} edited at {get_formatted_date()}")
            print(f'> {username} edited MSG #{msg_no} "{new_msg}"')

    def handle_rdm_command(args):
        if len(args) == 0:
            send(conn, MISSING_ARGUMENTS)
            return

        timestamp = " ".join(args)
        messages = read_messages(timestamp)

        if messages == DATE_FORMAT_ERROR:
            send(conn, DATE_FORMAT_ERROR)
            print(f"> {username} issues RDM, but provided a wrong date format")

        elif len(messages) == 0:
            send(conn, NO_NEW_MSG)
            print(f"> {username} issues RDM, but there are no new messages to return")

        else:
            send(conn, SUCCESS)
            send_pickle(conn, messages)
            print(f"> {username} issues RDM. ")
            print(f"> Return messages: ")

            for message in messages:
                (msg_no, date, user, msg, _) = message.strip().split(";")
                print(f'  >> #{msg_no}; {user}: "{msg.strip()}" posted at {date}.')

    def handle_atu_command(udp_port):
        active_users = get_active_users(username, addr[0], udp_port)

        if len(active_users) == 0:
            send(conn, NO_ACTIVE_USERS)
            print(f"> {username} issues ATU, but there are not active users")

        else:
            send(conn, SUCCESS)
            send_pickle(conn, active_users)

            print(f"> {username} issues ATU")
            print(f"> Return active users: ")

            for user in active_users:
                (_, date, user, ip, udp_port) = user.strip().split(";")
                print(f" >> {user}, {ip}, {udp_port}, active since {date}.")

    # perform authenticaiton and reject client is they fail
    # Upon failure, the client must wait 10 seconds before re-attempting
    username = handle_authentication(conn, addr)
    authenticated = True if username else False

    # client is authenticated and may begin interacting with the server
    if authenticated:
        udp_port = recieve(conn)
        lock.acquire()
        log_active_user(username, addr[0], udp_port)  # log active user
        lock.release()

        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            try:
                msg = recieve(conn)
                # print(f"[{addr}] {msg}")

                if msg == DISCONNECTED:
                    print("[Disconnected] Client disconnected remotely")
                    unlog_disconnected_user(username, addr[0], udp_port)
                    conn.close()
                    return

                # retrieve the command and arguments from user message
                (command, *args) = msg.strip().split(" ")

                # handle user request
                if command not in Commands.__members__:
                    send(conn, INVALID_COMMAND)
                elif command == Commands.MSG.value:
                    handle_msg_command(username, args)
                elif command == Commands.DLT.value:
                    handle_dlt_command(username, args)
                elif command == Commands.EDT.value:
                    handle_edt_command(username, args)
                elif command == Commands.RDM.value:
                    handle_rdm_command(args)
                elif command == Commands.ATU.value:
                    handle_atu_command(udp_port)
                elif command == Commands.OUT.value:
                    unlog_disconnected_user(username, addr[0], udp_port)
                    send(conn, SUCCESS)
                    connected = False
                    print(f"{username} logout")

            except socket.error as e:
                # handle error if client disconnects without logging out
                if isinstance(e.args, tuple):
                    print(f"[Err] {e}")
                    if e.errno == errno.EPIPE:
                        print(f"[Err] Client {username} disconnected remotely")
                        sys.exit(1)
                else:
                    print("Unknown error")
                    sys.exit(1)

    print(f"[DISCONNECTED] {addr}")
    conn.close()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")


# ---------------- Start ----------------

# start: starts running the server and keeps it listening for new incomming connections.
# any new connections are given their own thread and handed off to handle_client()


def start():
    try:
        server_socket.bind(ADDR)
        server_socket.listen()

        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            conn, addr = server_socket.accept()
            print(f"NEW ADDR IS {addr}")
            lock = threading.Lock()
            thread = threading.Thread(target=handle_client, args=(conn, addr, lock))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
    except socket.error:
        print("[Err] Failed to start the server")
        sys.exit(1)


# ---------------- Program Entry Point ----------------

print("[STARTING] server is starting...")
start()

