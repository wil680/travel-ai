from __future__ import annotations

import json
import os
from typing import Any


def debug(message: str, *, data: Any | None = None) -> None:
    """Lightweight debug printer controlled by the GLOBEGUIDE_DEBUG env flag."""
    if os.getenv("GLOBEGUIDE_DEBUG") != "1":
        return

    if data is None:
        print(f"[debug] {message}")
    else:
        try:
            payload = json.dumps(data, indent=2, default=str)
        except TypeError:
            payload = repr(data)
        print(f"[debug] {message}: {payload}")

