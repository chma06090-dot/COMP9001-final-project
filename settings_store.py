"""Save and load user settings for Sip Time Cafe."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


SETTINGS_PATH = Path(__file__).with_name("saved_settings.json")


def save_settings(settings: Dict[str, Any], path: Path = SETTINGS_PATH) -> None:
    """Save settings as readable JSON."""

    path.write_text(
        json.dumps(settings, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_settings(path: Path = SETTINGS_PATH) -> Optional[Dict[str, Any]]:
    """Load settings, returning None if no valid settings file exists."""

    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None
    return data
