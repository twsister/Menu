import sys
import subprocess
import os
import natsort
import curses
import datetime
from pathlib import Path
import BatchExecutor
from BatchLogger import log

dfl_root = Path(sys.argv[0]).absolute().parent.parent.parent
sys.path.append(dfl_root.joinpath("_internal/DeepFaceLab"))


ENV = [
    ("%WORKSPACE%", "workspace"),
    ("%PYTHON_EXECUTABLE%", "python3"),
    ("%DFL_ROOT%", str(dfl_root.joinpath("_internal/DeepFaceLab")))
]


class Screen:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.stdscr.keypad(True)
        curses.curs_set(0)

    def __enter__(self, *args):
        return self.stdscr

    def __exit__(self, *args):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.curs_set(1)
        curses.echo()
        curses.endwin()


def _get_sum():
    s = []
    model_dir = dfl_root.joinpath("workspace/model")
    for file in os.listdir(model_dir):
        if file.endswith("_summary.txt"):
            with open(model_dir + file) as f:
                s.append(f.read())
    return s


if __name__ == "__main__":
    try:
        gpus = subprocess.check_output(["nvidia-smi", "-L"]).decode().count("\n")
    except FileNotFoundError:
        gpus = 0

    sys.path.append(dfl_root.joinpath("_internal/DeepFaceLab"))
    bats = []
    for filename in os.listdir(dfl_root):
        if filename.endswith(".bat"):
            bats.append(filename[:-4])

    all_bats = natsort.natsorted(bats)

    bats = all_bats.copy()

    selected = 0

    search = ""

    while True:
        with Screen() as stdscr:
            stdscr.erase()

            dims = stdscr.getmaxyx()

            centerX = int(dims[1] / 2)
            centerY = int(dims[0] / 2)

            code = -0
            while True:
                key = curses.keyname(code).decode()
                if code == 10 or code == 343:
                    break
                elif code == 27:
                    exit(0)
                elif code == curses.KEY_DOWN and selected < len(bats) - 1:
                    selected += 1
                elif code == curses.KEY_UP and selected > 0:
                    selected -= 1
                elif key.lower() in "abcdefghijklmnopqrstuvwxyz.-()_ 1234567890" and len(search) < dims[1] - 1:
                    search += key
                    selected = 0
                elif key == "^?" or key == "KEY_BACKSPACE":
                    search = search[:-1]
                    selected = 0
                bats = [bat for bat in all_bats.copy() if search.lower() in bat.lower()]
                stdscr.erase()
                stdscr.addstr(1, 1, "Select .bat File to Run", curses.A_BOLD | curses.A_UNDERLINE)
                for x in range(0, len(bats)):
                    value = x - selected + centerY
                    if 0 <= value < dims[0]:
                        if x == selected:
                            style = curses.A_STANDOUT
                        else:
                            style = curses.A_NORMAL
                        stdscr.addstr(value, 0, bats[x].ljust(dims[1] - 1), style)
                stdscr.addstr(dims[0] - 1, dims[1] - 1 - len(search), search, curses.A_BOLD)
                code = stdscr.getch()
        with open(str(dfl_root.joinpath(bats[selected])) + '.bat') as the_file:
            print("\n\nRunning selection:", bats[selected], '\n')
            log("Running: " + str(bats[selected]))
            sums = _get_sum()
            start = datetime.datetime.now()
            try:
                BatchExecutor.process(ENV, the_file.read().strip())
            except KeyboardInterrupt:
                log("KeyboardInterrupt")
            end = datetime.datetime.now()
            new_sums = _get_sum()
            for entry in new_sums:
                if entry not in sums:
                    append(entry)
            delta = end - start
            log("Finished after {} GPU hours ({})".format(delta * gpus, delta))
