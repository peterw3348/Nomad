from pathlib import Path

API_DIR = Path(__file__).resolve()
BASE_DIR = API_DIR.parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def print_dirs():
    print(f"Base Directory: {BASE_DIR}")
    print(f"API Directory: {API_DIR}")
    print(f"Data Directory: {DATA_DIR}")

if __name__ == "__main__":
    print_dirs()