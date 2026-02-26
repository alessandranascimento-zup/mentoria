# AI Email Triage (Desafio AI Engineer)

Este repositório implementa um fluxo autônomo para **classificar e-mails** em:
- `RECLAMACAO`
- `SOLICITACAO_SERVICO`
- `ELOGIO`

E, a partir disso, executar **ações específicas por categoria**:
- Reclamação / Solicitação: **direcionar para área responsável** e **avaliar criticidade**
- Elogio: **categorizar o elogio** e **inferir nota de satisfação (1 a 5)**

Além disso, o sistema registra **telemetria de atendimento** para gerar relatórios:
- tempo de atendimento
- falha de categorização
- retentativas
- chamados que caíram para atendimento humano

> O enunciado pede base fictícia (CSV/JSON/TXT) com campos `from,to,cc,subject,date-time,content` e automação do fluxo com notificações e relatório.  
> Implementado conforme arquivo do problema. (ver `data/emails.csv` e `scripts/generate_report.py`)

---

## Como rodar

### 1) Criar ambiente e instalar dependências
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e .
```

### 2) Gerar base fictícia (CSV)
```bash
python scripts/generate_fake_emails.py --out data/emails.csv --n 250
```

### 3) Treinar modelo (ML determinístico + baseline)
```bash
python scripts/train.py --data data/emails.csv --out models
```

### 4) Rodar API
```bash
uvicorn app.api:app --reload
```

Abra:
- `http://127.0.0.1:8000/docs`

### 5) Rodar processamento em lote e gerar relatório
```bash
python scripts/batch_process.py --data data/emails.csv --models models --out runs/run_001
python scripts/generate_report.py --run runs/run_001 --out reports/run_001_report.csv
```

---

## Decisões de engenharia (o que o recrutador vai avaliar)

### Determinismo (por design)
1) **Regras primeiro (rule-based)**
   - Para casos óbvios e críticos: indisponibilidade, erro técnico, cobrança, pedido de suporte, elogio explícito etc.
   - Motivo: regras são **auditáveis**, baratas e consistentes.

2) **Modelo clássico (TF-IDF + Logistic Regression)**
   - Treinamento reprodutível (seed fixa) e inferência rápida.
   - Motivo: baseline forte, fácil de explicar e manter.

3) **Fallback para humano**
   - Se a confiança for baixa, o caso vai para triagem humana e conta como "autonomia falhou".

### Uso de "tools" (LLM/RAG) — opcional e justificado
Este repo inclui um **stub** de ferramenta LLM em `app/tools/llm_stub.py`:
- Só seria acionada quando `confidence < threshold` **ou** quando regras/ML não inferirem subcategoria/criticidade.
- Configuração sugerida: **temperature=0**, **label set fechado**, resposta em **JSON validado**.
- Justificativa: melhorar casos ambíguos mantendo previsibilidade.  
- Importante: o desafio não exige LLM; por isso o sistema roda **100% offline** por padrão.

### Base de conhecimento (KB)
- A taxonomia e mapeamentos ficam em `app/config/taxonomy.yml` (rótulos, áreas, criticidade, exemplos e palavras-chave).
- Se fosse necessário RAG, os documentos de política/FAQ seriam carregados e indexados (não requerido aqui).

---

## Estrutura do repositório

- `app/`
  - `api.py` (FastAPI)
  - `core/` (pipeline, regras, modelo, métricas)
  - `config/taxonomy.yml` (KB/taxonomia)
  - `tools/llm_stub.py` (opcional)
- `data/` (CSV fictício)
- `models/` (artefatos do treinamento)
- `runs/` (execuções batch com logs)
- `reports/` (relatórios)

---

## Testes
```bash
pytest -q
```
