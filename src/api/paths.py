from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_DIR = BASE_DIR / "src" / "api"
DATA_DIR = BASE_DIR / "data"

def print_dirs():
    print(f"Base Directory: {BASE_DIR}")
    print(f"API Directory: {API_DIR}")
    print(f"Data Directory: {DATA_DIR}")

if __name__ == "__main__":
    print_dirs()