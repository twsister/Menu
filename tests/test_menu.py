import os
from pathlib import Path
import unittest.mock
from unittest.mock import Mock
import pytest
import menu
import pyfakefs
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
    result = str(menu.stdscr.method_calls).split(',')
    result = list(map(str.strip, result))
    assert 22 == len(result)
    assert result[4] == "'Select .bat File to Run'"
    assert result[8] == "'(type to search)'"
    assert result[10] == "call.addstr(20"
    assert result[12] == "'1) test'"
    assert result[13] == "65536)"
    assert result[14] == "call.addstr(21"
    assert result[16] == "'2) XSeg - edit'"
    assert result[17] == "0)"
    assert result[18] == "call.addstr(22"
    assert result[20] == "'10) XSeg - apply'"
    assert result[21] == "0)]"


# ensure files move up and are correctly highlighted when selected changes
def test_display_bats_down_one():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    selected = 1
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split(',')
    result = list(map(str.strip, result))
    assert 22 == len(result)
    assert result[4] == "'Select .bat File to Run'"
    assert result[8] == "'(type to search)'"
    assert result[10] == "call.addstr(19"
    assert result[12] == "'1) test'"
    assert result[13] == "0)"
    assert result[14] == "call.addstr(20"
    assert result[16] == "'2) XSeg - edit'"
    assert result[17] == "65536)"
    assert result[18] == "call.addstr(21"
    assert result[20] == "'10) XSeg - apply'"
    assert result[21] == "0)]"


# ensure long file names are ok
def test_display_bats_long_names():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 80]
    all_bats = ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    selected = 1
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split(',')
    result = list(map(str.strip, result))
    assert 22 == len(result)
    assert result[4] == "'Select .bat File to Run'"
    assert result[8] == "'(type to search)'"
    assert result[10] == "call.addstr(19"
    assert result[12] == "'1) test of a really really really long file name'"
    assert result[13] == "0)"
    assert result[14] == "call.addstr(20"
    assert result[16] == "'2) XSeg - edit'"
    assert result[17] == "65536)"
    assert result[18] == "call.addstr(21"
    assert result[20] == "'10) XSeg - apply'"
    assert result[21] == "0)]"


# ensure long file names are truncated if screen is too small
def test_display_bats_truncated_long_names():
    menu.stdscr = Mock()
    menu.stdscr.getmaxyx.return_value = [40, 30]
    all_bats = ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    selected = 1
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == ['1) test of a really really really long file name', '2) XSeg - edit', '10) XSeg - apply']
    result = str(menu.stdscr.method_calls).split(',')
    result = list(map(str.strip, result))
    assert 22 == len(result)
    assert result[4] == "'Select .bat File to Run'"
    assert result[8] == "'(type to search)'"
    assert result[10] == "call.addstr(19"
    assert result[12] == "'1) test of a really really..'"
    assert result[13] == "0)"
    assert result[14] == "call.addstr(20"
    assert result[16] == "'2) XSeg - edit'"
    assert result[17] == "65536)"
    assert result[18] == "call.addstr(21"
    assert result[20] == "'10) XSeg - apply'"
    assert result[21] == "0)]"


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
    selected = 0
    search = ''
    bats = menu.display_bats(all_bats, selected, search)
    assert bats == all_bats
    result = str(menu.stdscr.method_calls).split(',')
    result = list(map(str.strip, result))
    assert 50 == len(result)
    assert result[46] == "call.addstr(19"
    assert result[48] == "'4.5) test write to bottom line last charac..'"
    assert result[49] == "0)]"


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
    result = str(menu.stdscr.method_calls).split(',')
    result = list(map(str.strip, result))
    assert 82 == len(result)
    # assert '' == result
    assert result[10] == "call.addstr(2"
    assert result[12] == "'3.1) test'"
    assert result[13] == "0)"


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
        [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)


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
    # re-run, to test appending to search
    code = curses.KEY_BACKSPACE
    [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)
    assert selected == 0
    assert search == 'j'
