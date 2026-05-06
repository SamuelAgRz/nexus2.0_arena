from pathlib import Path
from typing import Any
import json
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str | Path) -> dict[str, Any]:
    file_path = PROJECT_ROOT / path if not Path(path).is_absolute() else Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data or {}


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = PROJECT_ROOT / path if not Path(path).is_absolute() else Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data or {}


def load_text(path: str | Path) -> str:
    file_path = PROJECT_ROOT / path if not Path(path).is_absolute() else Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")

    return file_path.read_text(encoding="utf-8")