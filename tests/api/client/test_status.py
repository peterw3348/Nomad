import pytest
import requests
from unittest.mock import patch
from src.api.client.status import get_status, Status


@pytest.mark.parametrize(
    "mock_response, expected_status",
    [
        ("None", Status.NONE.value),
        ("Lobby", Status.LOBBY.value),
        ("Matchmaking", Status.MATCHMAKING.value),
        ("ReadyCheck", Status.READYCHECK.value),
        ("ChampSelect", Status.CHAMPSELECT.value),
        ("GameStart", Status.GAMESTART.value),
        ("InProgress", Status.INPROGRESS.value),
        ("Reconnect", Status.RECONNECT.value),
        ("WaitingForStats", Status.WAITINGFORSTATS.value),
        ("PreEndOfGame", Status.PREENDOFGAME.value),
        ("EndOfGame", Status.ENDOFGAME.value),
        ("Unknown", Status.UNKNOWN.value),
    ],
)
@patch("src.api.client.status.requests.get")
def test_get_status(mock_get, mock_response, expected_status):
    """Test that get_status returns the correct phase based on API response."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    port = "1234"
    password = "testpassword"
    result = get_status(port, password)

    assert result == expected_status, f"Expected {expected_status}, got {result}"


@patch("src.api.client.status.requests.get")
def test_get_status_request_error(mock_get):
    """Test get_status when a request exception occurs."""
    mock_get.side_effect = requests.RequestException("Connection error")

    port = "1234"
    password = "testpassword"
    result = get_status(port, password)

    assert result == "Unknown", "Expected 'Unknown' on request failure"


@patch("src.api.client.status.requests.get")
def test_get_status_non_200_response(mock_get):
    """Test get_status when API returns a non-200 response."""
    mock_get.return_value.status_code = 500  # Simulating server error

    port = "1234"
    password = "testpassword"
    result = get_status(port, password)

    assert result == "Unknown", "Expected 'Unknown' on non-200 API response"
