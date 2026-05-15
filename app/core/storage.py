import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
KNOWLEDGE_FILE = os.path.join(DATA_DIR, 'knowledge.json')
LOCATIONS_FILE = os.path.join(DATA_DIR, 'locations.json')


def ensure_data_dir() -> None:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create data directories: {e}")


def read_json_file(path: str, default: Any):
    try:
        if not os.path.isfile(path):
            return default
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON file {path}: {e}")
        return default


def write_json_file(path: str, data: Any) -> bool:
    try:
        tmp = f"{path}.tmp"
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except Exception as e:
        logger.error(f"Failed to write JSON file {path}: {e}")
        return False




