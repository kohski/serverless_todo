import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(
    os.path.abspath(__file__)) + "/../../src/task/"))


DEFAULT_TIME = '2021-03-04T15:00:00'

@pytest.fixture(autouse=True)
@pytest.mark.freeze_time
def set_time(freezer):
    freezer.move_to(DEFAULT_TIME)

