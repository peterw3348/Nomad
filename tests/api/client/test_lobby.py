"""Unit tests for the api > client > test lobby."""

import requests
from unittest.mock import patch
from src.api.client.lobby import fetch_lobby_champions


@patch("src.api.client.lobby.requests.get")
def test_fetch_lobby_champions_success(mock_get):
    """Test fetch_lobby_champions when API request succeeds with valid data."""
    mock_data = {
        "myTeam": [
            {"championId": 64, "puuid": "player1"},
            {"championId": 55, "puuid": "player2"},
        ],
        "benchChampions": [{"championId": 20}, {"championId": 30}],
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_data

    port = "1234"
    password = "testpassword"
    result = fetch_lobby_champions(port, password)

    assert result == mock_data, "Expected the function to return valid JSON data."


@patch("src.api.client.lobby.requests.get")
def test_fetch_lobby_champions_fail_non_200(mock_get):
    """Test fetch_lobby_champions when API returns a non-200 response."""
    mock_get.return_value.status_code = 403  # Simulating forbidden access

    port = "1234"
    password = "testpassword"
    result = fetch_lobby_champions(port, password)

    assert result is None, "Expected None on non-200 API response."


@patch("src.api.client.lobby.requests.get")
def test_fetch_lobby_champions_request_exception(mock_get):
    """Test fetch_lobby_champions when a request exception occurs."""
    mock_get.side_effect = requests.RequestException("Connection error")

    port = "1234"
    password = "testpassword"
    result = fetch_lobby_champions(port, password)

    assert result is None, "Expected None when a request exception occurs."
