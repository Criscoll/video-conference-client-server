import socket, errno, sys, pickle, threading
from helpers import send, recieve, recieve_pickle
from constants import *


SERVER = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
UDP_PORT = int(sys.argv[3])

ADDR = (SERVER, SERVER_PORT)
CLIENT_UDP_SERVER = socket.gethostbyname(
    socket.gethostname()
)  # The IP address of the server
CLIENT_UDP_ADDR = (CLIENT_UDP_SERVER, UDP_PORT)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_UDP_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_UDP_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def connect():
    try:
        client.connect(ADDR)
    except socket.timeout:
        print("[ERR] Connection timeout")
        sys.exit(1)
    except:
        print("[ERR] Unable to connect to server")
        sys.exit(1)


def login():
    try:
        authenticated = False
        server_msg = recieve(client)

        if server_msg == BLOCKED:
            print(server_msg)
            sys.exit(1)
        else:
            print(server_msg)
            while not authenticated:
                server_msg = recieve(client)
                send(client, input(server_msg))  # username
                server_msg = recieve(client)
                send(client, input(server_msg))  # password

                server_msg = recieve(client)

                if server_msg == AUTHENTICATED:
                    authenticated = True
                elif server_msg == INCORRECT_CREDENTIALS:
                    print(server_msg)
                elif server_msg == ATTEMPTS_EXCEEDED:
                    print(server_msg)
                    sys.exit(1)

    except:
        print("[ERR] Login Error")
        sys.exit(1)


def client_UDP_sender(addr, udp_port, filename):
    print(f"{addr} - {udp_port} - {filename}")


def client_UDP_server():
    try:
        client_UDP_receiver_socket.bind(CLIENT_UDP_ADDR)

        while True:
            data = client_UDP_receiver_socket.recv(1024)

            if stop_threads == True:
                break

    except socket.error as e:
        print(e)
        print("[Err] Failed to start the UDP listening server")
        sys.exit(1)


def handle_UDP_transfer(msg):
    args = msg.strip().split(" ")[1:3]
    if len(args) != 2:
        print("[UDP] Invalid set of arguments provided")
        return

    send(client, "ATU")
    result = recieve(client)

    if result != SUCCESS:
        print(result)
        return

    active_users = recieve_pickle(client)

    (target_user, filename) = msg.strip().split(" ")[1:3]

    user_found = False

    for user in active_users:
        (_, _, username, ip, udp_port) = user.strip().split(";")
        username = username.strip()
        if username == target_user:
            user_found = True
            client_UDP_sender_thread = threading.Thread(
                target=client_UDP_sender, args=(ip, udp_port, filename)
            )
            client_UDP_sender_thread.start()

    if not user_found:
        print(f"{target_user} is offline")


# ---------------- Program Entry Point ----------------

connect()
login()

connected = True
send(client, str(UDP_PORT))

# create a client side thread to handle incoming UDP packets, runs until client terminates
stop_threads = False
client_UDP_server_thread = threading.Thread(target=client_UDP_server)
client_UDP_server_thread.start()

print(f"Connected successfully to [{SERVER}]")

while connected:
    try:
        if client.fileno() == -1:
            print("[Connection Lost] Connection lost with server {SERVER}")
            sys.exit(1)

        msg = input(
            "Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT): "
        )
        command = msg.split(" ")[0].strip()

        if command == Commands.UDP.value:
            handle_UDP_transfer(msg)
            continue

        send(client, msg)
        server_msg = recieve(client)

        if server_msg != SUCCESS:
            print(server_msg)
        elif command == Commands.RDM.value:
            messages = recieve_pickle(client)
            for message in messages:
                (msg_no, date, user, msg, edited) = message.strip().split(";")
                print(f'> #{msg_no}; {user}: "{msg}" posted at {date}.')
        elif command == Commands.OUT.value:
            connected = False

        elif command == Commands.ATU.value:
            active_users = recieve_pickle(client)
            for user in active_users:
                (_, date, user, ip, udp_port) = user.strip().split(";")
                print(f"> {user}, {ip}, {udp_port}, active since {date}.")

    except socket.error as e:
        if isinstance(e.args, tuple):
            print(f"[Err] {e}")
            if e.errno == errno.EPIPE:
                print("[Err] Server disconnected remotely")
                sys.exit(1)
        else:
            print("Unknown error")
            sys.exit(1)


stop_threads = True

client_UDP_sender_socket.sendto(b" ", CLIENT_UDP_ADDR)
client_UDP_receiver_socket.close()
print(f"Disconnected from server [{SERVER}]")

