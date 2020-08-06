from pathlib import Path
from unittest.mock import Mock
import pytest
import menu
import curses


# ensure only bat files are read
def test_get_bats(fs):
    dfl_root = Path('/dfl')
    menu.dfl_root = dfl_root
    fs.create_file(dfl_root.joinpath('1) test.bat'))
    fs.create_file(dfl_root.joinpath('10) test.bat'))
    fs.create_file(dfl_root.joinpath('2) test.bat'))
    fs.create_file(dfl_root.joinpath('5) not_a_bat.txt'))
    bats = menu.get_bats()
    assert bats == ['1) test', '2) test', '10) test']


# ensure '2)' displays before '10)'
def test_display_bats_sorted():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    selected = 0
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test', '2) XSeg - edit', '10) XSeg - apply']


# test searching a single word
def test_display_bats_search_word():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    selected = 0
    search = 'xs'
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['2) XSeg - edit', '10) XSeg - apply']


# test searching for multiple words
def test_display_bats_search_multiple_words():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    selected = 0
    search = 'xs ed'
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['2) XSeg - edit']


# ensure default display is correct
def test_display_bats_text():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    selected = 0
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 8
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, '(type to search)', 0),"
    assert result[5] == "addstr(20, 1, '1) test', 65536),"
    assert result[6] == "addstr(21, 1, '2) XSeg - edit', 0),"
    assert result[7] == "addstr(22, 1, '10) XSeg - apply', 0)]"


# ensure files move up and are correctly highlighted when selected changes
def test_display_bats_down_one():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    selected = 1
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 8
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, '(type to search)', 0),"
    assert result[5] == "addstr(19, 1, '1) test', 0),"
    assert result[6] == "addstr(20, 1, '2) XSeg - edit', 65536),"
    assert result[7] == "addstr(21, 1, '10) XSeg - apply', 0)]"


# ensure long file names are ok
def test_display_bats_long_names():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    selected = 1
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 8
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, '(type to search)', 0),"
    assert result[5] == "addstr(19, 1, '1) test of a really really really long file name', 0),"
    assert result[6] == "addstr(20, 1, '2) XSeg - edit', 65536),"
    assert result[7] == "addstr(21, 1, '10) XSeg - apply', 0)]"


# ensure long file names are truncated if screen is too small
def test_display_bats_truncated_long_names():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 30]
    all_bats = ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    selected = 1
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 8
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, '(type to search)', 0),"
    assert result[5] == "addstr(19, 1, '1) test of a really really..', 0),"
    assert result[6] == "addstr(20, 1, '2) XSeg - edit', 65536),"
    assert result[7] == "addstr(21, 1, '10) XSeg - apply', 0)]"


# fix known curses error when printing to last character of bottom row
def test_display_bats_curses_error():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [20, 46]
    all_bats = [
        '1) test of a really really really long file name',
        '2) XSeg - edit',
        '3.1) test',
        '3.2) test',
        '3.3) test',
        '4.1) test of another really really really long file name',
        '4.2) test of yet another really really really long file name',
        '4.3) test of a really really really long file name',
        '4.4) test of a really really really long file name',
        '4.5) test write to bottom line last character',
        '4.6) test of a really really really long file name'
    ]
    selected = 0
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == all_bats
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 15
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, '(type to search)', 0),"
    assert result[5] == "addstr(10, 1, '1) test of a really really really long fil..', 65536),"
    assert result[6] == "addstr(11, 1, '2) XSeg - edit', 0),"
    assert result[7] == "addstr(12, 1, '3.1) test', 0),"
    assert result[8] == "addstr(13, 1, '3.2) test', 0),"
    assert result[9] == "addstr(14, 1, '3.3) test', 0),"
    assert result[10] == "addstr(15, 1, '4.1) test of another really really really ..', 0),"
    assert result[11] == "addstr(16, 1, '4.2) test of yet another really really rea..', 0),"
    assert result[12] == "addstr(17, 1, '4.3) test of a really really really long f..', 0),"
    assert result[13] == "addstr(18, 1, '4.4) test of a really really really long f..', 0),"
    assert result[14] == "addstr(19, 1, '4.5) test write to bottom line last charac..', 0)]"


