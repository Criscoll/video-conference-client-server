import socket
import sys
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
    pass


connect()
connected = True
print(f"Connected successfully to [{SERVER}]")

while connected:
    msg = input("Enter a message: ")
    send(client, msg)

    if msg == DISCONNECT_MESSAGE:
        connected = False

print(f"Disconnected from server [{SERVER}]")

