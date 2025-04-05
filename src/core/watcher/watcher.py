"""
watcher.py - Core ARAM Champion Select Monitor.

Coordinates polling the League Client API (LCU), triggering champion evaluations,
and calling display and logging utilities. Designed to run persistently in the
background, cycling through games and automatically restarting when one ends.

Responsibilities:
- Poll LCU for lobby status and champion select phase.
- Fetch and sanitize lobby champion data.
- Evaluate team compositions using the Evaluator pipeline.
- Call display and logging handlers with evaluated results.
"""

import time
from src.api.client.acquire import get_credentials
from src.api.client.lobby import fetch_lobby_champions
from src.api.client.sanitize import sanitize_champion_data
from src.api.client.status import Status, get_status
from src.core.evaluator import evaluator
from src.core.watcher.display import display_lobby_champions
from src.core.watcher.logging import log_final_champion_select

WAIT_INTERVAL = 10
POLL_INTERVAL = 1
MAX_FAILS_BEFORE_EXIT = 10


def wait_for_champ_select(port, password):
    """
    Block until the game enters the champion select phase.

    Periodically checks the LCU status endpoint until it reports
    `CHAMPSELECT`, then returns control to the caller.

    Args:
        port (str): Port for LCU authentication.
        password (str): Password/token for LCU authentication.
    """
    while True:
        status = get_status(port, password)
        if status == Status.CHAMPSELECT.value:
            print("\nChampion Select detected. Fetching lobby data...")
            return
        print("\rWaiting for Champion Select...", end="", flush=True)
        time.sleep(WAIT_INTERVAL)


def monitor_lobby(port, password, puuid):
    """
    Continuously monitor the ARAM lobby state during champion select.

    This function:
    - Waits for the lobby to enter champion select.
    - Polls the lobby to fetch team composition.
    - Evaluates champions and displays the result.
    - Logs the final champion state when champion select ends.

    Args:
        port (str): Port for LCU authentication.
        password (str): Password/token for LCU authentication.
        puuid (str): The player's Riot PUUID (used to identify their selected champion).
    """
    pool = None
    while True:
        wait_for_champ_select(port, password)
        failure_count = 0

        while True:
            status = get_status(port, password)
            if status != Status.CHAMPSELECT.value:
                if pool:
                    log_final_champion_select(pool)
                print("\nChampion Select ended. Waiting for next game...\n")
                break

            lobby_data = fetch_lobby_champions(port, password)
            if lobby_data:
                sanitized_data = sanitize_champion_data(lobby_data, puuid)
                pool = evaluator(sanitized_data)
                display_lobby_champions(pool)
                failure_count = 0
            else:
                failure_count += 1
                if failure_count >= MAX_FAILS_BEFORE_EXIT:
                    print("\nFailed to fetch lobby data multiple times. Exiting early.")
                    return

            time.sleep(POLL_INTERVAL)


def main():
    """Entry point for initializing credentials and monitoring the champion select process."""
    port, password, puuid = get_credentials()
    monitor_lobby(port, password, puuid)


if __name__ == "__main__":
    main()
