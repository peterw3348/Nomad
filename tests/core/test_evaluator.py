"""Unit tests for the core > test evaluator."""

import pytest
import numpy as np
from unittest.mock import patch, mock_open
from src.core.evaluator import (
    check_role_weight_sums,
    diminishing_returns,
    apply_role_weights,
    fetch_win_rates,
    convert_grouped_to_champs,
    compute_composition_gain,
    evaluator,
)
from src.api.client.champion import ChampionState, ChampionMetadata, ChampionPool


@pytest.fixture
def mock_role_weights():
    """Fixture for sample role weight configuration."""
    return {
        "Mage": {
            "Damage": 1.5,
            "Toughness": 0.5,
            "Control": 1.0,
            "Mobility": 1.0,
            "Utility": 1.0,
        },
        "Tank": {
            "Damage": 1.0,
            "Toughness": 2.0,
            "Control": 1.0,
            "Mobility": 0.5,
            "Utility": 0.5,
        },
    }


@pytest.fixture
def mock_win_rates():
    """Fixture for sample win rate values."""
    return {
        "64": (50.0, 0.0),
        "136": (55.0, 10.0),
        "875": (45.0, -10.0),
    }


@pytest.fixture
def mock_champions():
    """Fixture for mock ChampionState objects."""
    return {
        "64": ChampionState(
            ChampionMetadata(
                "64",
                {
                    "name": "Lee Sin",
                    "Primary": "Fighter",
                    "Secondary": "Tank",
                    "Ratings": {
                        "Damage": 2,
                        "Control": 1,
                        "Toughness": 3,
                        "Mobility": 4,
                        "Utility": 1,
                    },
                    "Basic Attacks": "Melee",
                    "Style": 2,
                    "Abilities": "Energy-based",
                    "Damage Type": "Physical",
                    "Difficulty": 3,
                },
            )
        ),
        "136": ChampionState(
            ChampionMetadata(
                "136",
                {
                    "name": "Aurelion Sol",
                    "Primary": "Mage",
                    "Secondary": "Controller",
                    "Ratings": {
                        "Damage": 3,
                        "Control": 4,
                        "Toughness": 1,
                        "Mobility": 2,
                        "Utility": 3,
                    },
                    "Basic Attacks": "Ranged",
                    "Style": 3,
                    "Abilities": "Mana-based",
                    "Damage Type": "Magic",
                    "Difficulty": 4,
                },
            )
        ),
        "875": ChampionState(
            ChampionMetadata(
                "875",
                {
                    "name": "Sett",
                    "Primary": "Fighter",
                    "Secondary": "Tank",
                    "Ratings": {
                        "Damage": 4,
                        "Control": 2,
                        "Toughness": 5,
                        "Mobility": 1,
                        "Utility": 1,
                    },
                    "Basic Attacks": "Melee",
                    "Style": 1,
                    "Abilities": "Grit-based",
                    "Damage Type": "Physical",
                    "Difficulty": 2,
                },
            )
        ),
    }


@patch(
    "src.core.evaluator.role_weights",
    new_callable=lambda: {
        "Tank": {
            "Damage": 1.5,
            "Toughness": 2,
            "Control": 1,
            "Mobility": 0.3,
            "Utility": 0.2,
        }
    },
)
def test_check_role_weight_sums(mock_weights):
    """Test that role weight sums fall within expected tolerance."""
    check_role_weight_sums()


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0, 5.0),
        (5, 5.0),
        (10, 12.13),
        (15, 14.18),
    ],
)
@pytest.mark.skip(reason="Postponing until evaluator refactor")
def test_diminishing_returns(input_value, expected_output):
    """Test diminishing returns formula for various inputs."""
    result = diminishing_returns(input_value)
    assert np.isclose(result, expected_output, atol=0.1)


@patch(
    "src.core.evaluator.role_weights", new_callable=lambda: {"Mage": {"Damage": 1.5}}
)
def test_apply_role_weights(mock_weights, mock_champions):
    """Test weighted contribution calculation for a champion category."""
    champ = mock_champions["136"]
    result = apply_role_weights(champ, "Damage")
    assert result == 4.5


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="id,champion,win_rate\n1,64,50.0\n2,136,55.0\n3,875,45.0",
)
def test_fetch_win_rates(mock_file):
    """Test loading and normalization of win rate values."""
    win_rates = fetch_win_rates()
    assert win_rates["64"] == (50.0, 0.0)
    assert win_rates["136"][1] > 0
    assert win_rates["875"][1] < 0


@patch("src.api.client.champion.load_champions")
@patch("src.core.evaluator.fetch_win_rates")
def test_convert_grouped_to_champs(
    mock_fetch_wr, mock_load_champs, mock_champions, mock_win_rates
):
    """Test grouped champion data is properly wrapped in a ChampionPool."""
    mock_load_champs.return_value = mock_champions
    mock_fetch_wr.return_value = mock_win_rates

    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    result = convert_grouped_to_champs(grouped)

    assert hasattr(result, "team") and len(result.team) == 2
    assert hasattr(result, "bench") and len(result.bench) == 1
    assert hasattr(result, "player") and result.player.cid == "64"


@patch("src.core.evaluator.diminishing_returns", side_effect=lambda x: x)
def test_compute_composition_gain(mock_diminishing, mock_champions):
    """Test champion composition gain and score calculation."""
    grouped_raw = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    pool = ChampionPool(grouped_raw, mock_champions)
    result = compute_composition_gain(pool)

    assert result.player.score is not None
    assert result.bench[0].score is not None


@patch("src.core.evaluator.convert_grouped_to_champs")
@patch("src.core.evaluator.compute_composition_gain")
def test_evaluator(mock_compute_gain, mock_convert_champs, mock_champions):
    """Test full evaluation flow from input to score output."""
    mock_convert_champs.return_value = {
        "team": [mock_champions["64"], mock_champions["136"]],
        "bench": [mock_champions["875"]],
        "player": [mock_champions["64"]],
    }
    mock_compute_gain.return_value = mock_convert_champs.return_value

    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    result = evaluator(grouped)

    assert isinstance(result, dict)
    assert "team" in result and len(result["team"]) == 2
    assert "bench" in result and len(result["bench"]) == 1
    assert "player" in result and len(result["player"]) == 1
