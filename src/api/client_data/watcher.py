import sys
import time
import itertools
import urllib3
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.api.client_data.acquire import get_credentials
from src.api.client_data.lobby import fetch_lobby_champions
from src.api.client_data.sanitize import sanitize_champion_data
from src.api.client_data.status import Status, get_status
from src.utils import paths

MAX_RETRIES = 3
WAIT_INTERVAL = 10  # Time between status checks
POLL_INTERVAL = 1   # Time between lobby fetch attempts
MAX_FAILS_BEFORE_EXIT = 10  # Stop retrying after too many failures
WR_PATH = paths.STATIC_DIR / "dd_wr.csv"

# Store last fetched data to prevent redundant reprints
previous_lobby_data = None  

def load_win_rate(file_path=WR_PATH):
    win_rate_dict = {}

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header

        for row in reader:
            if len(row) < 4:
                print("Error: Misaligned row")
                continue
            name, key, win_rate, _ = row[:4]
            win_rate_dict[int(key)] = (name, float(win_rate.strip('%')))

    return win_rate_dict

def display_lobby_champions(sanitized_data, wr):
    """Displays Team and Bench champions in a structured format, only if there are changes."""
    global previous_lobby_data

    if sanitized_data == previous_lobby_data:
        return  # Do nothing if the lobby data is the same

    previous_lobby_data = sanitized_data  # Update previous state

    grouped = sanitized_data

    def sort_by_wr(champ_list):
        """Sorts champions by win rate in descending order."""
        return sorted(champ_list, key=lambda champ: wr.get(champ, ("Unknown", 0))[1], reverse=True)

    sorted_team = sort_by_wr(grouped["team"])
    sorted_bench = sort_by_wr(grouped["bench"])
    player_champ = grouped["player"][0] if grouped["player"] else None

    while len(sorted_bench) < 10:
        sorted_bench.append(None)  # Fill with empty placeholders

    # Clear terminal screen to overwrite previous output
    sys.stdout.write("\033c")  # Clears terminal (works on most systems)
    sys.stdout.flush()

    output_lines = ["\nChampion Select:"]
    output_lines.append(f" {'Team':<20} {'Win Rate':<8} | {'Bench':<20} {'Win Rate':<8}  | {'Bench':<20} {'Win Rate':<8}")
    output_lines.append("-" * 80)

    for i in range(max(len(sorted_team), 5)):
        team_champ = sorted_team[i] if i < len(sorted_team) else None
        bench_champ_1 = sorted_bench[i] if i < len(sorted_bench) else None
        bench_champ_2 = sorted_bench[i + 5] if i + 5 < len(sorted_bench) else None

        team_text = f"{'> ' if team_champ == player_champ else '  '}{wr.get(team_champ, ('Unknown', 0))[0]:<18} {wr.get(team_champ, ('Unknown', 0))[1]:<8.1f}%" if team_champ else " " * 30
        bench_text_1 = f"{wr.get(bench_champ_1, ('', 0))[0]:<20} {wr.get(bench_champ_1, ('', 0))[1]:<8.1f}%" if bench_champ_1 else " " * 30
        bench_text_2 = f"{wr.get(bench_champ_2, ('', 0))[0]:<20} {wr.get(bench_champ_2, ('', 0))[1]:<8.1f}%" if bench_champ_2 else " " * 30

        output_lines.append(f"{team_text} | {bench_text_1} | {bench_text_2}")

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

def monitor_lobby(port, password, wr, puuid):
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
                display_lobby_champions(sanitized_data, wr)
                failure_count = 0
            else:
                failure_count += 1
                if failure_count >= MAX_FAILS_BEFORE_EXIT:
                    print("\nFailed to fetch lobby data multiple times. Exiting early.")
                    return

            time.sleep(POLL_INTERVAL)

def main():
    wr = load_win_rate()
    port, password, puuid = get_credentials()
    monitor_lobby(port, password, wr, puuid)

if __name__ == "__main__":
    main()
