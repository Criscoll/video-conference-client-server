import socket, errno, sys
from helpers import send, recieve
from constants import *


SERVER = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
UDP_PORT = int(sys.argv[3])

ADDR = (SERVER, SERVER_PORT)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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


connect()
login()

connected = True
send(client, str(UDP_PORT))
print(f"Connected successfully to [{SERVER}]")

while connected:
    try:
        if client.fileno() == -1:
            print("[Connection Lost] Connection lost with server {SERVER}")
            sys.exit(1)

        msg = input(
            "Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT): "
        )
        send(client, msg)

        if msg == DISCONNECT_MESSAGE:
            connected = False
    except socket.error as e:
        if isinstance(e.args, tuple):
            print(f"[Err] {e}")
            if e.errno == errno.EPIPE:
                print("[Err] Server disconnected remotely")
                sys.exit(1)
        else:
            print("Unknown error")
            sys.exit(1)


print(f"Disconnected from server [{SERVER}]")

