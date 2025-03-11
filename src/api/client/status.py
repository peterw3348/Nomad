import requests
from enum import Enum

class Status(Enum):
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
    """Fetch the current gameflow phase status from LCU API."""
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