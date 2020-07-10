import os
from pathlib import Path
import unittest
import menu
import pyfakefs


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


if __name__ == '__main__':
    unittest.main()
