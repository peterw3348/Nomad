import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.core.watcher import (
    log_final_champion_select,
    display_lobby_champions,
    monitor_lobby,
)
from src.api.client.status import Status


@pytest.fixture
def mock_evaluated_data():
    """Mock evaluated data fixture for tests."""
    mock_lee_sin = MagicMock()
    mock_lee_sin.cid = "64"
    mock_lee_sin.name = "Lee Sin"
    mock_lee_sin.score = 50.0
    mock_lee_sin.norm_gain = 10.0
    mock_lee_sin.norm_wr = 5.0
    mock_lee_sin.raw_wr = 3.0

    mock_aurelion_sol = MagicMock()
    mock_aurelion_sol.cid = "136"
    mock_aurelion_sol.name = "Aurelion Sol"
    mock_aurelion_sol.score = 45.0
    mock_aurelion_sol.norm_gain = 12.0
    mock_aurelion_sol.norm_wr = 4.0
    mock_aurelion_sol.raw_wr = 2.0

    return {
        "team": [mock_lee_sin],
        "bench": [mock_aurelion_sol],
        "player": [mock_lee_sin],
    }


@patch("builtins.open", new_callable=mock_open)
def test_log_final_champion_select(mock_file, mock_evaluated_data):
    log_final_champion_select(mock_evaluated_data)
    mock_file.assert_called_once()


@patch("sys.stdout.write")
def test_display_lobby_champions(mock_stdout):
    mock_champ = MagicMock()
    mock_champ.cid = "64"
    mock_champ.name = "Lee Sin"
    mock_champ.score = 10.0
    mock_champ.norm_gain = 2.0
    mock_champ.norm_wr = 3.0
    mock_champ.raw_wr = 4.0

    mock_evaluated_data = {
        "team": [mock_champ],
        "bench": [mock_champ],
        "player": [mock_champ],
    }

    display_lobby_champions(mock_evaluated_data)
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
@patch("time.sleep", return_value=None)  # Avoid actual sleep calls in tests
@pytest.mark.skip(reason="Postponing until watcher refactor")
def test_monitor_lobby(
    mock_sleep, mock_display, mock_evaluator, mock_sanitize, mock_fetch, mock_get_status
):
    """Test that monitor_lobby fetches data, evaluates, and logs final state."""

    # Simulating status transitions (game phase changes)
    status_sequence = [
        Status.NONE.value,  # Pre-game state
        Status.CHAMPSELECT.value,  # Champion select begins
        Status.CHAMPSELECT.value,  # Champion select ongoing
        Status.INPROGRESS.value,  # Game starts, should exit now
    ]

    # Mock `get_status` to return statuses sequentially, then stay on INPROGRESS
    mock_get_status.side_effect = lambda *args, **kwargs: (
        status_sequence.pop(0) if status_sequence else Status.INPROGRESS.value
    )

    # Run monitor_lobby in test mode with a max iteration cap
    monitor_lobby("port", "password", "puuid", max_iterations=5)

    # Ensure expected function calls were made
    assert mock_get_status.call_count >= 4  # Called multiple times
    mock_display.assert_called()
    mock_evaluator.assert_called()
    mock_fetch.assert_called()
    mock_sanitize.assert_called()
