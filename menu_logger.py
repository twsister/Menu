import time
import os
import subprocess
import datetime
# from dfl_menu import dfl_root


def log(info):
    with open("log.txt", 'a+') as the_log:
        the_log.write("{}:\n".format(datetime.datetime.now()))
        the_log.write(info.strip() + "\n")


def append(info):
    with open("log.txt", 'a') as the_log:
        the_log.write(info.strip() + "\n")

#
# def get_sum():
#     s = []
#     model_dir = dfl_root.joinpath("workspace/model")
#     for file in os.listdir(model_dir):
#         if file.endswith("_summary.txt"):
#             with open(model_dir + file) as f:
#                 s.append(f.read())
#     return s


# count the number of NVIDIA GPUs found
def get_gpus():
    try:
        return subprocess.check_output(["nvidia-smi", "-L"]).decode().count("\n")
    except FileNotFoundError:
        return 0


def update_stats():
    end = datetime.datetime.now()
    new_sums = _get_sum()
    for entry in new_sums:
        if entry not in sums:
            append(entry)
    delta = end - start
    log("Finished after {} GPU hours ({})".format(delta * get_gpus(), delta))
