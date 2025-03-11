from pathlib import Path

PWD = Path(__file__).resolve()
BASE_DIR = PWD.parent.parent.parent
API_DIR =  BASE_DIR / "src" / "api"
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STATIC_DIR = DATA_DIR / "static"
TEST_DIR = BASE_DIR / "test"

def print_dirs():
    print(f"Base Directory: {BASE_DIR}")
    print(f"API Directory: {API_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Raw Directory: {RAW_DIR}")
    print(f"Static Directory: {STATIC_DIR}")

if __name__ == "__main__":
    print_dirs()