import sys
import os
import natsort
import curses
import menu_runner
from pathlib import Path
from menu_logger import log

# set dfl_root to location of .bat files
# this assumes that menu.py lives in <dfl_root>/_internal/Menu/
dfl_root = Path(sys.argv[0]).absolute().parent.parent.parent
sys.path.append(dfl_root.joinpath("_internal/DeepFaceLab"))

# these map to the variables inside the .bat files
ENV = [
    ("%WORKSPACE%", str(dfl_root.joinpath("workspace"))),
    ("%PYTHON_EXECUTABLE%", "python3"),
    ("%DFL_ROOT%", str(dfl_root.joinpath("_internal/DeepFaceLab")))
]


# simple screen to display the menu
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


# create a list of .bat files
def get_bats():
    result_bats = []
    for filename in os.listdir(dfl_root):
        if filename.endswith(".bat"):
            result_bats.append(filename[:-4])
    # sort to get 10 after 9
    return natsort.natsorted(result_bats)


# takes keyboard input and returns the file selected and search string
def decode_keys(code, selected, search, len_bats):
    key = curses.keyname(code).decode()
    if code == 10 or code == 343:
        # ENTER - run the selected batch file
        # X in position 0 is a flag
        search = 'X' + search
    elif code == 27:
        # ESC - exit the menu
        raise SystemExit
    elif code == curses.KEY_DOWN and selected < len_bats - 1:
        selected += 1
    elif code == curses.KEY_UP and selected > 0:
        selected -= 1
    elif key.lower() in "abcdefghijklmnopqrstuvwxyz.-()_ 1234567890":
        # searching, so reposition the cursor
        search += key.lower()
        selected = 0
    elif key == "^?" or key == "KEY_BACKSPACE":
        # searching, so reposition the cursor
        search = search[:-1]
        selected = 0
    return [selected, search]


def display_bats(all_bats, selected, search, stdscr):
    height, width = stdscr.getmaxyx()
    center_y = int(height / 2)
    terms = search.split(' ')
    bats = [bat for bat in all_bats.copy() if all(x in bat.lower() for x in terms)]
    stdscr.erase()
    stdscr.addstr(1, 1, "Select .bat File to Run", curses.A_BOLD | curses.A_UNDERLINE)
    if len(search) > 0:
        stdscr.addstr(1, 25, search, curses.A_NORMAL)
    else:
        stdscr.addstr(1, 25, "(type to search)", curses.A_NORMAL)
    for x in range(0, len(bats)):

        value = x - selected + center_y
        if 2 <= value < height:
            if x == selected:
                style = curses.A_STANDOUT
            else:
                style = curses.A_NORMAL
            file_name = bats[x]
            display_name = file_name[:width - 4] + '..' if len(file_name) > width - 2 else file_name
            stdscr.addstr(value, 1, display_name, style)
    return bats


def exec_bat_file(bats, selected):
    with open(str(dfl_root.joinpath(bats[selected])) + '.bat') as the_file:
        print("\n\nRunning selection:", bats[selected], '\n')
        log("Running: " + str(bats[selected]))
        try:
            menu_runner.process(ENV, the_file.read().strip())
        except KeyboardInterrupt:
            log("KeyboardInterrupt")


def get_selected_file(all_bats, selected, search, stdscr):
    while len(search) == 0 or search[0] != 'X':
        bats = display_bats(all_bats, selected, search, stdscr)
        code = stdscr.getch()
        [selected, search] = decode_keys(code, selected, search, len(bats))
    search = search[1:]
    return [selected, search, bats]


def run_menu():
    selected = 0
    search = ""
    while True:
        with Screen() as stdscr:
            stdscr.erase()
            all_bats = get_bats()
            bats = all_bats.copy()
            [selected, search, bats] = get_selected_file(all_bats, selected, search, stdscr)
        # sums = get_sum()
        # start = datetime.datetime.now()
        exec_bat_file(bats, selected)
        # update_stats(start, sums)


if __name__ == "__main__":
    run_menu()
