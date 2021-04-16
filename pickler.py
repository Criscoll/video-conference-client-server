# this file is just used to pickle my data structures into a txt file
# this should be deleted prior to submitting

import pickle

with open("credentials.txt", "r") as f:

    for line in f:
        print(line.split(" ")[0])

