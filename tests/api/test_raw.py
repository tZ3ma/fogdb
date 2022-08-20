# tests/api/test_raw.py
"""Test correct fogdb raw data input reading."""
from pathlib import Path

import pytest

from fogdb import raw
from fogdb.raw import lcl, smb

# path relative to project root from where the nox test session is called:
raw_data_folder = Path("tests/api/raw_data").absolute()


def test_raw_data_forlder():
    """Test raw data folder existence."""
    assert raw_data_folder.is_dir()


def test_default_to_dict_categories():
    """Test default usage of raw.to_dict."""
    raw_data_map = raw.to_dict(lcl.Handler(raw_data_folder))

    exp_keys = ["test_jacke", "test_crawford"]
    assert sorted(exp_keys) == sorted(raw_data_map.keys())


@pytest.mark.parametrize("expected", ["Arbutus_unedo", "Asimina_triloba"])
def test_default_to_dict_no_cfg_and_no_yml(expected):
    """Test default usage of raw.to_dict not parsing yml and cfg."""
    rdm = raw.to_dict(lcl.Handler(raw_data_folder))

    assert expected not in rdm["test_crawford"]["less_common_fruiting_trees"]


def test_to_dict_categories():
    """Test raw.to_dict correctly using 'categories' argument."""
    rdm = raw.to_dict(lcl.Handler(raw_data_folder, categories="test_crawford"))
    assert "test_crawford" in rdm
    assert "test_jacke" not in rdm


def test_to_dict_dtype_yml():
    """Test raw.to_dict correctly using dtype="yml"."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {},
            "less_common_fruiting_trees": {
                "Asimina_triloba": {
                    "common_names": ["PawPaw", "Pawpaw"],
                    "USDA_hardiness": 5,
                }
            },
        },
        "test_jacke": {"plant_matrix": {}},
    }
    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="yml"))
    assert rdm == expected


def test_to_dict_dtype_yaml():
    """Test raw.to_dict correctly using dtype="yaml"."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {},
            "less_common_fruiting_trees": {},
        },
        "test_jacke": {"plant_matrix": {}},
    }

    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="yaml"))
    assert rdm == expected


def test_to_dict_dtype_txt():
    """Test raw.to_dict correctly using dtype="txt"."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {
                "Cydonia_oblonga": {"common_names": ["Quince"], "usda_hardiness": "4"},
                "Ficus_carica": {"common_names": ["Fig"], "usda_hardiness": "7"},
            },
            "less_common_fruiting_trees": {
                "Armelancher_canadensis": {
                    "common_names": ["Juneberry", "Serviceberry"],
                    "usda_hardiness": "4",
                }
            },
        },
        "test_jacke": {
            "plant_matrix": {
                "Cydonia_oblonga": {"common_names": ["Quince"], "usda_hardiness": "4"}
            }
        },
    }
    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="txt"))
    assert rdm == expected


def test_to_dict_dtype_cfg():
    """Test raw.to_dict correctly using dtype="cfg"."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {},
            "less_common_fruiting_trees": {
                "Arbutus unedo": {
                    "common_names": ["Strawberry Tree"],
                    "usda_hardiness": "7",
                }
            },
        },
        "test_jacke": {"plant_matrix": {}},
    }
    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="cfg"))
    assert rdm == expected


def test_to_dict_dtype_all():
    """Test raw.to_dict correctly using dtype="all"."""
    expected = {
        "test_crawford": {
            "common_fruiting_trees": {
                "Cydonia_oblonga": {"common_names": ["Quince"], "usda_hardiness": "4"},
                "Ficus_carica": {"common_names": ["Fig"], "usda_hardiness": "7"},
            },
            "less_common_fruiting_trees": {
                "Arbutus unedo": {
                    "common_names": ["Strawberry Tree"],
                    "usda_hardiness": "7",
                },
                "Armelancher_canadensis": {
                    "common_names": ["Juneberry", "Serviceberry"],
                    "usda_hardiness": "4",
                },
                "Asimina_triloba": {
                    "common_names": ["PawPaw", "Pawpaw"],
                    "USDA_hardiness": 5,
                },
            },
        },
        "test_jacke": {
            "plant_matrix": {
                "Cydonia_oblonga": {"common_names": ["Quince"], "usda_hardiness": "4"}
            }
        },
    }

    rdm = raw.to_dict(lcl.Handler(raw_data_folder, dtype="all"))
    assert rdm == expected


def test_dummy_smb():
    """Pseudo test for raw.smb, to emulate module testing."""
    handler_class = smb.Handler
    # assert type(handler_class) == type(smb.Handler)
    assert isinstance(handler_class, type(handler_class))
