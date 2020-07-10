import os
from pathlib import Path
import unittest
from unittest.mock import patch
import dfl_menu
import pyfakefs


class DflMenuTest(pyfakefs.fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.dfl_root = Path('/dfl')
        dfl_menu.dfl_root = self.dfl_root
        os.mkdir(self.dfl_root)

    def create(self, bat_file):
        open(self.dfl_root.joinpath(bat_file), 'a').close()

    @patch('dfl_menu.subprocess.check_output')
    def test_get_gpus_two(self, mock_subprocess):
        result = bytes("GPU 0: TITAN RTX (UUID: GPU-61b5b696-f611-9c9e-1153-1fa05d67156d)\n" +
                       "GPU 1: TITAN RTX (UUID: GPU-7911f59d-e739-702b-d23b-73536786e295)\n", 'utf-8')
        mock_subprocess.return_value = result
        gpus = dfl_menu.get_gpus()
        self.assertEqual(2, gpus)

    @patch('dfl_menu.subprocess.check_output', side_effect=FileNotFoundError())
    def test_get_gpus_except(self, mock_subprocess):
        # ensure gpus is set to zero if nvidia-smi command is not found
        gpus = dfl_menu.get_gpus()
        self.assertEqual(0, gpus)

    def test_get_bats_1(self):
        self.create('1) test.bat')
        self.create('10) test.bat')
        self.create('2) test.bat')
        bats = dfl_menu.get_bats()
        assert bats == ['1) test', '2) test', '10) test']


if __name__ == '__main__':
    unittest.main()
