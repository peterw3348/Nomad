import subprocess
import re
import sys

def get_lcu_credentials():
    if sys.platform.startswith("win"):
        cmd = ["wmic", "PROCESS", "WHERE", "name='LeagueClientUx.exe'", "GET", "commandline"]
    else:
        cmd = "ps -A | grep LeagueClientUx"
    
    try:
        result = subprocess.run(cmd, shell=(not sys.platform.startswith("win")), capture_output=True, text=True)
        output = result.stdout
    
        if not output:
            print("LeagueClientUx process not found.")
            return

        port_match = re.search(r"--app-port=([0-9]*)", output)
        token_match = re.search(r"--remoting-auth-token=([\w-]*)", output)

        if port_match and token_match:
            print(f"Port: {port_match.group(1)}")
            print(f"Password: {token_match.group(1)}")
        else:
            print("Could not extract credentials.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_lcu_credentials()
