import subprocess
import re
import sys
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_credentials():
    port, password = get_process()
    if port and password:
        puuid = get_puuid()
        return port, password, puuid
    else:
        return None, None, None

def get_process():
    if sys.platform.startswith("win"):
        cmd = ["wmic", "PROCESS", "WHERE", "name='LeagueClientUx.exe'", "GET", "commandline"]
    else:
        cmd = "ps -A | grep LeagueClientUx"
    
    try:
        result = subprocess.run(cmd, shell=(not sys.platform.startswith("win")), capture_output=True, text=True)
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
