from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterator, Tuple
import sqlite3

from .classifier import RuleBasedClassifier
from .models import Email
from .notifier import notify
from .router import route
from .utils import load_kb


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  email_id TEXT NOT NULL,
  ts_utc TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  email_id TEXT NOT NULL,
  category TEXT NOT NULL,
  confidence REAL NOT NULL,
  retries INTEGER NOT NULL,
  escalated_human INTEGER NOT NULL,
  area TEXT,
  criticidade TEXT,
  elogio_tipo TEXT,
  nps INTEGER,
  started_ts REAL NOT NULL,
  ended_ts REAL NOT NULL
);
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.executescript(SCHEMA_SQL)
    con.commit()
    return con


def _log_event(con: sqlite3.Connection, run_id: str, email_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    con.execute(
        "INSERT INTO events(run_id,email_id,ts_utc,event_type,payload_json) VALUES (?,?,?,?,?)",
        (run_id, email_id, datetime.utcnow().isoformat(), event_type, json.dumps(payload, ensure_ascii=False)),
    )
    con.commit()


def _iter_csv(path: Path) -> Iterator[Tuple[str, Email]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            email = Email(
                from_addr=row.get("from", ""),
                to_addr=row.get("to", ""),
                cc=row.get("cc", ""),
                subject=row.get("subject", ""),
                date_time=row.get("date_time", ""),
                content=row.get("content", ""),
            )
            yield str(i), email


def _iter_jsonl(path: Path) -> Iterator[Tuple[str, Email]]:
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            obj = json.loads(line)
            email = Email(
                from_addr=obj.get("from", ""),
                to_addr=obj.get("to", ""),
                cc=obj.get("cc", ""),
                subject=obj.get("subject", ""),
                date_time=obj.get("date_time", ""),
                content=obj.get("content", ""),
            )
            yield str(i), email


def _iter_input(path: Path) -> Iterator[Tuple[str, Email]]:
    if path.suffix.lower() == ".csv":
        return _iter_csv(path)
    if path.suffix.lower() in (".jsonl", ".json"):
        return _iter_jsonl(path)
    raise ValueError("Formato não suportado. Use .csv ou .jsonl")


def run_pipeline(
    input_path: Path,
    output_path: Path,
    kb_path: Path,
    db_path: Path,
    outbox_dir: Path,
) -> Dict[str, Any]:
    kb = load_kb(kb_path)
    classifier = RuleBasedClassifier(kb)
    max_retries = int(kb.get("rules", {}).get("max_retries", 2))
    min_conf = float(kb.get("rules", {}).get("min_confidence", 0.55))
    fallback_human = bool(kb.get("rules", {}).get("human_fallback_on_low_confidence", True))

    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    con = _connect(db_path)

    processed = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as out:
        for email_id, email in _iter_input(input_path):
            started = time.time()
            retries = 0
            escalated = 0

            _log_event(con, run_id, email_id, "email_received", email.as_dict())

            while True:
                res = classifier.classify(email)
                _log_event(con, run_id, email_id, "classified", {"category": res.category, "confidence": res.confidence, "evidence": res.evidence})

                if res.category != "INDEFINIDO" and res.confidence >= min_conf:
                    break

                if retries >= max_retries:
                    if fallback_human:
                        escalated = 1
                        _log_event(con, run_id, email_id, "escalated_human", {"reason": "low_confidence_or_undefined", "retries": retries})
                    break

                retries += 1
                _log_event(con, run_id, email_id, "retry", {"retry": retries})

            routing = route(res.category, email)
            _log_event(con, run_id, email_id, "routed", {"category": res.category, "routing": routing.__dict__})

            notif_payload = {
                "email_id": email_id,
                "category": res.category,
                "confidence": res.confidence,
                "retries": retries,
                "escalated_human": bool(escalated),
                "routing": routing.__dict__,
                "to_notify": [email.to_addr, email.cc],
            }
            notif_path = notify(outbox_dir, notif_payload)
            _log_event(con, run_id, email_id, "notified", {"path": str(notif_path)})

            ended = time.time()
            con.execute(
                """INSERT INTO results(run_id,email_id,category,confidence,retries,escalated_human,area,criticidade,elogio_tipo,nps,started_ts,ended_ts)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    run_id,
                    email_id,
                    res.category,
                    float(res.confidence),
                    int(retries),
                    int(escalated),
                    routing.area,
                    routing.criticidade,
                    routing.elogio_tipo,
                    routing.nps,
                    float(started),
                    float(ended),
                ),
            )
            con.commit()

            record = {
                "run_id": run_id,
                "email_id": email_id,
                **email.as_dict(),
                "category": res.category,
                "confidence": res.confidence,
                "retries": retries,
                "escalated_human": bool(escalated),
                "routing": routing.__dict__,
                "latency_seconds": round(ended - started, 4),
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            processed += 1

    con.close()
    return {"run_id": run_id, "processed": processed}
