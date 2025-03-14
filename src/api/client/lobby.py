"""
lobby.py - League of Legends Champion Select Data Fetcher.

Version: 0.1.0

This module interacts with the League of Legends LCU API to fetch champion
selection data during the lobby phase. It retrieves and processes the raw
champion selection session JSON data.

Functions:
    - fetch_lobby_champions(port, password): Fetches the current champion selection data.
"""

import requests
import json
import sys

from src.api.client.sanitize import sanitize_champion_data


def fetch_lobby_champions(port, password):
    """
    Fetch the current champion selection session data from the LCU API.

    Args:
        port (str): The authentication port for the LCU API.
        password (str): The authentication token for the LCU API.

    Returns:
        dict: The raw JSON data if successful, else None.
    """
    base_url = f"https://riot:{password}@127.0.0.1:{port}"
    session_url = f"{base_url}/lol-champ-select/v1/session"

    try:
        response = requests.get(session_url, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException as e:
        print("Error fetching data:", e)
        return None


if __name__ == "__main__":
    """
    Entry point for fetching champion selection data from the LCU API.

    Usage:
        python lobby.py <port> <password>

    Args:
        port (str): The authentication port for the LCU API.
        password (str): The authentication token for the LCU API.
    """
    if len(sys.argv) != 3:
        print("Usage: python lobby.py <port> <password>")
        sys.exit(1)

    port = sys.argv[1]
    password = sys.argv[2]

    data = fetch_lobby_champions(port, password)

    if data:
        sanitized_data = sanitize_champion_data(data)
        print(json.dumps(sanitized_data, indent=4))
