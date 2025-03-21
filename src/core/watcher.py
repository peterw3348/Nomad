"""
watcher.py - ARAM Champion Select Watcher.

This script monitors League of Legends ARAM champion select,
evaluates champion picks, and logs the final team composition.

Functions:
    - log_final_champion_select(evaluated_data): Logs the final state of champion select before exiting.
    - display_lobby_champions(evaluated_data): Displays Team and Bench champions in a structured format only if data has changed.
    - wait_for_champ_select(port, password): Waits for the game to enter champion select before proceeding.
    - monitor_lobby(port, password, puuid): Monitors champion select, retrieves lobby data, and evaluates champion choices.
    - main(): Entry point for initializing credentials and monitoring the champion select process.
"""

import sys
import time
import urllib3
from datetime import datetime
from src.api.client.acquire import get_credentials
from src.api.client.lobby import fetch_lobby_champions
from src.api.client.sanitize import sanitize_champion_data
from src.api.client.status import Status, get_status
from src.core.evaluator import evaluator
from src.utils import paths
from src.__version__ import __version__ as version

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_RETRIES = 3
WAIT_INTERVAL = 10  # Time between status checks
POLL_INTERVAL = 1  # Time between lobby fetch attempts
MAX_FAILS_BEFORE_EXIT = 10  # Stop retrying after too many failures
LOG_PATH = paths.DATA_DIR / "logs" / version

# Setup logging
LOG_PATH.mkdir(parents=True, exist_ok=True)
previous_lobby_data = None  # Store last fetched data to prevent redundant reprints


def log_final_champion_select(evaluated_data):
    """
    Log the final state of champion select before exiting.

    Args:
        evaluated_data (dict): Processed champion selection data containing team and bench information.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_file = LOG_PATH / f"champion_select_{timestamp}.log"

    log_lines = [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')} ==="]
    log_lines.append("Champion Select:")
    log_lines.append(
        f" {'Key':<6} {'Champion':<18}  | {'Score':<10} {'Comp Score':<10} {'WR Score':<10} {'Raw WR':<10}"
    )
    log_lines.append("-" * 80)

    player_champ = evaluated_data["player"][0] if evaluated_data["player"] else None

    for champ in evaluated_data["team"]:
        if champ == player_champ:
            log_lines.append(
                f"> {champ.cid:<6} {champ.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
            )
        else:
            log_lines.append(f"  {champ.cid:<6} {champ.name:<18}")

    log_lines.append("Bench ===")
    for champ in evaluated_data["bench"]:
        log_lines.append(
            f"  {champ.cid:<6} {champ.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
        )

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))


def display_lobby_champions(evaluated_data):
    """
    Display Team and Bench champions in a structured format only if data has changed.

    Args:
        evaluated_data (dict): Processed champion selection data containing team and bench information.
    """
    global previous_lobby_data
    if evaluated_data == previous_lobby_data:
        return  # Skip printing if no new data

    previous_lobby_data = evaluated_data  # Update state

    sys.stdout.write("\033c")  # Clears terminal
    sys.stdout.flush()

    output_lines = ["\nChampion Select:"]
    output_lines.append(
        f" {'Key':<6} {'Champion':<18}  | {'Score':<10} {'Comp Score':<10} {'WR Score':<10} {'Raw WR':<10}"
    )
    output_lines.append("-" * 80)

    player_champ = evaluated_data["player"][0] if evaluated_data["player"] else None

    for champ in evaluated_data["team"]:
        if champ == player_champ:
            output_lines.append(
                f"> {champ.cid:<6} {champ.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
            )
        else:
            output_lines.append(f"  {champ.cid:<6} {champ.name:<18}")

    output_lines.append("Bench ===")
    for champ in evaluated_data["bench"]:
        output_lines.append(
            f"  {champ.cid:<6} {champ.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
        )

    sys.stdout.write("\n".join(output_lines) + "\n")
    sys.stdout.flush()


def wait_for_champ_select(port, password):
    """
    Wait for the game to enter champion select before proceeding.

    Args:
        port (str): The authentication port for the LCU API.
        password (str): The authentication token for the LCU API.
    """
    while True:
        status = get_status(port, password)
        if status == Status.CHAMPSELECT.value:
            print("\nChampion Select detected. Fetching lobby data...")
            return
        sys.stdout.write("\rWaiting for Champion Select... ")
        sys.stdout.flush()
        time.sleep(WAIT_INTERVAL)


def monitor_lobby(port, password, puuid):
    """
    Monitor champion select, retrieves lobby data, evaluates champion choices, and logs final selection.

    Args:
        port (str): The authentication port for the LCU API.
        password (str): The authentication token for the LCU API.
        puuid (str): The player's unique identifier.
    """
    evaluated_data = None

    while True:
        wait_for_champ_select(port, password)
        failure_count = 0

        while True:
            status = get_status(port, password)
            if status != Status.CHAMPSELECT.value:
                log_final_champion_select(evaluated_data)
                print("\nChampion Select ended. Waiting for next game...\n")
                break

            lobby_data = fetch_lobby_champions(port, password)
            if lobby_data:
                sanitized_data = sanitize_champion_data(lobby_data, puuid)
                evaluated_data = evaluator(sanitized_data)
                display_lobby_champions(evaluated_data)
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
