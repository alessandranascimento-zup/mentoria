from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


def build_report(db_path: Path, out_md: Path, out_csv: Path) -> None:
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM results")
    total = cur.fetchone()[0] or 0

    cur.execute("SELECT AVG(ended_ts - started_ts) FROM results")
    avg_latency = cur.fetchone()[0] or 0.0

    cur.execute("SELECT SUM(escalated_human) FROM results")
    human = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(retries) FROM results")
    retries = cur.fetchone()[0] or 0

    cur.execute("SELECT category, COUNT(*) FROM results GROUP BY category ORDER BY COUNT(*) DESC")
    by_cat = cur.fetchall()

    cur.execute("SELECT area, COUNT(*) FROM results WHERE area IS NOT NULL GROUP BY area ORDER BY COUNT(*) DESC")
    by_area = cur.fetchall()

    cur.execute("SELECT criticidade, COUNT(*) FROM results WHERE criticidade IS NOT NULL GROUP BY criticidade ORDER BY COUNT(*) DESC")
    by_crit = cur.fetchall()

    cur.execute("SELECT AVG(nps) FROM results WHERE nps IS NOT NULL")
    avg_nps = cur.fetchone()[0]

    autonomy = total - human
    autonomy_rate = (autonomy / total) if total else 0.0

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["total", "autonomous", "autonomy_rate", "human_escalations", "total_retries", "avg_latency_s", "avg_nps"])
        wcsv.writerow([total, autonomy, round(autonomy_rate, 4), human, retries, round(avg_latency, 4), (round(avg_nps, 2) if avg_nps is not None else "")])

    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Relatório de Triagem de E-mails\n")
    lines.append(f"- Total de e-mails processados: **{total}**")
    lines.append(f"- Atendimentos autônomos: **{autonomy}** ({autonomy_rate:.1%})")
    lines.append(f"- Chamados que caíram para atendimento humano: **{human}**")
    lines.append(f"- Retentativas totais: **{retries}**")
    lines.append(f"- Tempo médio de atendimento (latência do pipeline): **{avg_latency:.4f}s**")
    if avg_nps is not None:
        lines.append(f"- NPS médio inferido (Elogios): **{avg_nps:.2f} / 5**")
    lines.append("\n## Distribuição por categoria\n")
    for cat, cnt in by_cat:
        lines.append(f"- {cat}: {cnt}")

    lines.append("\n## Distribuição por área (quando aplicável)\n")
    for area, cnt in by_area:
        lines.append(f"- {area}: {cnt}")

    lines.append("\n## Distribuição por criticidade (quando aplicável)\n")
    for crit, cnt in by_crit:
        lines.append(f"- {crit}: {cnt}")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    con.close()
