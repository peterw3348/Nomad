"""Unit tests for the core > test watcher."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.core.watcher.watcher import (
    log_final_champion_select,
    display_lobby_champions,
    monitor_lobby,
)
from src.api.client.status import Status
from src.api.client.champion import ChampionPool


@pytest.fixture
def mock_evaluated_data():
    """Fixture that returns a mocked ChampionPool for testing."""
    mock_lee_sin = MagicMock()
    mock_lee_sin.cid = "64"
    mock_lee_sin.meta.name = "Lee Sin"
    mock_lee_sin.score = 50.0
    mock_lee_sin.norm_gain = 10.0
    mock_lee_sin.norm_wr = 5.0
    mock_lee_sin.raw_wr = 3.0

    mock_aurelion_sol = MagicMock()
    mock_aurelion_sol.cid = "136"
    mock_aurelion_sol.meta.name = "Aurelion Sol"
    mock_aurelion_sol.score = 45.0
    mock_aurelion_sol.norm_gain = 12.0
    mock_aurelion_sol.norm_wr = 4.0
    mock_aurelion_sol.raw_wr = 2.0

    mock_pool = MagicMock(spec=ChampionPool)
    mock_pool.team = [mock_lee_sin]
    mock_pool.bench = [mock_aurelion_sol]
    mock_pool.player = mock_lee_sin

    return mock_pool


@patch("builtins.open", new_callable=mock_open)
def test_log_final_champion_select(mock_file, mock_evaluated_data):
    """Test that log_final_champion_select writes output to a file."""
    log_final_champion_select(mock_evaluated_data)
    mock_file.assert_called_once()


@patch("sys.stdout.write")
def test_display_lobby_champions(mock_stdout):
    """Test that display_lobby_champions prints structured champion info."""
    mock_champ = MagicMock()
    mock_champ.cid = "64"
    mock_champ.meta.name = "Lee Sin"
    mock_champ.score = 10.0
    mock_champ.norm_gain = 2.0
    mock_champ.norm_wr = 3.0
    mock_champ.raw_wr = 4.0

    mock_pool = MagicMock(spec=ChampionPool)
    mock_pool.team = [mock_champ]
    mock_pool.bench = [mock_champ]
    mock_pool.player = mock_champ

    display_lobby_champions(mock_pool)
    mock_stdout.assert_called()


@patch("src.core.watcher.get_status")
@patch(
    "src.core.watcher.fetch_lobby_champions",
    return_value={"team": [], "bench": [], "player": []},
)
@patch(
    "src.core.watcher.sanitize_champion_data",
    return_value={"team": [], "bench": [], "player": []},
)
@patch(
    "src.core.watcher.evaluator", return_value={"team": [], "bench": [], "player": []}
)
@patch("src.core.watcher.display_lobby_champions")
@patch("time.sleep", return_value=None)
@pytest.mark.skip(reason="Postponing until watcher refactor")
def test_monitor_lobby(
    mock_sleep, mock_display, mock_evaluator, mock_sanitize, mock_fetch, mock_get_status
):
    """Test that monitor_lobby fetches data, evaluates, and logs final state."""
    status_sequence = [
        Status.NONE.value,
        Status.CHAMPSELECT.value,
        Status.CHAMPSELECT.value,
        Status.INPROGRESS.value,
    ]

    mock_get_status.side_effect = lambda *args, **kwargs: (
        status_sequence.pop(0) if status_sequence else Status.INPROGRESS.value
    )

    monitor_lobby("port", "password", "puuid", max_iterations=5)

    assert mock_get_status.call_count >= 4
    mock_display.assert_called()
    mock_evaluator.assert_called()
    mock_fetch.assert_called()
    mock_sanitize.assert_called()
