import socket
import threading
import sys
import time
from helpers import send, recieve
from constants import *

PORT = int(sys.argv[1])
CONSECUTIVE_FAILS = int(sys.argv[2])

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def handle_authentication(conn):
    attempts = 0
    authenticated = False

    while not authenticated:
        send(conn, "[Authentication] Please enter your username: ")
        username = recieve(conn)
        send(conn, "[Authentication] Please enter your password: ")
        password = recieve(conn)

        if username == "user" and password == "password":
            send(conn, AUTHENTICATED)
            return True

        attempts += 1

        if attempts == CONSECUTIVE_FAILS:
            send(conn, ATTEMPTS_EXCEEDED)
            return False

        send(conn, INCORRECT_CREDENTIALS)


def handle_client(conn, addr):

    if handle_authentication(conn) == False:
        conn.close()

    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg = recieve(conn)

        if msg == DISCONNECTED:
            print(f"[Connection Lost] Connection was lost with {addr}")
            conn.close()
            return
        elif msg == DISCONNECT_MESSAGE:
            connected = False
        print(f"[{addr}] {msg}")

    print(f"[DISCONNECTED] {addr}")
    conn.close()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")


def start():
    try:
        server_socket.bind(ADDR)
        server_socket.listen()

        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
    except socket.error:
        print("[Err] Failed to start the server")
        sys.exit(1)


print("[STARTING] server is starting...")
start()

