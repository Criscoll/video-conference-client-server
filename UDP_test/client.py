import socket, errno, sys, pickle, threading, sys
from helpers import send, recieve, recieve_pickle
from constants import *
from time import sleep


# ---------------- client config ----------------

BUFSIZE = 1024
SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
UDP_PORT = int(sys.argv[3])

SERVER_ADDR = (SERVER_IP, SERVER_PORT)

CLIENT_IP = "127.0.0.1"  # The IP address of the UDP server
CLIENT_UDP_ADDR = (CLIENT_IP, UDP_PORT)

# initialise the required sockets
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_UDP_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_UDP_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# ---------------- connect ----------------


def connect():
    try:
        client.connect(SERVER_ADDR)
    except socket.timeout:
        print("[ERR] Connection timeout")
        sys.exit(1)
    except:
        print("[ERR] Unable to connect to server")
        sys.exit(1)


# ---------------- login ----------------


def login():
    try:
        authenticated = False
        server_msg = recieve(client)

        # check if user is currently blocked
        if server_msg == BLOCKED:
            print(server_msg)
            sys.exit(1)
        else:
            print(server_msg)

            # collect user credentials and verify the authentication
            while not authenticated:
                server_msg = recieve(client)  # server: enter username
                username = input(server_msg)
                send(client, username)  # username

                server_msg = recieve(client)  # server: enter password
                password = input(server_msg)
                send(client, password)  # password

                server_msg = recieve(client)  # response

                if server_msg == AUTHENTICATED:
                    authenticated = True
                    return username
                elif server_msg == INCORRECT_CREDENTIALS:
                    print(server_msg + "\n")
                elif server_msg == ATTEMPTS_EXCEEDED:
                    print(server_msg)
                    sys.exit(1)

        return ""

    except:
        sys.exit(1)


# ---------------- client_UDP_sender ----------------


def client_UDP_sender(addr, udp_port, filename, target_user, sender_user):
    user_address = (addr.strip(), int(udp_port))
    try:
        # read in data from the file and continually transfer it to the recipient until finished
        with open(filename, "rb") as f:
            client_UDP_sender_socket.sendto(sender_user.encode(FORMAT), user_address)
            client_UDP_sender_socket.sendto(filename.encode(FORMAT), user_address)
            data = f.read(BUFSIZE)
            while data:
                data_sent = client_UDP_sender_socket.sendto(data, user_address)
                print(f"\n  **Sending data chunk of size {data_sent}...")
                data = f.read(BUFSIZE)

            sleep(1)  # wait before prompting success to ensure the message is seen
            global re_prompt
            print(f"  >> Successfully transfered {filename} to {target_user} [{addr}]")
            re_prompt = True

    except FileNotFoundError:
        print(f'\n  !>> The file "{filename}" does not exist')
        re_prompt = True


# ---------------- client_UDP_server ----------------


def client_UDP_server():
    try:
        client_UDP_receiver_socket.bind(CLIENT_UDP_ADDR)

        while True:
            (sender_name, addr) = client_UDP_receiver_socket.recvfrom(BUFSIZE)
            (filename, addr) = client_UDP_receiver_socket.recvfrom(BUFSIZE)

            if stop_threads == True:
                return

            sender_name = sender_name.decode(FORMAT)
            filename = filename.decode(FORMAT)

            try:
                with open(filename, "wb+") as f:
                    data = client_UDP_receiver_socket.recv(BUFSIZE)
                    while data:
                        f.write(data)
                        client_UDP_receiver_socket.settimeout(2)
                        data = client_UDP_receiver_socket.recv(BUFSIZE)
            except socket.timeout:
                client_UDP_receiver_socket.settimeout(None)
                global re_prompt
                print(f'\n >> Recieved "{filename}" from {sender_name} | {addr[0]}')
                re_prompt = True

    except socket.error as e:
        print(e)
        print("[Err] Failed to start the UDP listening server")
        sys.exit(1)


# ---------------- handle_udp_transfer ----------------


def handle_UDP_transfer(msg, sender_username):
    udp_args = msg.strip().split(" ")[1:3]  # get relevant arguments from client msg
    if len(udp_args) != 2:
        print("[UDP] Invalid set of arguments provided")
        return

    # send an ATU command to retrieve a list of active users from the server
    send(client, "ATU")
    result = recieve(client)
    if result != SUCCESS:
        print(result)
        return
    active_users = recieve_pickle(client)

    # search for user in ATU list and if found begin transmitting the file to them
    (target_user, filename) = udp_args
    user_found = False
    for user in active_users:
        (_, _, username, ip, udp_port) = user.strip().split(";")
        username = username.strip()
        if username == target_user:
            user_found = True
            client_UDP_sender_thread = threading.Thread(
                target=client_UDP_sender,
                args=(ip, udp_port, filename, target_user, sender_username),
            )
            client_UDP_sender_thread.start()

    if not user_found:
        print(f"{target_user} is offline")


# ---------------- should_re_prompt ----------------


def should_re_prompt():
    global re_prompt
    global stop_threads
    while True:

        if stop_threads:
            break

        if re_prompt:
            print(
                "Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UDP): ",
                end="",
                flush=True,
            )
            re_prompt = False
        sleep(2)


# ---------------- Program Entry Point ----------------

connect()
client_username = login()

connected = True
send(client, str(UDP_PORT))

# create a client side thread to handle incoming UDP packets, runs until client terminates
client_UDP_server_thread = threading.Thread(target=client_UDP_server)
client_UDP_server_thread.start()

# periodically checks whether a re-prompt is necessary
stop_threads = False
re_prompt = False
re_prompt_thread = threading.Thread(target=should_re_prompt)
re_prompt_thread.start()

print(f"Connected successfully to [{SERVER_IP}]")

while connected:
    try:
        if client.fileno() == -1:
            print("[Connection Lost] Connection lost with server {SERVER_IP}")
            sys.exit(1)

        msg = input(
            "Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UDP): "
        )
        command = msg.split(" ")[0].strip()

        if command == Commands.UDP.value:
            handle_UDP_transfer(msg, client_username)
            continue

        send(client, msg)
        server_msg = recieve(client)

        if server_msg != SUCCESS:
            print(server_msg)
        elif command == Commands.RDM.value:
            messages = recieve_pickle(client)
            for message in messages:
                (msg_no, date, user, msg, edited) = message.strip().split(";")
                print(f' > #{msg_no}; {user}: "{msg.strip()}" posted at {date}.')
        elif command == Commands.OUT.value:
            connected = False

        elif command == Commands.ATU.value:
            active_users = recieve_pickle(client)
            for user in active_users:
                (_, date, user, ip, udp_port) = user.strip().split(";")
                print(f" > {user}, {ip}, {udp_port}, active since {date}.")

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

client_UDP_sender_socket.sendto(b" ", CLIENT_UDP_ADDR)  # to trigger thread recv
client_UDP_sender_socket.sendto(b" ", CLIENT_UDP_ADDR)

# client_UDP_receiver_socket.close()
# client_UDP_sender_socket.close()
print(f"Disconnected from server [{SERVER_IP}]")

