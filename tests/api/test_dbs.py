# tests/api/test_dbs.py
"""Test correct fogdb database interface."""
import os
from pathlib import Path

import pytest

from fogdb import raw
from fogdb.dbs import cassy
from fogdb.raw import lcl

# path relative to project root from where the nox test session is called:
raw_data_folder = Path("tests/api/raw_data").absolute()


@pytest.mark.parametrize(
    ("test_case", "expected"),
    [
        (str, "Text"),
        (int, "Integer"),
        (type(True), "Boolean"),
        (type({}), "Map"),
        (type([]), "List"),
    ],
)
def test_data_type_mapping(test_case, expected):
    """Test python -> cassandra data type mapping."""
    assert cassy.dtypes[test_case] == expected


def test_map_model_attributes():
    """Test raw_data -> cassandra table attributes."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {
                ("latin", "Text"),
                ("common_names", "List"),
                ("usda_hardiness", "Text"),
            },
            "less_common_fruiting_trees": {
                ("latin", "Text"),
                ("common_names", "List"),
                ("usda_hardiness", "Integer"),
                ("usda_hardiness", "Text"),
            },
        },
        "test_jacke": {
            "plant_matrix": {
                ("latin", "Text"),
                ("common_names", "List"),
                ("usda_hardiness", "Text"),
            }
        },
    }

    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="all"))
    attributes = cassy.map_model_attributes(rdm)
    assert attributes == expected


def test_hardcode_model(fogdb_init):
    """Test raw_data_map -> hardcoded model."""
    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="all"))
    locations = cassy.hardcode_datamodel_from_raw(
        raw_data_map=rdm,
        path=os.path.join(fogdb_init.home, "db_data_models", "cassy"),
        primary_keys=("latin",),
        clustering_keys=None,
        config=fogdb_init.config,
        overwrite=True,
        backup=True,
    )

    expected_categories = ["test_crawford", "test_jacke"]
    assert list(locations.keys()) == expected_categories

    expected_subcategories = [
        "common_fruiting_trees",
        "less_common_fruiting_trees",
        "plant_matrix",
    ]

    nested_subcats = [list(entry.keys()) for entry in locations.values()]
    subcats = [item for lst in nested_subcats for item in lst]

    assert subcats == expected_subcategories

    for cat in locations:
        for subcat in locations[cat]:
            assert Path(locations[cat][subcat]).is_file()


def test_hardcode_model_with_clustering_keys(fogdb_init):
    """Test raw_data_map -> hardcoded model."""
    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="all"))
    locations = cassy.hardcode_datamodel_from_raw(
        raw_data_map=rdm,
        path=os.path.join(fogdb_init.home, "db_data_models", "cassy"),
        primary_keys=("latin",),
        clustering_keys=(("common_names", "ASC"),),
        config=fogdb_init.config,
        overwrite=True,
        backup=True,
    )

    expected_categories = ["test_crawford", "test_jacke"]
    assert list(locations.keys()) == expected_categories

    expected_subcategories = [
        "common_fruiting_trees",
        "less_common_fruiting_trees",
        "plant_matrix",
    ]

    nested_subcats = [list(entry.keys()) for entry in locations.values()]
    subcats = [item for lst in nested_subcats for item in lst]

    assert subcats == expected_subcategories

    for cat in locations:
        for subcat in locations[cat]:
            assert Path(locations[cat][subcat]).is_file()


@pytest.mark.parametrize(
    ("test_case", "expected"),
    [
        ([("attr1", "Text"), ("attr1", "Integer")], {"attr1": "Text"}),
        ([("attr2", "Map"), ("attr2", "Text")], {"attr2": "Text"}),
    ],
)
# pylint: disable=protected-access
def test_parse_column_tuples_to_dict(test_case, expected):
    """Test both existing if clauses."""
    assert cassy._parse_column_tuples_to_dict(test_case) == expected


# pylint: enable=protected-access
