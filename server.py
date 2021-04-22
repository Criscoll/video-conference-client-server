import socket, threading, sys, time, errno, pickle
from helpers import (
    send,
    recieve,
    get_formatted_date,
    get_blocked_timestamps,
    update_blocked_timestamps,
    get_time_since,
    next_message_no,
    log_message,
    delete_message,
)
from constants import *


PORT = int(sys.argv[1])  # PORT number
CONSECUTIVE_FAILS = int(sys.argv[2])  # Number of allowed fails during authentication

SERVER = socket.gethostbyname(socket.gethostname())  # The IP address of the server
ADDR = (SERVER, PORT)  # The endpoint of the server


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The server socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# handle_authentication: prompt client for username and password and verify whether
# these match with any entries in credentials.txt
def handle_authentication(conn, addr):
    def verify_credentials(username, password):
        with open("credentials.txt", "r") as f:
            for line in f:
                u_name, p_word = line.split(" ")
                if username == u_name and password == p_word.rstrip():
                    return True

        return False

    attempts = 0
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


# handle_client: the moment as client establishes a connection with the server, the server hands
# off the client to their own thread where any interaction with the server is handled.
# This should handle any asynchronous behaviour as each client is essentially handed their
# own little environment to make requests within. Most client handling is done here
def handle_client(conn, addr, seq_no, lock):
    # when a user is authenticated, log their info in userlog.txt
    def log_user_activity(udp_port):
        lock.acquire()
        with open("userlog.txt", "a") as wf:
            date = get_formatted_date()
            wf.write(f"{seq_no}; {date}; {addr[0]}; {udp_port}\n")
        lock.release()

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

        print(f"{msg_no} - {timestamp} - {username}")

        lock.acquire()
        result = delete_message(msg_no, timestamp, username)
        lock.release()

        if result == MSG_NOT_FOUND:
            send(conn, MSG_NOT_FOUND)
        else:
            send(conn, f"Message {msg_no} deleted at {get_formatted_date()}")

    def handle_rdm_command():
        pass

    def handle_edt_command():
        pass

    def handle_atu_command():
        pass

    # perform authenticaiton and reject client is they fail
    # Upon failure, the client must wait 10 seconds before re-attempting
    username = handle_authentication(conn, addr)
    authenticated = True if username else False

    if not authenticated:
        pass

    # client is authenticated and may begin interacting with the server
    else:
        udp_port = recieve(conn)
        log_user_activity(udp_port)

        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            try:
                msg = recieve(conn)
                print(f"[{addr}] {msg}")

                if msg == DISCONNECTED:
                    print("[Disconnected] Client disconnected remotely")
                    conn.close()
                    return

                (command, *args) = msg.strip().split(" ")

                if command not in Commands.__members__:
                    send(conn, INVALID_COMMAND)
                elif command == Commands.MSG.value:
                    handle_msg_command(username, args)
                elif command == Commands.DLT.value:
                    handle_dlt_command(username, args)
                elif command == Commands.EDT.value:
                    pass
                elif command == Commands.RDM.value:
                    pass
                elif command == Commands.ATU.value:
                    pass
                elif command == Commands.OUT.value:
                    send(conn, SUCCESS)
                    connected = False
                elif command == Commands.UDP.value:
                    pass

            except socket.error as e:
                if isinstance(e.args, tuple):
                    print(f"[Err] {e}")
                    if e.errno == errno.EPIPE:
                        print("[Err] Client disconnected remotely")
                        sys.exit(1)
                else:
                    print("Unknown error")
                    sys.exit(1)

    print(f"[DISCONNECTED] {addr}")
    conn.close()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")


# start: starts running the server and keeps it listening for new incomming connections.
# any new connections are given their own thread and handed off to handle_client()
def start():
    try:
        server_socket.bind(ADDR)
        server_socket.listen()

        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            conn, addr = server_socket.accept()
            lock = threading.Lock()
            seq_no = threading.activeCount() - 1
            thread = threading.Thread(
                target=handle_client, args=(conn, addr, seq_no, lock)
            )
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
    except socket.error:
        print("[Err] Failed to start the server")
        sys.exit(1)


# main: entry point of the program
print("[STARTING] server is starting...")
start()