# ensure top line is not over written
def test_display_bats_top_line_bug():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [20, 40]
    all_bats = [
        '1) test of a really really really long file name',
        '2) XSeg - edit',
        '3.1) test',
        '3.2) test',
        '3.3) test',
        '4.1) test of another really really really long file name',
        '4.2) test of yet another really really really long file name',
        '4.3) test of a really really really long file name',
        '4.4) test of a really really really long file name',
        '4.5) test write to bottom line last character',
        '4.6) test of a really really really long file name',
        '4.7) test of a really really really long file name',
        '4.8) test of a really really really long file name',
        '4.9) test of a really really really long file name',
        '5) test',
        '6.1) test',
        '6.2) test',
        '6.3) test',
        '6.4) test',
        '6.5) test',
        '6.6) test',
        '6.7) test',
        '7) test',
        '8) test',
        '9) test',
        '10) XSeg - apply'
    ]
    selected = 10
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == all_bats
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 23
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, '(type to search)', 0),"
    assert result[5] == "addstr(2, 1, '3.1) test', 0),"
    assert result[6] == "addstr(3, 1, '3.2) test', 0),"
    assert result[7] == "addstr(4, 1, '3.3) test', 0),"
    assert result[8] == "addstr(5, 1, '4.1) test of another really really r..', 0),"
    assert result[9] == "addstr(6, 1, '4.2) test of yet another really real..', 0),"
    assert result[10] == "addstr(7, 1, '4.3) test of a really really really ..', 0),"
    assert result[11] == "addstr(8, 1, '4.4) test of a really really really ..', 0),"
    assert result[12] == "addstr(9, 1, '4.5) test write to bottom line last ..', 0),"
    assert result[13] == "addstr(10, 1, '4.6) test of a really really really ..', 65536),"
    assert result[14] == "addstr(11, 1, '4.7) test of a really really really ..', 0),"
    assert result[15] == "addstr(12, 1, '4.8) test of a really really really ..', 0),"
    assert result[16] == "addstr(13, 1, '4.9) test of a really really really ..', 0),"
    assert result[17] == "addstr(14, 1, '5) test', 0),"
    assert result[18] == "addstr(15, 1, '6.1) test', 0),"
    assert result[19] == "addstr(16, 1, '6.2) test', 0),"
    assert result[20] == "addstr(17, 1, '6.3) test', 0),"
    assert result[21] == "addstr(18, 1, '6.4) test', 0),"
    assert result[22] == "addstr(19, 1, '6.5) test', 0)]"


# ensure cursor doesn't go below the bottom of the list of bats
def test_display_bats_cursor_disappears_bug():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [20, 40]
    all_bats = [
        '1) test',
        '2) test',
        '3) test',
        '4) test',
        '5) test'
    ]
    curses.initscr()
    selected = 0
    search = '4'
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['4) test']
    code = curses.KEY_DOWN
    search = '4'
    [selected, search] = menu.decode_keys(code, selected, search, len(bats))
    assert search == '4'
    assert selected == 0
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['4) test']
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 11
    assert result[10] == "addstr(10, 1, '4) test', 65536)]"


# ensure searching for garbage results in the empty set of files
def test_display_bats_nothing_found():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [20, 40]
    all_bats = [
        '1) test',
        '2) test',
        '3) test',
        '4) test',
        '5) test'
    ]
    curses.initscr()
    selected = 0
    search = 'q'
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == []
    result = str(menu.stdscr.method_calls).split('call.')
    result = list(map(str.strip, result))
    assert len(result) == 5
    assert result[3] == "addstr(1, 1, 'Select .bat File to Run', 2228224),"
    assert result[4] == "addstr(1, 25, 'q', 0)]"


def test_decode_keys_enter():
    curses.initscr()
    selected = 3
    search = ''
    len_all_bats = 5
    code = 10
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 3
    assert search == 'X'
    code = 343
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 3
    assert search == 'X'


def test_decode_keys_esc():
    curses.initscr()
    selected = 3
    search = ''
    len_all_bats = 5
    code = 27
    with pytest.raises(SystemExit):
        menu.decode_keys(code, selected, search, len_all_bats)


def test_decode_keys_down():
    curses.initscr()
    selected = 3
    search = ''
    len_all_bats = 5
    code = curses.KEY_DOWN
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 4
    assert search == ''
    # re-run, this time selected should not change (bottom of list)
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 4
    assert search == ''


def test_decode_keys_up():
    curses.initscr()
    selected = 3
    search = ''
    len_all_bats = 5
    code = curses.KEY_UP
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 2
    assert search == ''
    # re-run, this time selected should not change (top of list)
    selected = 0
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 0
    assert search == ''


def test_decode_keys_search():
    curses.initscr()
    selected = 3
    search = ''
    len_all_bats = 5
    code = ord('J')
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 0
    assert search == 'j'
    # re-run, to test appending to search
    code = ord('G')
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 0
    assert search == 'jg'


def test_decode_keys_backspace():
    curses.initscr()
    selected = 3
    search = 'jon'
    len_all_bats = 5
    code = curses.KEY_BACKSPACE
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 0
    assert search == 'jo'
    # re-run, to test erasing from search
    code = curses.KEY_BACKSPACE
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 0
    assert search == 'j'
