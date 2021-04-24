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


def is_later_than(formatted_input_date, formatted_logged_date):
    input_date = datetime.datetime.strptime(formatted_input_date, "%d %b %y %H:%M:%S")
    logged_date = datetime.datetime.strptime(formatted_logged_date, "%d %b %y %H:%M:%S")

    return logged_date > input_date


def next_active_seq_no():
    try:
        last_seq_no = 1
        with open("userlog.txt", "a+") as f:
            f.seek(0)

            for last_line in f:
                pass

            last_seq_no = last_line.split(" ")[0].strip(";")
            last_seq_no = str(int(last_seq_no) + 1)

    except FileNotFoundError:
        print(f"[File Err] Could not find the userlog.txt")
        last_seq_no = 1
    finally:
        return last_seq_no


# ------------------ TCP Transmission --------------------


def recieve(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)

    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        return msg
    else:
        return DISCONNECTED


def recieve_pickle(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)

    if msg_length:
        msg_length = int(msg_length)
        data = conn.recv(msg_length)
        msg = pickle.loads(data)
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


def send_pickle(socket, data):
    message = pickle.dumps(data)
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
            print(f"[Pickle Error] pickle file is empty, creating the file...")
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


def log_active_user(username, addr, udp_port):
    try:
        seq_no = next_active_seq_no()
        with open("userlog.txt", "a+") as wf:
            date = get_formatted_date()
            wf.write(f"{seq_no}; {date}; {username}; {addr}; {udp_port}\n")
    except FileNotFoundError:
        pass


def unlog_disconnected_user(username, addr, udp_port):
    try:
        with open("userlog.txt", "a+") as f:
            f.seek(0)
            file_lines = []
            line_found = False

            # fine the line being referenced, delete it and move all subsequent elements up
            for line in f:
                (line_no, line_date, line_user, line_ip, line_udp_port) = line.split(
                    ";"
                )
                line_no = line_no.strip()
                line_date = line_date.strip()
                line_user = line_user.strip()
                line_ip = line_ip.strip()
                line_udp_port = line_udp_port.strip()

                if line_found == False:
                    if (
                        username == line_user
                        and addr == line_ip
                        and udp_port == line_udp_port
                    ):
                        line_found = True
                    else:
                        file_lines.append(line)

                # line with users arguments was found
                else:
                    line_no = str(int(line_no) - 1)
                    file_lines.append(
                        f"{line_no}; {line_date}; {line_user}; {line_ip}; {line_udp_port}\n"
                    )

            if line_found == False:
                return USER_NOT_FOUND
            else:
                f.seek(0)
                f.truncate(0)
                for line in file_lines:
                    f.write(line)

                return SUCCESS

    except FileNotFoundError:
        pass


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
            authorised_to_delete = True

            # fine the line being referenced, delete it and move all subsequent elements up
            for line in f:
                (line_no, line_date, line_user, msg, edited) = line.split(";")
                line_no = line_no.strip()
                line_date = line_date.strip()
                line_user = line_user.strip()
                msg = msg.strip()
                edited = edited.strip()

                if line_found == False:
                    if msg_no == line_no and timestamp == line_date:

                        if username == line_user:
                            line_found = True
                        else:
                            authorised_to_delete = False
                            file_lines.append(line)
                    else:
                        file_lines.append(line)

                # line with users arguments was found
                else:
                    line_no = str(int(line_no) - 1)
                    file_lines.append(
                        f"{line_no}; {line_date}; {line_user}; {msg}; {edited}\n"
                    )

            if authorised_to_delete == False:
                return NOT_AUTHORISED_DLT
            elif line_found == False:
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
            authorised_to_edit = True
            # fine the line being referenced, delete it and move all subsequent elements up
            for line in f:
                (line_no, line_date, line_user, msg, edited) = line.split(";")
                line_no = line_no.strip()
                line_date = line_date.strip()
                line_user = line_user.strip()
                msg = msg.strip()
                edited = edited.strip()

                if msg_no == line_no and timestamp == line_date:

                    if username == line_user:
                        line_found = True
                        file_lines.append(
                            f"{line_no}; {get_formatted_date()}; {line_user}; {new_msg}; yes\n"
                        )
                    else:
                        authorised_to_edit = False
                        file_lines.append(line)

                else:
                    file_lines.append(line)

            if authorised_to_edit == False:
                return NOT_AUTHORISED_EDT
            elif line_found == False:
                return MSG_NOT_FOUND
            else:
                f.seek(0)
                f.truncate(0)
                for line in file_lines:
                    f.write(line)

                return SUCCESS

    except FileNotFoundError:
        print(f"[File Err] Could not find the messagelog.txt")


# ------------------ RDM Command --------------------
def read_messages(timestamp):
    try:
        with open("messagelog.txt", "r") as f:
            f.seek(0)
            messages = []

            for line in f:
                logged_date = line.split(";")[1].strip()
                if is_later_than(timestamp, logged_date):
                    messages.append(line)

            return messages

    except FileNotFoundError:
        print(f"[File Err] Could not find the messagelog.txt")
    except ValueError:
        return DATE_FORMAT_ERROR


# ------------------ ATU Command --------------------


def get_active_users(client_username, addr, udp_port):
    try:
        with open("userlog.txt", "r") as f:
            users = []

            for line in f:
                (_, _, username, ip, line_udp_port) = line.strip().split(";")

                username = username.strip()
                ip = ip.strip()
                line_udp_port = line_udp_port.strip()

                if (
                    username != client_username
                    or ip != addr
                    or line_udp_port != udp_port
                ):
                    users.append(line)

            return users

    except FileNotFoundError:
        print(f"[File Err] Could not find the userlog.txt")

