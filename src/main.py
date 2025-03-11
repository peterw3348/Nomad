from src.api.client.acquire import get_credentials
from src.core.watcher import monitor_lobby

def main():
    port, password, puuid = get_credentials()
    monitor_lobby(port, password, puuid)

if __name__ == "__main__":
    main()