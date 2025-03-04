import sys
import time
import itertools
import urllib3
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.api.client_data.acquire import get_lcu_credentials
from src.api.client_data.lobby import fetch_lobby_champions
from src.api.client_data.sanitize import sanitize_champion_data
from src.api.client_data.status import Status, get_status
from src.api import paths

MAX_RETRIES = 20
WAIT_INTERVAL = 10  # Time between status checks
POLL_INTERVAL = 1   # Time between lobby fetch attempts
MAX_FAILS_BEFORE_EXIT = 10  # Stop retrying after too many failures
WR_PATH = paths.DATA_DIR / "static" / "dd_wr.csv"

def animated_waiting(message="Waiting", duration=WAIT_INTERVAL):
    """Displays a rotating spinner animation while waiting."""
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{message} {next(spinner)} ")
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")

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
    """Displays Team and Bench champions in a structured format with sorting and placeholders."""
    grouped = sanitized_data

    def sort_by_wr(champ_list):
        """Sorts champions by win rate in descending order."""
        return sorted(champ_list, key=lambda champ: wr.get(champ, ("Unknown", 0))[1], reverse=True)

    sorted_team = sort_by_wr(grouped["team"])
    sorted_bench = sort_by_wr(grouped["bench"])

    while len(sorted_bench) < 10:
        sorted_bench.append(None)  # Fill with empty placeholders

    output_lines = ["\nChampion Select:"]
    output_lines.append(f"{'Team':<20} {'Win Rate':<8} | {'Bench':<20} {'Win Rate':<8} | {'Bench':<20} {'Win Rate':<8}")
    output_lines.append("-" * 80)

    for i in range(max(len(sorted_team), 5)):
        team_champ = sorted_team[i] if i < len(sorted_team) else None
        bench_champ_1 = sorted_bench[i] if i < len(sorted_bench) else None
        bench_champ_2 = sorted_bench[i + 5] if i + 5 < len(sorted_bench) else None

        team_text = f"{wr.get(team_champ, ('Unknown', 0))[0]:<20} {wr.get(team_champ, ('Unknown', 0))[1]:<8.1f}%" if team_champ else " " * 30
        bench_text_1 = f"{wr.get(bench_champ_1, ('', 0))[0]:<20} {wr.get(bench_champ_1, ('', 0))[1]:<8.1f}%" if bench_champ_1 else " " * 30
        bench_text_2 = f"{wr.get(bench_champ_2, ('', 0))[0]:<20} {wr.get(bench_champ_2, ('', 0))[1]:<8.1f}%" if bench_champ_2 else " " * 30

        output_lines.append(f"{team_text} | {bench_text_1} | {bench_text_2}")

    sys.stdout.write("\r" + "\n".join(output_lines) + "\n")
    sys.stdout.flush()

def get_credentials_with_retries():
    for attempt in range(1, MAX_RETRIES + 1):
        credentials = get_lcu_credentials()
        if credentials:
            print(f"Successfully acquired credentials.")
            return credentials
        print(f"Attempt {attempt} failed. Retrying...")
        animated_waiting("Retrying credentials")

    print("Failed to acquire LCU credentials after multiple attempts. Exiting.")
    sys.exit(0)

def wait_for_champ_select(port, password):
    while True:
        status = get_status(port, password)
        if status == Status.CHAMPSELECT.value:
            print("\nChampion Select detected. Fetching lobby data...")
            return
        animated_waiting("Waiting for next Champion Select...")

def monitor_lobby(port, password, wr):
    while True:
        wait_for_champ_select(port, password)

        failure_count = 0
        while True:
            status = get_status(port, password)
            if status != Status.CHAMPSELECT.value:
                print("\nChampion Select ended. Waiting for next game...\n")
                break

            sys.stdout.write("\rFetching lobby data... ")
            sys.stdout.flush()

            lobby_data = fetch_lobby_champions(port, password)

            if lobby_data:
                sys.stdout.write("\rLobby data fetched successfully.          \n")
                sanitized_data = sanitize_champion_data(lobby_data)
                display_lobby_champions(sanitized_data, wr)
                failure_count = 0
            else:
                failure_count += 1
                if failure_count >= MAX_FAILS_BEFORE_EXIT:
                    print("\nFailed to fetch lobby data multiple times. Exiting early.")
                    return
                animated_waiting("Waiting for lobby data...")

            time.sleep(POLL_INTERVAL)

def main():
    wr = load_win_rate()
    port, password = get_credentials_with_retries()
    monitor_lobby(port, password, wr)

if __name__ == "__main__":
    main()
