# this file is just used to pickle my data structures into a txt file
# this should be deleted prior to submitting
import datetime

from helpers import read_messages
from constants import *
import pickle
import socket
import sys
from time import sleep
import threading


def test():
    global re_prompt
    sleep(5)
    print("\n>> file received")
    re_prompt = True


def should_re_prompt():
    global re_prompt
    global threads_closed
    while True:

        if threads_closed:
            break

        if re_prompt:
            print("", flush=True)
            print("Enter some input: ", end="", flush=True)
            re_prompt = False
        sleep(3)


re_prompt = False

thread = threading.Thread(target=test)
thread.start()

prompt_thread = threading.Thread(target=should_re_prompt)
prompt_thread.start()


print("Enter some input: ", end="", flush=True)
for line in sys.stdin:
    print("Enter some input: ", end="", flush=True)

