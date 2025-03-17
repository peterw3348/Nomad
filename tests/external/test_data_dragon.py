from unittest.mock import patch
from src.api.external.data_dragon import get_champion_names


MOCK_DDRAGON_RESPONSE = {
    "data": {
        "Aatrox": {"key": "266"},
        "Ahri": {"key": "103"},
        "Akali": {"key": "84"},
        "Alistar": {"key": "12"},
    }
}


@patch("src.api.external.data_dragon.requests.get")
def test_get_champion_names_success(mock_get):
    """Test successful retrieval and parsing of champion names from Data Dragon."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_DDRAGON_RESPONSE

    champions = get_champion_names()

    assert champions == {
        "266": "Aatrox",
        "103": "Ahri",
        "84": "Akali",
        "12": "Alistar",
    }, "Champion data should match the expected API response"


@patch("src.api.external.data_dragon.requests.get")
def test_get_champion_names_api_failure(mock_get):
    """Test behavior when Data Dragon API returns a failure response."""
    mock_get.return_value.status_code = 500  # Simulating a server error

    champions = get_champion_names()

    assert champions == {}, "Function should return an empty dictionary on API failure"


@patch("src.api.external.data_dragon.requests.get")
def test_get_champion_names_malformed_response(mock_get):
    """Test behavior when Data Dragon API returns malformed data."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"invalid_key": "bad_data"}

    champions = get_champion_names()

    assert (
        champions == {}
    ), "Function should return an empty dictionary if response is malformed"
