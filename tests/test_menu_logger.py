from unittest.mock import patch
import menu_logger


@patch('menu_logger.subprocess.check_output')
def test_get_gpus_2(mock_subprocess):
    # nvidia-smi generates these results & get_gpus() counts the lines
    result = bytes("GPU 0: TITAN RTX (UUID: GPU-61b5b696-f611-9c9e-1153-1fa05d67156d)\n" +
                   "GPU 1: TITAN RTX (UUID: GPU-7911f59d-e739-702b-d23b-73536786e295)\n", 'utf-8')
    mock_subprocess.return_value = result
    gpus = menu_logger.get_gpus()
    assert 2 == gpus


@patch('menu_logger.subprocess.check_output', side_effect=FileNotFoundError())
def test_get_gpus_except(mock_subprocess):
    # ensure gpus is set to zero if nvidia-smi command is not found
    gpus = menu_logger.get_gpus()
    assert 0 == gpus
