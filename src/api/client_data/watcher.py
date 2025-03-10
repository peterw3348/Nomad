import sys
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.api.client_data.acquire import get_credentials
from src.api.client_data.lobby import fetch_lobby_champions
from src.api.client_data.sanitize import sanitize_champion_data
from src.api.client_data.status import Status, get_status
from src.api.client_data.evaluator import evaluator

MAX_RETRIES = 3
WAIT_INTERVAL = 10  # Time between status checks
POLL_INTERVAL = 1   # Time between lobby fetch attempts
MAX_FAILS_BEFORE_EXIT = 10  # Stop retrying after too many failures

# Store last fetched data to prevent redundant reprints
previous_lobby_data = None  

def display_lobby_champions(evaluated_data):
    """Displays Team and Bench champions in a structured format, only if there are changes."""
    global previous_lobby_data

    if evaluated_data == previous_lobby_data:
        return  # Do nothing if the lobby data is the same

    previous_lobby_data = evaluated_data  # Update previous state

    team = evaluated_data["team"]
    bench = evaluated_data["bench"]
    player_champ = evaluated_data["player"][0] if evaluated_data["player"] else None

    # Clear terminal screen to overwrite previous output
    sys.stdout.write("\033c")  # Clears terminal (works on most systems)
    sys.stdout.flush()

    output_lines = ["\nChampion Select:"]
    output_lines.append(f" {'Key':<6} {'Champion':<18}  | {'Score':<10} {'Comp Score':<10} {'WR Score':<10} {'Raw WR':<10}")
    output_lines.append("-" * 80)

    for champ in team:
        if champ == player_champ:
            output_lines.append(f"> {champ.cid:<6} {champ.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}")
        else:
            output_lines.append(f"  {champ.cid:<6} {champ.name:<18} | ")
    
    output_lines.append("Bench ===")
    for champ in bench:
        output_lines.append(f"  {champ.cid:<6} {champ.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}")

    sys.stdout.write("\n".join(output_lines) + "\n")
    sys.stdout.flush()

def wait_for_champ_select(port, password):
    """Waits for the game to enter champion select before proceeding."""
    while True:
        status = get_status(port, password)
        if status == Status.CHAMPSELECT.value:
            print("\nChampion Select detected. Fetching lobby data...")
            return
        sys.stdout.write("\rWaiting for Champion Select... ")
        sys.stdout.flush()
        time.sleep(WAIT_INTERVAL)

def monitor_lobby(port, password, puuid):
    while True:
        wait_for_champ_select(port, password)

        failure_count = 0
        while True:
            status = get_status(port, password)
            if status != Status.CHAMPSELECT.value:
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
    port, password, puuid = get_credentials()
    monitor_lobby(port, password, puuid)

if __name__ == "__main__":
    main()
