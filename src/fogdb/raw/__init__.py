# src/fogdb/raw/__init__.py
"""Module providing raw data parsing capabilities."""
import abc
import os
from collections import defaultdict


def to_dict(handler):
    """Read in raw data.

    Parameters
    ----------
    handler
        Handler class providing key interfacing capabilities. See
        :mod:`fogdb.raw.lcl` or :mod:`fogdb.raw.smb` for examples.

    Returns
    -------
    tuple
        Tuple of quadruple nested dicts holding the data keyed by subcategory,
        keyed by filename - ending, keyed by (found)
        :paramref:`~read_raw.categories` as in::

            returned_tuple = (
                {
                    "crawford": {  # category
                        "common_fruiting_trees": {  # subcategory
                            "Cydonia_oblonga": {  # filename - ending
                                "common_names": "Quince",
                                "USDA_hardiness": 4,
                                # ...,
                            },
                        },
                        "less_common_fruiting_trees": {  # another subcategory
                            "Armelancher_canadensis": {  # filename - ending
                                "common_names": "Juneberry",
                                "USDA_hardiness": 4,
                                # ...,
                            },
                        },
                    },
                },
                {
                    "jacke": {  # another category
                        "plant_matrix": {  # source specific subcategory
                            "Cydonia_oblonga": {  # filename - ending
                                "common_names": "Quince",
                                "USDA_hardiness": 4,
                                # ...,
                            },
                        },
                    },
                },
            )
    """
    # create a file tree of path
    tree = handler.map_raw_data_file_tree()

    # reuse tree dict, cause only the lowest level data change
    raw_data_map = tree.copy()

    for cat, subcats in tree.items():
        for subcat, files in subcats.items():
            raw_data_map[cat][subcat] = {}
            for fle in files:
                # rile reading is handled by file specific parsers
                raw_data_map[cat][subcat][
                    fle.split(".")[0]
                ] = handler.map_source_file_data(os.path.join(cat, subcat, fle))

    return raw_data_map


# pylint: disable=too-few-public-methods
# the BaseHandler provides only one public methods, but a bun of key privates
class BaseHandler:
    """Partly abstract Handler base class for mapping raw data.

    Parameters
    ----------
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

    def __init__(self, categories="all", dtype="txt", excl_dirs=("FRITZ",)):
        self.categories = categories
        self.dtype = dtype
        self.exclude = excl_dirs

    def map_raw_data_file_tree(self):
        """Return mapped file tree of the expected :ref:`raw_data` strucure."""
        cats = self._list_top_level_folders(relative_file_path=".")
        if self.categories != "all":
            cats = [cat for cat in cats if cat in self.categories]

        cat_subcat_map = {
            cat: self._list_top_level_folders(relative_file_path=os.path.join(".", cat))
            for cat in cats
        }

        file_tree = defaultdict(dict)
        for cat, subcats in cat_subcat_map.items():
            for subcat in subcats:
                file_tree[cat][subcat] = []
                for filename in self._list_files(
                    relative_file_path=os.path.join(".", cat, subcat)
                ):
                    file_tree[cat][subcat].append(filename)

        return dict(file_tree)

    @abc.abstractmethod
    def _list_files(self, relative_file_path):
        """Return sorted and filtered list of file names found in relative_file_path."""

    @abc.abstractmethod
    def _list_top_level_folders(self, relative_file_path):
        """Return alphabetically sorted list of folder names found in relative_file_path."""

    def _sort_and_filter_file_list(self, file_list):

        sorted_files = sorted(file_list)
        if self.dtype != "all":
            filtered_files = [
                fle for fle in sorted_files if fle.split(".")[-1] == self.dtype
            ]
        else:
            filtered_files = sorted_files

        return filtered_files

    def _infer_file_type(self, file_string):
        return str(file_string).rsplit(".", maxsplit=1)[-1]


# pylint: enable=too-few-public-methods
