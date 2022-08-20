# src/fogdb/setup.py
"""Module for setting up fogdb."""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _create_home(path="~/.fogdb"):
    """Create the fogdb home folder."""
    pth = Path(path)
    pth.mkdir(parents=True, exist_ok=True)
    return pth


def _create_db_toplevel_folder(path="~/.fogdb_databases"):
    """Create the cassandra database toplevel folder."""
    pth = Path(path)
    pth.mkdir(parents=True, exist_ok=True)
    return pth


# pylint: disable=too-few-public-methods
class Initializer:
    """Initialize the forest garden cassandra database.

    Holds the initialization details and writes them into a config file as
    specified by :paramref:`~Initializer.home` and
    :paramref:`~Initializer.conf`.

    Parameters
    ----------
    home: path, str, default="~/.fogdb.d"
        Path or string specifying FogDB's new home folder. Config files and
        future auxilliaries be located there.
    database: path, str, default="~/.fogdb_databases"
        Path or string specifying FogDB's new database folder. Database
        "objects" will be located there.
    config: str, default = "conf.cfg"
        String specifying the config file name. Holds info of home and database
        path, as well as datamodels used.
    """

    def __init__(
        self,
        home="~/.fogdb.d",
        database="~/.fogdb_databases",
        config="conf.cfg",
    ):
        # initialize home
        self.home = home
        home_p = _create_home(self.home)
        logger.debug("Initialized fogdb home in %s", home_p)

        # initialize database folder
        self.database = database
        db_p = _create_db_toplevel_folder(self.database)
        logger.debug("Initialized fogdb database in %s", db_p)

        # create config file
        self.config = config
        self.config_file_path = self.home / self.config

        _cf_lines = [
            "[default]\n",
            f"home = {self.home}\n",
            f"database = {self.database}\n",
            f"config_file_name = {self.config}\n",
            f"config_file_path = {self.config_file_path}\n",
        ]

        with open(self.config_file_path, "w", encoding="utf8") as config_file:
            config_file.writelines(_cf_lines)

            logger.debug("Succesfully create fogdb config file at")
            logger.debug("%s", self.config_file_path)


# pylint: enable=too-few-public-methods
