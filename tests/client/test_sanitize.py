import json
import pytest
from src.api.client.sanitize import sanitize_champion_data


@pytest.fixture
def golden_data():
    """Load golden data from fixture files."""
    with open("tests/fixtures/lobby.json", "r") as f:
        input_data = json.load(f)

    with open("tests/fixtures/lobby_clean.json", "r") as f:
        expected_output = json.load(f)

    return input_data, expected_output


def test_sanitize_champion_data(golden_data):
    """Test that sanitize_champion_data produces the correct output."""
    input_data, expected_output = golden_data
    player_puuid = "15c66f9d-0464-513f-a881-a72d40386dbd"

    result = sanitize_champion_data(input_data, player_puuid)

    assert (
        result == expected_output
    ), "sanitize_champion_data output does not match expected golden data."
