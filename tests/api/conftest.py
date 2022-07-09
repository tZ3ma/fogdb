# tests/api/conftest.py
"""Configure fogdb test suite."""
import pytest

from fogdb.setup import Initializer


@pytest.fixture(scope="session")
def fogdb_init(tmp_path_factory):
    """Initialize fogdb on a temp directory."""
    home = tmp_path_factory.mktemp("pytest_fogdb.d")
    database = tmp_path_factory.mktemp("pytest_fogdb")
    config = "pytest_config"

    inizialized_fogdb = Initializer(
        home=home,
        database=database,
        config=config,
    )

    return inizialized_fogdb
