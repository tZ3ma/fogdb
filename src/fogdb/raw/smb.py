# src/fogdb/raw/smb.py
"""Module a handler class for  mapping locally stored raw data."""
import os
import tempfile
import urllib

from smb.SMBHandler import SMBHandler

from . import BaseHandler
from .reader import parser


# on pylint:
# pylint: disable=too-many-arguments
# 3 argumetns passed on to parent class. 7-3 = 4 ;)
# honestly, this is an api interface so imho, 7 args is ok.
# on pytest:
# this module was tested successfully on my local machine.
# Until now however, i have not figured out, how to set up a samba network drive
# on a CI-Environment like github.
# Help would be greatly appreciated.
class Handler(BaseHandler):  # pragma: no cover
    """Handle data mapping for locally stored raw data.

    Parameters
    ----------
    connection
        `pysmb ConnectionClass instance
        <https://pysmb.readthedocs.io/en/latest/api/smb_SMBConnection.html>`_
        providing the samba shared network connection under the label of
        :paramref:`sharename`.

        This is usually something like::

           from smb.SMBConnection import SMBConnection
            conn = SMBConnection(
                username="MyUserName",
                password="MyPassword",
                my_name="",
                remote_name="192.168.178.1",
            )

    sharename: str
        String labeling the samba shared network service, provided by the
        :paramref:`connection`.

        For a ``Fritz!Box``, this usually is::

            "fritz.nas"

    top_level_folder: str
        String specifying the name of the toplevel folder where the raw
        data is found.

    categories: str, list, default="all"
        String or list of strings specifying which categories (i.e. sublevel
        folders) are used for reading in the data. If ``"all"`` is used, all
        sublevel folders are traversed.

        Can be something like ``"crawford"``, ``"jacke"``,
        ``"myRand0mSUBf0lder"``, ...

    dtype: str, default="txt"
        String specifying the data type of the raw datafiles. If ``"all"``
        is used, data type is not filtered.

        Can be something like ``"rst"``, ``"cfg"``, ...

    excl_dirs: ~collections.abc.Container
        Container of strings specifying folder names to excluded during the
        mapping.
    """

    def __init__(
        self,
        connection,
        sharename,
        top_level_folder,
        categories="all",
        dtype="txt",
        excl_dirs=("FRITZ",),
    ):
        self.connection = connection
        self.sharename = sharename
        self.tlf = top_level_folder

        super().__init__(
            categories=categories,
            dtype=dtype,
            excl_dirs=excl_dirs,
        )

    # pylint: disable=too-many-locals
    # imho constructing the smb-string is way better this way
    # so im gonna be a little liberal with the amount of locals in this one
    def map_source_file_data(self, relative_file_path):
        """Return source file data mappings."""
        uname = self.connection.username
        pwd = self.connection.password
        host = self.connection.remote_name
        sharename = self.sharename
        top = self.tlf
        path = relative_file_path

        conn_string = f"smb://{uname}:{pwd}@{host}/{sharename}/{top}/{path}"

        opener = urllib.request.build_opener(SMBHandler)
        file_handler = opener.open(conn_string)
        data = file_handler.read()
        file_handler.close()

        with tempfile.NamedTemporaryFile() as tmp:

            # Open the file for writing.
            with open(tmp.name, "w", encoding="utf-8") as fle:
                fle.write(data.decode("utf-8"))

            # infer file type
            dtype = self._infer_file_type(relative_file_path)
            parsed_data = parser[dtype](tmp.name)

        return parsed_data

    # pylint: enable=too-many-locals

    def _list_top_level_folders(self, relative_file_path):
        """Return alphabetically sorted list of folder names found in path."""
        _excl = [".", "..", *self.exclude]
        folders = [
            name.filename
            for name in self.connection.listPath(
                self.sharename, os.path.join(self.tlf, relative_file_path)
            )
            if name.isDirectory and name.filename not in _excl
        ]
        sorted_folders = list(sorted(folders))

        return sorted_folders

    def _list_files(self, relative_file_path):
        """Return alphabetically sorted list of file names found in path."""
        found_files = [
            found.filename
            for found in self.connection.listPath(
                self.sharename, os.path.join(self.tlf, relative_file_path)
            )
            if not found.isDirectory
        ]

        return self._sort_and_filter_file_list(found_files)

    # pylint: enable=too-many-arguments
