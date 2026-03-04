from __future__ import annotations

from .models import Email, RoutingResult
from .utils import normalize


def infer_area(email: Email) -> str:
    t = normalize(email.subject + " " + email.content)

    if any(k in t for k in ["bacen", "anatel", "cvm", "regulator", "regulatório", "regulatorio"]):
        return "REGULATORIO"
    if any(k in t for k in ["ouvidoria", "denuncia", "denúncia"]):
        return "OUVIDORIA"
    if any(k in t for k in ["procon", "processo", "advogado", "juridic", "jurídic", "contrato"]):
        return "JURIDICO"
    return "SUPORTE_APLICATIVO"


def infer_criticidade(email: Email) -> str:
    t = normalize(email.subject + " " + email.content)

    if any(k in t for k in ["fora do ar", "indispon", "não abre", "nao abre", "down", "sem acesso", "queda"]):
        return "INDISPONIBILIDADE"
    if any(k in t for k in ["como faço", "como usar", "não consigo", "nao consigo", "dúvida", "duvida", "passo a passo"]):
        return "USABILIDADE"
    return "TECNICO"


def infer_elogio_tipo(email: Email) -> str:
    t = normalize(email.subject + " " + email.content)
    if any(k in t for k in ["atendimento", "suporte", "rápido", "rapido", "gentil"]):
        return "ATENDIMENTO"
    if any(k in t for k in ["produto", "funcionalidade", "aplicativo", "sistema"]):
        return "PRODUTO_VALORES"
    return "EXPERIENCIA"


def infer_nps(email: Email) -> int:
    t = normalize(email.subject + " " + email.content)
    strong = ["excelente", "incrível", "incrivel", "perfeito", "nota 10", "sensacional"]
    medium = ["ótimo", "otimo", "muito bom", "parabéns", "parabens"]
    weak = ["obrigado", "obrigada", "valeu", "bom"]

    if any(k in t for k in strong):
        return 5
    if any(k in t for k in medium):
        return 4
    if any(k in t for k in weak):
        return 3
    return 2


def route(category: str, email: Email) -> RoutingResult:
    if category in ("RECLAMACAO", "SOLICITACAO"):
        return RoutingResult(area=infer_area(email), criticidade=infer_criticidade(email))
    if category == "ELOGIO":
        return RoutingResult(elogio_tipo=infer_elogio_tipo(email), nps=infer_nps(email))
    return RoutingResult()
