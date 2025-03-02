import sys
import time
import itertools
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.api.client_data.acquire import get_lcu_credentials
from src.api.client_data.lobby import fetch_lobby_champions
from src.api.client_data.sanitize import sanitize_champion_data
from src.api.converter import substitute_champion_ids

MAX_RETRIES = 20
TOTAL_RUNTIME = 70  # Total time limit in seconds
WAIT_INTERVAL = 10  # Time between lobby fetch attempts
POLL_INTERVAL = 1
MAX_FAILS_BEFORE_EXIT = 60  # Stop retrying after too many failures

def animated_waiting(message="Waiting", duration=WAIT_INTERVAL):
    """Displays a rotating spinner animation while waiting."""
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{message} {next(spinner)} ")
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")  # Clear line

def get_credentials_with_retries():
    """Tries to get LCU credentials up to MAX_RETRIES times before exiting."""
    for attempt in range(1, MAX_RETRIES + 1):
        credentials = get_lcu_credentials()
        if credentials:
            print(f"Successfully acquired credentials.")
            return credentials
        print(f"Attempt {attempt} failed. Retrying...")
        animated_waiting("Retrying credentials")

    print("Failed to acquire LCU credentials after multiple attempts. Exiting.")
    sys.exit(0)

def main():
    """Main function to acquire LCU credentials and fetch lobby data within a 70-second window."""
    port, password = get_credentials_with_retries()

    print("\nWaiting for a successful lobby fetch before starting the timer...")

    while True:
        lobby_data = fetch_lobby_champions(port, password)
        if lobby_data:
            print("\nFirst successful lobby fetch. Starting the timer now.")
            break
        animated_waiting("Waiting for lobby data...")

    start_time = time.time()
    failure_count = 0  # Track failures after first success

    while time.time() - start_time < TOTAL_RUNTIME:
        sys.stdout.write("\rFetching lobby data... ")
        sys.stdout.flush()

        lobby_data = fetch_lobby_champions(port, password)

        if lobby_data:
            sys.stdout.write("\rLobby data fetched successfully.          \n")

            sanitized_data = sanitize_champion_data(lobby_data)
            lobby_data = substitute_champion_ids(sanitized_data)
            print("\nLobby Data:")
            print(lobby_data)

            failure_count = 0  # Reset failure counter
        else:
            failure_count += 1
            if failure_count >= MAX_FAILS_BEFORE_EXIT:
                print("\nFailed to fetch lobby data multiple times. Exiting early.")
                break

            animated_waiting("Waiting for lobby data...")

        time.sleep(POLL_INTERVAL)

    print("\nTime limit reached. Exiting.")

if __name__ == "__main__":
    main()
