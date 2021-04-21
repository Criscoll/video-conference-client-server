import datetime
from constants import HEADER, FORMAT, DISCONNECTED


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
            time_blocked_map = pickle.load(pickle_in)
        except EOFError as e:
            print(e)
            time_blocked_map = {}
        finally:
            return time_blocked_map

    return {}


def update_blocked_timestamps(time_blocked_map):
    with open("blocked_timestamps.pickle", "a+b") as pickle_out:
        try:
            pickle.dump(a, time_blocked_map)
        except EOFError as e:
            print(e)

