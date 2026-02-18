# PNCP Pricing Intelligence (MVP)

Implementação inicial da proposta de aplicativo para pesquisa de preços em licitações concluídas no PNCP.

## Entregas implementadas

- API FastAPI com endpoints:
  - `POST /api/search`: busca avançada com filtros e fuzzy matching.
  - `POST /api/report`: gera relatório de justificativa em Markdown.
  - `GET /health`: healthcheck.
- Camada de análise com:
  - estatísticas (média, mediana, mínimo, máximo, desvio padrão);
  - alertas de conformidade (amostra insuficiente, baixa recência, alta variabilidade).
- Cliente PNCP com estratégia educada:
  - limite de QPS;
  - retry com backoff exponencial;
  - paginação incremental.
- Testes unitários para normalização, fuzzy e estatística.

## Executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Exemplo de requisição

```bash
curl -X POST http://127.0.0.1:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{
    "termo": "cimento cp2 50kg",
    "status": "concluida",
    "limite": 50
  }'
```

## Observações

- Repositório usa `InMemoryRepository` para demonstração funcional.
- Próximo passo recomendado: trocar repositório em memória por PostgreSQL + ingestão real do PNCP.
