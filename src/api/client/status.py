"""
status.py - League of Legends Gameflow Status Retriever.

Version: 0.1.0

This module retrieves the current gameflow phase status from the League of Legends LCU API.
It provides an enumeration of possible game phases and a function to fetch the current status.

Classes:
    - Status: Enum representing different game phases.

Functions:
    - get_status(port, password): Fetches the current gameflow phase from the LCU API.
"""

import requests
from enum import Enum


class Status(Enum):
    """Enumeration representing different gameflow phases in League of Legends."""

    NONE = "None"
    LOBBY = "Lobby"
    MATCHMAKING = "Matchmaking"
    READYCHECK = "ReadyCheck"
    CHAMPSELECT = "ChampSelect"
    GAMESTART = "GameStart"
    INPROGRESS = "InProgress"
    RECONNECT = "Reconnect"
    WAITINGFORSTATS = "WaitingForStats"
    PREENDOFGAME = "PreEndOfGame"
    ENDOFGAME = "EndOfGame"
    UNKNOWN = "Unknown"


def get_status(port, password):
    """
    Fetch the current gameflow phase status from the League Client API (LCU API).

    Args:
        port (str): The authentication port for the LCU API.
        password (str): The authentication token for the LCU API.

    Returns:
        str: The current gameflow phase as a string.
        If an error occurs, returns "Unknown".
    """
    url = f"https://riot:{password}@127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching game status: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request error: {e}")

    return "Unknown"
