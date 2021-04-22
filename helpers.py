import datetime
from constants import *
import pickle


# ------------------ General Helpers --------------------


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


# ------------------ TCP Transmission --------------------


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


# ------------------ Authentication --------------------


def get_blocked_timestamps():
    with open("blocked_timestamps.pickle", "a+b") as pickle_in:
        try:
            pickle_in.seek(0)
            time_blocked_map = {}
            time_blocked_map = pickle.load(pickle_in)
        except EOFError:
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


# ------------------ MSG Command --------------------


def next_message_no():
    try:
        last_msg_no = 1
        with open("messagelog.txt", "a+") as f:
            f.seek(0)

            for last_line in f:
                pass

            last_msg_no = last_line.split(" ")[0].strip(";")
            last_msg_no = str(int(last_msg_no) + 1)

    except FileNotFoundError:
        print(f"[File Err] Could not find the messagelog.txt")
        last_msg_no = 1
    finally:
        return last_msg_no


def log_message(msg_no, date, username, msg, edited):
    try:
        with open("messagelog.txt", "a+") as wf:
            wf.write(f"{msg_no}; {date}; {username}; {msg}; {edited}\n")
    except FileNotFoundError:
        print(f"[File Err] Could not find the messagelog.txt")


# ------------------ DLT Command --------------------


def delete_message(msg_no, timestamp, username):
    try:
        with open("messagelog.txt", "a+") as f:
            f.seek(0)
            file_lines = []
            line_found = False

            # fine the line being referenced, delete it and move all subsequent elements up
            for line in f:
                (line_no, line_date, line_user, msg, edited) = line.split(";")
                line_no = line_no.strip()
                line_date = line_date.strip()
                line_user = line_user.strip()
                msg = msg.strip()
                edited = edited.strip()

                if line_found == False:
                    if (
                        msg_no == line_no
                        and timestamp == line_date
                        and username == line_user
                    ):
                        line_found = True
                    else:
                        file_lines.append(line)

                # line with users arguments was found
                else:
                    line_no = str(int(line_no) - 1)
                    file_lines.append(
                        f"{line_no}; {line_date}; {line_user}; {msg}; {edited}\n"
                    )

            if line_found == False:
                return MSG_NOT_FOUND
            else:
                f.seek(0)
                f.truncate(0)
                for line in file_lines:
                    f.write(line)

                return SUCCESS

    except FileNotFoundError:
        print(f"[File Err] Could not find the messagelog.txt")


# ------------------ EDT Command --------------------
def edit_message(msg_no, timestamp, new_msg, username):
    try:
        with open("messagelog.txt", "a+") as f:
            f.seek(0)
            file_lines = []
            line_found = False

            # fine the line being referenced, delete it and move all subsequent elements up
            for line in f:
                (line_no, line_date, line_user, msg, edited) = line.split(";")
                line_no = line_no.strip()
                line_date = line_date.strip()
                line_user = line_user.strip()
                msg = msg.strip()
                edited = edited.strip()

                if (
                    msg_no == line_no
                    and timestamp == line_date
                    and username == line_user
                ):
                    line_found = True
                    file_lines.append(
                        f"{line_no}; {get_formatted_date()}; {line_user}; {new_msg}; yes\n"
                    )
                else:
                    file_lines.append(line)

            if line_found == False:
                return MSG_NOT_FOUND
            else:
                f.seek(0)
                f.truncate(0)
                for line in file_lines:
                    f.write(line)

                return SUCCESS

    except FileNotFoundError:
        print(f"[File Err] Could not find the messagelog.txt")
