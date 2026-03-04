from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class Email:
    from_addr: str
    to_addr: str
    cc: str
    subject: str
    date_time: str
    content: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_addr,
            "to": self.to_addr,
            "cc": self.cc,
            "subject": self.subject,
            "date_time": self.date_time,
            "content": self.content,
        }


@dataclass(frozen=True)
class ClassificationResult:
    category: str  # RECLAMACAO | SOLICITACAO | ELOGIO | INDEFINIDO
    confidence: float
    evidence: Dict[str, Any]  # keywords hit, scores, etc.


@dataclass(frozen=True)
class RoutingResult:
    area: Optional[str] = None
    criticidade: Optional[str] = None
    elogio_tipo: Optional[str] = None
    nps: Optional[int] = None
