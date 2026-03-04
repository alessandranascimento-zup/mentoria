from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict


_WORD_RE = re.compile(r"[\wÀ-ÿ]+")


def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    tokens = _WORD_RE.findall(text)
    return " ".join(tokens)


def load_kb(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
