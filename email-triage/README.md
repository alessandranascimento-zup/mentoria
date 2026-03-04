# Email Triage (Reclamação | Solicitação | Elogio)

Solução em Python para **categorizar e-mails**, **rotear para a área responsável**, **inferir criticidade/NPS**, **notificar envolvidos** e **gerar relatórios** de atendimento autônomo (tempo, falhas, retentativas e escalonamentos para humano).

Requisitos do desafio (base fictícia, autonomia, indicadores) estão descritos em `problema.md`.

## Tools (vou usar ou não usar?)

### Sem tools externas (padrão)
A solução funciona **sem LLM**, sem APIs externas e sem dependências além da standard library do Python.

**Por quê?**
- **Determinismo**: regras + KB tornam os resultados reprodutíveis (mesmo input → mesmo output).
- **Auditabilidade**: dá para explicar claramente o porquê do e-mail ter sido classificado (palavras-chave que contribuíram para o score).
- **Operação corporativa**: reduz risco de dependência externa e facilita homologação.

### Opcional: LLM como fallback (não implementado)
É possível adicionar um fallback com LLM quando a confiança ficar baixa, mas isso depende de credenciais e políticas corporativas.

## O que foi determinístico?
- Taxonomia/KB em `kb/taxonomy.json`
- Pontuação por keyword matching (assunto + conteúdo)
- Confiança calculada por separação entre scores (top1 vs top2)

## KB (base de conhecimento)
`kb/taxonomy.json` contém:
- keywords por categoria
- regras de roteamento (área, criticidade, tipo de elogio)
- parâmetros (confiança mínima, retentativas, fallback humano)

## Como rodar

### 1) Ambiente
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Gerar base fictícia
```bash
python main.py generate-data --out data/emails.csv --n 120
```

### 3) Rodar pipeline
```bash
python main.py run --input data/emails.csv --out runs/output.jsonl
```

### 4) Gerar relatório
```bash
python main.py report --db runs/triage.db --out runs/report.md --csv runs/metrics.csv
```

## Saídas
- `runs/output.jsonl`: registros classificados + roteamento + métricas por e-mail
- `runs/triage.db`: eventos e resultados (para auditoria)
- `runs/report.md` e `runs/metrics.csv`: indicadores consolidados
- `outbox/`: mock de notificações

