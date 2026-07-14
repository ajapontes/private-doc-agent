from pathlib import Path

APP_NAME = "private-doc-agent"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"

SUPPORTED_EXTENSIONS = {".txt", ".md"}