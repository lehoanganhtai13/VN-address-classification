import os
import json
import importlib
import pytest
import sys

current_directory = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_directory, '..', 'src')))
from run import Solution

@pytest.fixture()
def solution():
    return Solution()

test_cases_directory = os.path.abspath(os.path.join(current_directory, 'test_cases'))
@pytest.fixture()
def test_cases():
    test_file_path = os.path.join(test_cases_directory, 'public.json')
    with open(test_file_path, 'r') as test_file:
        data = json.load(test_file)
        return data
