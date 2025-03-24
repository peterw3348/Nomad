"""Unit tests for the core > evaluator module."""

import pytest
import numpy as np
from unittest.mock import patch, mock_open
from src.core.evaluator import (
    check_role_weight_sums,
    diminishing_returns,
    apply_role_weights,
    assign_win_rates,
    compute_raw_composition_gains,
    normalize_composition_gains,
    compute_scores,
    Evaluator,
)
from src.api.client.champion import ChampionState, ChampionMetadata, ChampionPool


@pytest.fixture
def mock_champions():
    """Fixture that returns a mock dictionary of ChampionState instances."""
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


def test_check_role_weight_sums():
    """Test that role weight sums do not raise any errors."""
    check_role_weight_sums()


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (5, 5.0),
        (10, 12.13),
        (15, 14.18),
    ],
)
def test_diminishing_returns(input_value, expected_output):
    """Test diminishing returns function with various inputs."""
    result = diminishing_returns(input_value)
    assert np.isclose(result, expected_output, atol=0.1)


@patch(
    "src.core.evaluator.role_weights", new_callable=lambda: {"Mage": {"Damage": 1.5}}
)
def test_apply_role_weights(mock_weights, mock_champions):
    """Test applying role weights to a champion's ratings."""
    champ = mock_champions["136"]
    result = apply_role_weights(champ, "Damage")
    assert result == 4.5


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="id,champion,win_rate\n1,64,50.0\n2,136,55.0\n3,875,45.0",
)
def test_assign_win_rates(mock_file, mock_champions):
    """Test assigning raw and normalized win rates to champions."""
    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    pool = ChampionPool(grouped, mock_champions)
    assign_win_rates(pool)
    assert pool.player.raw_wr == 50.0
    assert pool.player.norm_wr == 0.0
    assert pool.bench[0].norm_wr < 0


def test_compute_raw_composition_gains(mock_champions):
    """Test computing raw composition gains for a champion pool."""
    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    pool = ChampionPool(grouped, mock_champions)
    compute_raw_composition_gains(pool)
    assert hasattr(pool.player, "raw_gain")
    assert pool.player.raw_gain != 0.0


def test_normalize_composition_gains(mock_champions):
    """Test normalizing composition gains across the available pool."""
    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    pool = ChampionPool(grouped, mock_champions)
    for champ in pool.available:
        champ.raw_gain = 100 if champ.cid == "875" else 50
    normalize_composition_gains(pool)
    gains = [champ.norm_gain for champ in pool.available]
    assert any(g != 0 for g in gains)


def test_compute_scores(mock_champions):
    """Test computing final scores from normalized gain and win rate."""
    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    pool = ChampionPool(grouped, mock_champions)
    for champ in pool.available:
        champ.norm_gain = 10
        champ.norm_wr = 20
    compute_scores(pool)
    for champ in pool.available:
        assert champ.score == round(10 * 0.7 + 20 * 0.3, 2)


@patch("src.core.evaluator.assign_win_rates")
@patch("src.core.evaluator.compute_raw_composition_gains")
@patch("src.core.evaluator.normalize_composition_gains")
@patch("src.core.evaluator.compute_scores")
def test_aram_evaluator_pipeline(
    mock_scores, mock_normalize, mock_gain, mock_wr, mock_champions
):
    """Test full ARAM evaluation pipeline integration with mocks."""
    grouped = {"team": ["64", "136"], "bench": ["875"], "player": ["64"]}
    evaluator = Evaluator(grouped)
    pool = evaluator.evaluate()
    mock_wr.assert_called_once()
    mock_gain.assert_called_once()
    mock_normalize.assert_called_once()
    mock_scores.assert_called_once()
    assert isinstance(pool, ChampionPool)
