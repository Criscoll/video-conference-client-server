# this file is just used to pickle my data structures into a txt file
# this should be deleted prior to submitting
import datetime
from helpers import *
from constants import *
import pickle


a = "3 21 Feb 2021 16:03:01 this is a message"

args = a.strip().split(" ")

print(" ".join(args[5:]))
