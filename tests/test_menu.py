import os
from pathlib import Path
import unittest
import pytest
import menu
import pyfakefs
import curses




class DflMenuTest(pyfakefs.fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.dfl_root = Path('/dfl')
        menu.dfl_root = self.dfl_root
        os.mkdir(self.dfl_root)

    def create(self, bat_file):
        open(self.dfl_root.joinpath(bat_file), 'a').close()

    def test_get_bats(self):
        self.create('1) test.bat')
        self.create('10) test.bat')
        self.create('2) test.bat')
        bats = menu.get_bats()
        assert bats == ['1) test', '2) test', '10) test']

    def test_decode_keys_enter(self):
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

    def test_decode_keys_esc(self):
        curses.initscr()
        selected = 3
        search = ''
        len_all_bats = 5
        code = 27
        with pytest.raises(SystemExit):
            [selected, search] = menu.decode_keys(code, selected, search, len_all_bats)

    def test_decode_keys_down(self):
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

    def test_decode_keys_up(self):
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

    def test_decode_keys_search(self):
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

    def test_decode_keys_backspace(self):
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




if __name__ == '__main__':
    unittest.main()
