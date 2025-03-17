import pytest
from unittest.mock import patch, mock_open
from src.api.client.champion import Champ


@pytest.fixture
def mock_champion_data():
    """Mock champion data that simulates the contents of champion_ratings.json."""
    return {
        "266": {
            "name": "Aatrox",
            "Primary": "Fighter",
            "Secondary": "Tank",
            "Ratings": {"Damage": 8, "Survivability": 7, "Control": 6},
            "Basic Attacks": "Melee",
            "Style": 5,
            "Abilities": "Physical",
            "Damage Type": "Physical",
            "Difficulty": 3,
        },
        "103": {
            "name": "Ahri",
            "Primary": "Mage",
            "Secondary": "Assassin",
            "Ratings": {"Damage": 7, "Survivability": 4, "Control": 6},
            "Basic Attacks": "Ranged",
            "Style": 8,
            "Abilities": "Magic",
            "Damage Type": "Magic",
            "Difficulty": 4,
        },
    }


@patch("builtins.open", new_callable=mock_open)
@patch("json.load")
@patch(
    "src.api.client.champion.DATA_PATH", "mock_path/champion_ratings.json"
)  # Override file path
def test_load_champs(mock_json_load, mock_file_open, mock_champion_data):
    """Test loading champions from a JSON file."""
    mock_json_load.return_value = mock_champion_data

    champs = Champ.load_champs()

    assert "266" in champs
    assert "103" in champs
    assert champs["266"].name == "Aatrox"
    assert champs["103"].name == "Ahri"


@patch.object(Champ, "load_champs")
def test_get_existing_champion(mock_load_champs, mock_champion_data):
    """Test retrieving a champion that exists."""
    mock_load_champs.return_value = {
        cid: Champ(cid, data) for cid, data in mock_champion_data.items()
    }

    champ = Champ.get("266")

    assert champ is not None
    assert champ.name == "Aatrox"
    assert champ.primary == "Fighter"
    assert champ.secondary == "Tank"


@patch.object(Champ, "load_champs")
def test_get_nonexistent_champion(mock_load_champs, mock_champion_data):
    """Test retrieving a champion that does not exist."""
    mock_load_champs.return_value = {
        cid: Champ(cid, data) for cid, data in mock_champion_data.items()
    }

    champ = Champ.get("999")  # Non-existent ID

    assert champ is None


@patch.object(Champ, "load_champs")
def test_debug_output(mock_load_champs, mock_champion_data, capsys):
    """Test the debug function output."""
    mock_load_champs.return_value = {
        cid: Champ(cid, data) for cid, data in mock_champion_data.items()
    }

    champ = Champ.get("266")
    champ.debug()

    captured = capsys.readouterr()
    assert "Aatrox" in captured.out
    assert "Primary: Fighter" in captured.out
    assert "Secondary: Tank" in captured.out
