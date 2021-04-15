import socket
import threading
import sys
from helpers import send, recieve
from constants import *

PORT = int(sys.argv[1])
CONSECUTIVE_FAILS = int(sys.argv[2])

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)


def handle_authentication(conn):
    attempts = 0
    authenticated = False

    while not authenticated:

        username = input("[Authentication] Please enter your username: ")
        password = input("[Authentication] Please enter your password: ")


def handle_client(conn, addr):

    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = recieve(conn)
        print(f"[{addr}] {msg}")

        if msg == DISCONNECT_MESSAGE:
            connected = False

    print(f"[DISCONNECTED] {addr}")
    conn.close()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")


def start():
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()

