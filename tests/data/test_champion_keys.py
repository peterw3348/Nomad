import json
import pytest
from src.utils import paths


@pytest.fixture
def load_champion_data():
    """Loads real champion mapping and champion ratings data for validation."""
    champions_path = paths.ASSETS_DIR / "champions.json"
    ratings_path = paths.ASSETS_DIR / "champion_ratings.json"

    with open(champions_path, "r", encoding="utf-8") as file:
        champions = json.load(file)

    with open(ratings_path, "r", encoding="utf-8") as file:
        champion_ratings = json.load(file)

    return champions, champion_ratings


def test_validate_champion_keys(load_champion_data):
    """Ensures champion IDs match expected names in both files."""
    champions, champion_ratings = load_champion_data

    for champ_id, data in champion_ratings.items():
        expected_name = data.get("name")
        actual_name = champions.get(champ_id)

        assert (
            actual_name == expected_name
        ), f"Mismatch for key {champ_id}: Expected {expected_name}, Found {actual_name}"


def test_missing_champion_entries(load_champion_data):
    """Checks if all champion IDs in ratings exist in champions.json."""
    champions, champion_ratings = load_champion_data

    for champ_id in champion_ratings.keys():
        assert (
            champ_id in champions
        ), f"Missing champion ID {champ_id} in champions.json"


def test_no_extra_champion_entries(load_champion_data):
    """Ensures champions.json doesn't contain extra champions not found in ratings."""
    champions, champion_ratings = load_champion_data

    for champ_id in champions.keys():
        assert (
            champ_id in champion_ratings
        ), f"Extra champion ID {champ_id} found in champions.json but not in ratings"
