# this file is just used to pickle my data structures into a txt file
# this should be deleted prior to submitting
import datetime

from helpers import read_messages
from constants import *
import pickle


timestamp = "22 Apr 21 01:35:20"


messages = read_messages(timestamp)


print(messages)

