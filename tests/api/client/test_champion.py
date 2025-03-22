import pytest
from unittest.mock import patch, mock_open
from src.api.client.champion import ChampionMetadata, ChampionState, load_champions


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
def test_load_champions(mock_json_load, mock_file_open, mock_champion_data):
    """Test loading champions from a JSON file."""
    mock_json_load.return_value = mock_champion_data

    champs = load_champions()

    assert "266" in champs
    assert "103" in champs
    assert isinstance(champs["266"], ChampionState)
    assert champs["266"].meta.name == "Aatrox"
    assert champs["103"].meta.name == "Ahri"


def test_champion_metadata_fields(mock_champion_data):
    """Test individual metadata fields are correctly assigned."""
    meta = ChampionMetadata("266", mock_champion_data["266"])

    assert meta.name == "Aatrox"
    assert meta.primary == "Fighter"
    assert meta.secondary == "Tank"
    assert meta.type == "Physical"
    assert meta.ratings["Damage"] == 8


def test_champion_state_fields(mock_champion_data):
    """Test ChampionState correctly wraps metadata and initializes defaults."""
    meta = ChampionMetadata("266", mock_champion_data["266"])
    champ = ChampionState(meta)

    assert champ.cid == "266"
    assert champ.raw_gain == 0.0
    assert champ.norm_wr == 0.0
    assert champ.score == 0.0
    assert champ.meta.name == "Aatrox"


def test_champion_debug_output(capsys, mock_champion_data):
    """Test debug output includes important champion information."""
    meta = ChampionMetadata("266", mock_champion_data["266"])
    champ = ChampionState(meta)
    champ.debug()

    captured = capsys.readouterr()
    assert "Aatrox" in captured.out
    assert "Primary: Fighter" in captured.out
    assert "Secondary: Tank" in captured.out
