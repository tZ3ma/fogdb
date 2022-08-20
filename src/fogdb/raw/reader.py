# src/fogdb/raw/reader.py
"""Module providing file readers."""
import configparser

import yaml


def create_list_cfg_parser():
    """Wrap config parser creation."""
    # create a config parse able to parse lists
    list_configparser = configparser.ConfigParser(
        converters={"list": lambda x: [i.strip() for i in x.split(",")]}
    )
    return list_configparser


def config(path):
    """Read in config style data source files."""
    # recreate configparser to prevent bleed over
    print(path)
    list_configparser = create_list_cfg_parser()
    list_configparser.read(path)

    # bulk of the work
    data_map = dict(list_configparser["default"].items())

    # common names need extra parsing because they are a list
    # pylint: disable=no-member
    # the getlist is added implicitly above when creating "list_configparser"
    cnames = list_configparser.getlist("default", "common_names")
    # pylint: enable=no-member
    filtered_names = [entry for entry in cnames if entry != ""]
    data_map["common_names"] = filtered_names

    return data_map


def yml(path):
    """Read in yaml data source files."""
    with open(path, encoding="utf8") as stream:
        data = yaml.safe_load(stream)
    return data


parser = {
    "txt": config,
    "cfg": config,
    "yml": yml,
    "yaml": yml,
}
"""Known file type parsers."""
