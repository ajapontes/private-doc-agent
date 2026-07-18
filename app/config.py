"""
Application configuration module.

This module centralizes the main configuration values used by the
Private Doc Agent application, including application metadata,
local document paths, supported file extensions, and local LLM settings.

The values related to Ollama are loaded from environment variables
defined in the .env file.
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.2.2"


# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"


# Supported document types for this version
SUPPORTED_EXTENSIONS = {".txt", ".md"}


# Local LLM configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")