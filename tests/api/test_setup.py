# tests/api/test_setup.py
"""Test correct fogdb setup."""
import configparser

import pytest

# create a config parse able to parse lists
list_configparser = configparser.ConfigParser(
    converters={"list": lambda x: [i.strip() for i in x.split(",")]}
)


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        ("home", "pytest_fogdb.d"),
        ("database", "pytest_fogdb"),
        ("config_file_path", "pytest_config"),
    ],
)
def test_initialization(fogdb_init, test_input, expected):
    """Test correct fogdb initialization."""
    assert expected in str(getattr(fogdb_init, test_input))


@pytest.mark.parametrize("test_input", ["home", "database"])
def test_folder_initialization(fogdb_init, test_input):
    """Test correct folder initialization."""
    assert getattr(fogdb_init, test_input).is_dir()


def test_config_file_exists(fogdb_init):
    """Test correct config file location."""
    assert fogdb_init.config_file_path.is_file()


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        ("home", "pytest_fogdb.d"),
        ("database", "pytest_fogdb"),
        ("config_file_name", "pytest_config"),
    ],
)
def test_config_file_contents(fogdb_init, test_input, expected):
    """Test correct config file contents."""
    # read in the config file
    list_configparser.read(fogdb_init.config_file_path)
    assert expected in list_configparser["default"][test_input]
