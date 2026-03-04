from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def notify(outbox_dir: Path, payload: Dict[str, Any]) -> Path:
    outbox_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"notification_{ts}_{payload.get('email_id','na')}.json"
    path = outbox_dir / fname
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
