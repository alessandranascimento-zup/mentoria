from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


RECLAMACOES = [
    ("Aplicativo fora do ar", "O app está indisponível desde cedo. Preciso acessar e não consigo. Erro 500."),
    ("Erro ao logar", "Estou com falha ao entrar. Bug no login, aparece mensagem de erro."),
    ("Quero cancelar e pedir reembolso", "Serviço não funciona e estou insatisfeito. Solicito cancelamento e reembolso."),
    ("Vou acionar o Procon", "Se não resolverem, vou abrir reclamação no Procon e procurar meus direitos."),
]

SOLICITACOES = [
    ("Solicito acesso ao sistema", "Preciso habilitar meu acesso e atualizar meus dados cadastrais."),
    ("Como faço para emitir segunda via?", "Poderiam orientar o passo a passo para emitir segunda via do documento?"),
    ("Ajuda com redefinição de senha", "Não consigo redefinir minha senha. Poderiam me ajudar?"),
    ("Solicitação de alteração cadastral", "Gostaria de alterar meu e-mail e telefone no cadastro."),
]

ELOGIOS = [
    ("Parabéns pelo atendimento", "Atendimento excelente, muito rápido e gentil. Parabéns!"),
    ("Obrigado pelo suporte", "Obrigado pela ajuda. Resolveram meu problema, muito bom!"),
    ("Produto incrível", "O aplicativo está perfeito, experiência incrível. Nota 10!"),
    ("Satisfeito com a experiência", "Estou satisfeito, foi ótimo usar o produto. Recomendo."),
]


def _rand_dt(i: int) -> str:
    base = datetime(2026, 1, 1, 9, 0, 0)
    return (base + timedelta(minutes=15 * i)).isoformat()


def generate_csv(out_path: Path, n: int = 100, seed: int = 42) -> None:
    random.seed(seed)
    rows = []
    for i in range(n):
        kind = random.choice(["RECLAMACAO", "SOLICITACAO", "ELOGIO"])
        if kind == "RECLAMACAO":
            subject, content = random.choice(RECLAMACOES)
        elif kind == "SOLICITACAO":
            subject, content = random.choice(SOLICITACOES)
        else:
            subject, content = random.choice(ELOGIOS)

        rows.append({
            "from": f"cliente{i}@email.com",
            "to": "suporte@empresa.com",
            "cc": "gestor@empresa.com" if random.random() < 0.3 else "",
            "subject": subject,
            "date_time": _rand_dt(i),
            "content": content
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        wcsv = csv.DictWriter(f, fieldnames=["from", "to", "cc", "subject", "date_time", "content"])
        wcsv.writeheader()
        wcsv.writerows(rows)
