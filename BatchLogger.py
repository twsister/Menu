import time
import datetime


def log(info):
    with open("log.txt", 'a+') as the_log:
        the_log.write("{}:\n".format(datetime.datetime.now()))
        the_log.write(info.strip() + "\n")


def append(info):
    with open("log.txt", 'a') as the_log:
        the_log.write(info.strip() + "\n")
