from __future__ import annotations

from typing import Dict, Any, List, Tuple

from .models import Email, ClassificationResult
from .utils import normalize


class RuleBasedClassifier:
    """Classificador determinístico baseado em palavras-chave (KB).

    Regras:
    - subject tem peso maior (2.0)
    - content tem peso padrão (1.0)
    - confidence baseada na separação de score (top1 vs top2)
    """

    def __init__(self, kb: Dict[str, Any]):
        self.kb = kb
        self.categories = kb["categories"]
        self.min_conf = float(kb.get("rules", {}).get("min_confidence", 0.55))

    def _score_text(self, text_norm: str, keywords: List[str]) -> Tuple[float, List[str]]:
        hits: List[str] = []
        score = 0.0
        for kw in keywords:
            kw_norm = normalize(kw)
            if not kw_norm:
                continue
            if kw_norm in text_norm:
                hits.append(kw)
                score += 1.0
        return score, hits

    def classify(self, email: Email) -> ClassificationResult:
        subject_norm = normalize(email.subject)
        content_norm = normalize(email.content)

        scores: Dict[str, float] = {}
        hits_map: Dict[str, Dict[str, Any]] = {}

        for cat, meta in self.categories.items():
            kws = meta.get("keywords", [])
            s_sub, h_sub = self._score_text(subject_norm, kws)
            s_con, h_con = self._score_text(content_norm, kws)

            score = 2.0 * s_sub + 1.0 * s_con
            scores[cat] = score
            hits_map[cat] = {"subject_hits": h_sub, "content_hits": h_con, "score": score}

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0

        if top_score <= 0:
            return ClassificationResult(
                category="INDEFINIDO",
                confidence=0.0,
                evidence={"scores": scores, "hits": hits_map, "reason": "no_keyword_hits"},
            )

        conf_base = top_score / (top_score + second_score + 1.0)
        diff = max(0.0, top_score - second_score)
        confidence = min(1.0, conf_base + (diff / (top_score + 5.0)))

        return ClassificationResult(
            category=top_cat,
            confidence=float(confidence),
            evidence={"scores": scores, "hits": hits_map},
        )
