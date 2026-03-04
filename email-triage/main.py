from __future__ import annotations

import argparse
from pathlib import Path

from src.email_triage.pipeline import run_pipeline
from src.email_triage.report import build_report
from scripts.generate_fake_emails import generate_csv


PROJECT_ROOT = Path(__file__).resolve().parent


def _abs(p: str) -> Path:
    pp = Path(p)
    return pp if pp.is_absolute() else (PROJECT_ROOT / pp)


def cmd_generate_data(args: argparse.Namespace) -> int:
    out = _abs(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    generate_csv(out_path=out, n=args.n, seed=args.seed)
    print(f"[ok] base fictícia gerada: {out}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    inp = _abs(args.input)
    out = _abs(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    result = run_pipeline(
        input_path=inp,
        output_path=out,
        kb_path=_abs(args.kb),
        db_path=_abs(args.db),
        outbox_dir=_abs(args.outbox),
    )
    print(f"[ok] processados: {result['processed']}")
    print(f"[ok] output: {out}")
    print(f"[ok] db: {_abs(args.db)}")
    print(f"[ok] outbox: {_abs(args.outbox)}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    db = _abs(args.db)
    out = _abs(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    build_report(db_path=db, out_md=out, out_csv=_abs(args.csv))
    print(f"[ok] relatório: {out}")
    print(f"[ok] métricas (csv): {_abs(args.csv)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="email-triage", description="Email triage pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate-data", help="Gera base fictícia de e-mails")
    g.add_argument("--out", required=True, help="Caminho do CSV de saída")
    g.add_argument("--n", type=int, default=100, help="Quantidade de e-mails")
    g.add_argument("--seed", type=int, default=42, help="Seed")
    g.set_defaults(func=cmd_generate_data)

    r = sub.add_parser("run", help="Roda pipeline de triagem")
    r.add_argument("--input", required=True, help="CSV ou JSONL de entrada")
    r.add_argument("--out", required=True, help="JSONL de saída")
    r.add_argument("--kb", default="kb/taxonomy.json", help="KB / Taxonomia")
    r.add_argument("--db", default="runs/triage.db", help="SQLite DB")
    r.add_argument("--outbox", default="outbox", help="Diretório de notificações (mock)")
    r.set_defaults(func=cmd_run)

    rep = sub.add_parser("report", help="Gera relatório a partir do DB")
    rep.add_argument("--db", default="runs/triage.db", help="SQLite DB")
    rep.add_argument("--out", default="runs/report.md", help="Markdown de saída")
    rep.add_argument("--csv", default="runs/metrics.csv", help="CSV de saída")
    rep.set_defaults(func=cmd_report)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
