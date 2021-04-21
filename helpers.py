import datetime
from constants import HEADER, FORMAT, DISCONNECTED
import pickle


def recieve(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)

    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        return msg
    else:
        return DISCONNECTED


def send(socket, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    socket.send(send_length)
    socket.send(message)


def get_formatted_date():
    date_obj = datetime.datetime.now()

    month, day, year = date_obj.strftime("%x").split("/")
    month = date_obj.strftime("%b")
    time = date_obj.strftime("%X")

    formatted_date = f"{day} {month} {year} {time}"

    return formatted_date


def get_time_since(date):
    date_obj = datetime.datetime.now()

    return (date_obj - date).total_seconds()


def get_blocked_timestamps():
    with open("blocked_timestamps.pickle", "a+b") as pickle_in:
        try:
            pickle_in.seek(0)
            time_blocked_map = {}
            time_blocked_map = pickle.load(pickle_in)
        except EOFError as e:
            print(f"[Pickle Error] pickle file is empty, returning empty dict ")
            time_blocked_map = {}
        finally:
            return time_blocked_map

    return {}


def update_blocked_timestamps(time_blocked_map, ip):
    with open("blocked_timestamps.pickle", "wb+") as pickle_out:
        try:
            date_obj = datetime.datetime.now()
            time_blocked_map[ip] = date_obj
            pickle.dump(time_blocked_map, pickle_out)
            print(f"[Pickle] Successfully pickled timestamp of blocked user - {ip}")
        except EOFError as e:
            print(f"[Pickle Error] Could not update blocked timestamps - {e}")

