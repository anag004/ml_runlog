import pytest
import pandas as pd
from ml_runlog import MLRunlog
import os
import random

# Constants for testing
CREDENTIALS_PATH = os.path.expanduser("~") + "/creds.json"  # Ensure this is the path to your service account credentials
TEST_SHEET_NAME = 'mlrunlog-integration-test'  # Assumes this sheet has header [sno, col1, col2, col3] and all other rows empty

def generate_random_words_from_linux_dict(num_words=1):
    dict_file = '/usr/share/dict/words'  # Common path; might vary

    try:
        with open(dict_file, 'r') as file:
            words = file.read().splitlines()
        return random.choices(words, k=num_words)
    except FileNotFoundError:
        print("The dictionary file was not found.")
        return []

def generate_random_row():
    return {
        "col1": " ".join(generate_random_words_from_linux_dict(num_words=5)), 
        "col2": random.randint(0, 100), 
        "col3": bool(random.randint(0, 1))
    }

@pytest.fixture(scope="module")
def runlog():
    # Setup the MLRunlog instance for tests
    return MLRunlog(CREDENTIALS_PATH, TEST_SHEET_NAME)

def test_get_sno(runlog):
    """
    Test getting the serial number reflects the actual number of rows in the sheet.
    """
    initial_sno = runlog.get_sno()
    # Assuming the sheet is empty initially, or you know the initial row count.
    assert int(initial_sno) == 1  # Adjust according to the initial expected value

def test_allocate_and_log_data(runlog):
    """
    Test allocating serial numbers and logging data.
    """

    num_trials = 3 

    for _ in range(num_trials):
        initial_sno = runlog.get_sno()
        data_to_log = [generate_random_row() for _ in range(5)]
        allocated_sno = runlog.allocate_sno(len(data_to_log))

        # Check if SNO was allocated correctly
        assert allocated_sno == list(range(initial_sno, initial_sno + len(data_to_log)))

        # Log the data and verify
        runlog.log_data(data_to_log, sno=initial_sno, verify_timeout=10, verify_col_idx=0)
        new_sno = runlog.get_sno()
        assert new_sno == initial_sno + len(data_to_log)

    for _ in range(num_trials):
        max_sno = runlog.get_sno()
        initial_sno = random.randint(1, max_sno) 
        data_to_log = [generate_random_row() for _ in range(5)]
        allocated_sno = runlog.allocate_sno(len(data_to_log), sno=initial_sno)

        # Check if SNO was allocated correctly
        assert allocated_sno == list(range(initial_sno, initial_sno + len(data_to_log)))

        # Log the data and verify
        runlog.log_data(data_to_log, sno=initial_sno, verify_timeout=10, verify_col_idx=0)
        new_sno = runlog.get_sno()
        assert new_sno == max(max_sno, initial_sno + len(data_to_log))  

@pytest.fixture(scope="module", autouse=True)
def cleanup(runlog):
    """
    Cleanup the test sheet after tests are done.
    """
    
    runlog.clear_sheet()
