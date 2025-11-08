from __future__ import annotations

import json
from pathlib import Path

from utils.logger import debug

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DESTINATIONS_PATH = DATA_DIR / "destinations.json"


def _load_known_destinations() -> set[str]:
    if not DESTINATIONS_PATH.exists():
        return set()
    try:
        with DESTINATIONS_PATH.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
            if isinstance(data, list):
                return {str(item).strip().title() for item in data}
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        debug("Failed to load destinations list", data={"error": str(exc)})
    return set()


_KNOWN_DESTINATIONS = _load_known_destinations()


def normalize_destination(value: str) -> str:
    """Best-effort destination correction using a static lookup."""
    if not value:
        return value

    title_cased = value.strip().title()

    if not _KNOWN_DESTINATIONS:
        return title_cased

    if title_cased in _KNOWN_DESTINATIONS:
        return title_cased

    # Simple heuristic: find close match by prefix
    for destination in _KNOWN_DESTINATIONS:
        if destination.lower().startswith(title_cased.lower()):
            return destination

    return title_cased

