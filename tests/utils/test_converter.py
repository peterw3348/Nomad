import json
from unittest.mock import patch, mock_open
from pathlib import Path
from src.utils.converter import load_champion_mapping, substitute_champion_ids

# Fake champion mapping data
FAKE_CHAMPION_MAPPING = {
    "64": "Lee Sin",
    "136": "Aurelion Sol",
    "54": "Malphite",
    "875": "Sett",
    "498": "Xayah",
    "203": "Kindred",
    "517": "Sylas",
    "86": "Garen",
    "245": "Ekko",
    "141": "Kayn",
    "893": "Briar"
}

# Sample input for testing
FAKE_INPUT_DATA = {
    "team": [136, 64, 54, 875, 498],  # Known champions
    "bench": [203, 517, 86, 245, 141, 999]  # 999 is an unknown ID
}

EXPECTED_OUTPUT = {
    "team": ["Aurelion Sol", "Lee Sin", "Malphite", "Sett", "Xayah"],
    "bench": ["Kindred", "Sylas", "Garen", "Ekko", "Kayn", "Unknown"]  # 999 should be "Unknown"
}


@patch("src.utils.paths.ASSETS_DIR", new=Path("/fake/path"))  # Correctly use a Path object
@patch("pathlib.Path.exists", return_value=True)  # Mock file existence check
@patch("pathlib.Path.open", new_callable=mock_open, read_data=json.dumps(FAKE_CHAMPION_MAPPING))
def test_load_champion_mapping(mock_file, mock_exists):
    """Test that champion mappings are loaded correctly from a JSON file."""
    result = load_champion_mapping()
    assert result == FAKE_CHAMPION_MAPPING
    mock_file.assert_called_once()


@patch("src.utils.converter.load_champion_mapping", return_value=FAKE_CHAMPION_MAPPING)
def test_substitute_champion_ids(mock_load_mapping):
    """Test substitution of champion IDs to champion names, including handling unknown IDs."""
    result = substitute_champion_ids(FAKE_INPUT_DATA)
    assert result == EXPECTED_OUTPUT
    mock_load_mapping.assert_called_once()


def test_substitute_champion_ids_invalid_input():
    """Test error handling when input is not a dictionary."""
    result = substitute_champion_ids(["invalid", "data"])
    assert result == {}  # Should return an empty dictionary


@patch("src.utils.converter.load_champion_mapping", return_value={})
def test_substitute_champion_ids_no_mapping(mock_load_mapping):
    """Test behavior when the champion mapping file is empty."""
    result = substitute_champion_ids(FAKE_INPUT_DATA)
    assert result == {
        "team": ["Unknown"] * 5,
        "bench": ["Unknown"] * 6
    }
