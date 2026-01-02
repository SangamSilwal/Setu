"""
Configuration module for Module C (Letter Generation)
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "module-C"
TEMPLATE_DIR = DATA_DIR  # Templates are directly in data/module-C based on user input

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# LLM settings (Shared with Module A for consistency)
MISTRAL_MODEL = "mistral-tiny"
MISTRAL_API_KEY_ENV_VAR = "MISTRAL_API_KEY"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
