# src/fogdb/raw/lcl.py
"""Module a handler class for  mapping locally stored raw data."""
import os
from pathlib import Path

from . import BaseHandler
from .reader import parser


class Handler(BaseHandler):
    """Handle data mapping for locally stored raw data.

    Parameters
    ----------
    top_level_folder: str, pathlib.Path
        String/Path specifying the path of the toplevel folder where the raw
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
        self, top_level_folder, categories="all", dtype="txt", excl_dirs=("FRITZ",)
    ):
        self.tlf = Path(top_level_folder)

        super().__init__(
            categories=categories,
            dtype=dtype,
            excl_dirs=excl_dirs,
        )

    def map_source_file_data(self, relative_file_path):
        """Return source file data mappings."""
        # infer file type
        dtype = self._infer_file_type(relative_file_path)

        return parser[dtype](self.tlf / relative_file_path)

    def _list_top_level_folders(self, relative_file_path):
        """Return alphabetically sorted list of folder names found in relative file path."""
        folders = [
            fold.name
            for fold in os.scandir(self.tlf / relative_file_path)
            if fold.is_dir() and fold.name not in self.exclude
        ]
        sorted_folders = list(sorted(folders))

        return sorted_folders

    def _list_files(self, relative_file_path):
        """Return sorted list of file names found in self.tlf/folder."""
        found_files = [
            found.name
            for found in os.scandir(self.tlf / relative_file_path)
            if found.is_file()
        ]

        return self._sort_and_filter_file_list(found_files)
