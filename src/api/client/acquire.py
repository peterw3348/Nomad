"""
acquire.py - League of Legends Client Credential Retriever.

This module extracts authentication credentials from the League of Legends,
client. It retrieves the app port, authentication token, and the
PUUID (Player UUID) required for interacting with the League Client API.

Functions:
    - get_credentials(): Retrieve the app port, authentication token,
    and PUUID.
    - get_process(): Extract authentication details from the running
    LeagueClientUx process.
    - get_puuid(): Retrieve the player's unique identifier from the
    client API.
"""

import subprocess
import re
import sys
import requests

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_credentials():
    """
    Retrieve the League of Legends client authentication credentials.

    Returns:
        tuple: (port (str), password (str), puuid (str))
        If credentials are not found, returns (None, None, None).
    """
    port, password = get_process()
    if port and password:
        puuid = get_puuid()
        return port, password, puuid
    else:
        return None, None, None


def get_process():
    """
    Extract the app port and authentication token from the LeagueClientUx process.

    Returns:
        tuple: (port (str), password (str))
        If process is not found or credentials cannot be extracted,
        returns (None, None).
    """
    if sys.platform.startswith("win"):
        cmd = [
            "wmic",
            "PROCESS",
            "WHERE",
            "name='LeagueClientUx.exe'",
            "GET",
            "commandline",
        ]
    else:
        cmd = "ps -A | grep LeagueClientUx"
    try:
        result = subprocess.run(
            cmd,
            shell=(not sys.platform.startswith("win")),
            capture_output=True,
            text=True,
        )
        output = result.stdout

        if not output:
            print("LeagueClientUx process not found.")
            return None, None

        port_match = re.search(r"--app-port=([0-9]*)", output)
        token_match = re.search(r"--remoting-auth-token=([\w-]*)", output)

        if port_match and token_match:
            port = port_match.group(1)
            password = token_match.group(1)
            return port, password
        else:
            print("Could not extract credentials.")
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def get_puuid():
    """
    Retrieve the player's unique identifier (PUUID) from the League Client API.

    Returns:
        str: PUUID if successful.
        None: If the PUUID cannot be retrieved.
    """
    port, token = get_process()
    if not port or not token:
        print("Failed to retrieve credentials.")
        return None

    url = f"https://riot:{token}@127.0.0.1:{port}/lol-summoner/v1/current-summoner"

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        puuid = data.get("puuid")
        return puuid
    except requests.RequestException as e:
        print(f"Error fetching PUUID: {e}")
        return None


if __name__ == "__main__":
    port, password, puuid = get_credentials()
    print(f"Port: {port}, Token: {password}, PID: {puuid}")
