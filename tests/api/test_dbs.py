# tests/api/test_dbs.py
"""Test correct fogdb database interface."""
from pathlib import Path

from fogdb import raw
from fogdb.dbs import cassy
from fogdb.raw import lcl

# path relative to project root from where the nox test session is called:
raw_data_folder = Path("tests/api/raw_data").absolute()


def test_create_model_from_raw():
    """Test raw_data -> cassy meta model."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {
                ("common_names", type([])),
                ("usda_hardiness", str),
            },
            "less_common_fruiting_trees": {
                ("common_names", type([])),
                ("usda_hardiness", int),
                ("usda_hardiness", str),
            },
        },
        "test_jacke": {
            "plant_matrix": {
                ("common_names", type([])),
                ("usda_hardiness", str),
            }
        },
    }

    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="all"))
    attributes = cassy.create_model_from_raw(rdm)
    assert attributes == expected
