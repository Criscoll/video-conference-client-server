import socket
import sys

SERVER = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
UDP_PORT = int(sys.argv[3])
ADDR = (SERVER, SERVER_PORT)
FORMAT = "utf-8"
HEADER = 64
DISCONNECT_MESSAGE = "OUT"


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client_socket.send(send_length)
    client_socket.send(message)

