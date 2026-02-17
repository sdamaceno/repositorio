# Proposta de Aplicativo de Inteligência de Preços para Compras Públicas (PNCP)

## 1) Visão geral

Este documento descreve um aplicativo **web com opção desktop empacotada** (via Tauri/Electron) para pesquisa e justificativa de preços em contratações públicas, com foco em dados de licitações **realizadas/concluídas** no PNCP.

Objetivos centrais:
- reduzir o esforço operacional de pesquisa de preços;
- padronizar a coleta de evidências para ETP/TR e fase preparatória;
- aumentar rastreabilidade e conformidade com a Lei nº 14.133/2021;
- evitar práticas de coleta agressiva, respeitando limites técnicos e termos de uso do PNCP.

---

## 2) Arquitetura proposta (alto nível)

### 2.1 Escolha arquitetural

**Arquitetura recomendada: Web app modular + serviços assíncronos de ingestão**

- **Frontend (SPA):** busca, filtros, comparativos, dashboards e geração de relatório.
- **API Backend:** autenticação, consultas, regras de negócio, trilhas de auditoria.
- **Pipeline de Coleta/Normalização:** workers assíncronos para ingestão incremental e parser de múltiplos formatos.
- **Camada Analítica:** cálculo estatístico, detecção de outliers, formação de cesta de preços e ranking de fornecedores.
- **Armazenamento híbrido:** relacional para dados estruturados e object storage para anexos (PDF/planilhas).

### 2.2 Diagrama lógico (texto)

```text
[Usuário] -> [Frontend React]
               |
               v
           [API FastAPI]
               |
   +-----------+-------------------+
   |                               |
   v                               v
[PostgreSQL]                 [Fila Redis/RabbitMQ]
   |                               |
   |                               v
   |                         [Workers de Coleta]
   |                               |
   |                    +----------+-----------+
   |                    |                      |
   v                    v                      v
[Camada Analítica]  [Conectores PNCP]    [Parser Multi-formato]
   |                    |                      |
   +--------------------+----------------------+
                        |
                        v
               [Object Storage (S3/MinIO)]
```

### 2.3 Módulos de domínio

1. **Módulo Pesquisa de Itens**
   - busca por descrição, CATMAT/CATSER/código interno, unidade, faixa de valor;
   - filtros por período, órgão, UF, modalidade, situação da contratação.

2. **Módulo Coleta e Enriquecimento**
   - ingestão de dados oficiais (API/feeds/documentos públicos permitidos);
   - extração de metadados de itens, lotes, adjudicação/homologação;
   - deduplicação e versionamento.

3. **Módulo Estatístico e Benchmarks**
   - média, mediana, p25/p75, mínimo/máximo, desvio padrão, IQR;
   - séries temporais e comparação por recorte regional/porte/órgão;
   - score de confiabilidade da amostra.

4. **Módulo de Conformidade**
   - validações normativas configuráveis;
   - alertas de risco (amostra insuficiente, fonte antiga, itens heterogêneos);
   - trilha de auditoria com log de consultas, filtros e versão dos dados.

5. **Módulo Relatórios e Evidências**
   - relatório para instrução processual (PDF/HTML assinado);
   - links para origem e anexos de comprovação;
   - anexação ao SEI/ERP (integrações futuras).

---

## 3) Fluxo de dados e processos

## 3.1 Pipeline de ingestão

1. **Descoberta de fontes oficiais**
   - mapear endpoints/documentos públicos disponíveis e permitidos.
2. **Coleta incremental**
   - janela temporal diária e retroativa;
   - paginação resiliente com checkpoint.
3. **Parsing multi-formato**
   - JSON/XML/HTML/PDF/XLSX -> esquema canônico.
4. **Normalização semântica**
   - padronização de unidade, moeda, descrição e códigos.
5. **Validação de qualidade**
   - consistência de campos obrigatórios;
   - rejeição/flag de registros incompletos.
6. **Persistência + indexação de busca**
   - gravação no banco + índice textual/fuzzy.
7. **Agregação analítica**
   - cálculo de estatísticas por item e contexto.
8. **Exposição via API**
   - frontend consome resultados, gráficos e justificativa.

## 3.2 Fluxo de uso do analista de compras

1. Usuário informa item (ex.: “cimento CP II 50kg”).
2. Define filtros (últimos 12 meses, região, modalidade, situação concluída).
3. Sistema retorna amostra consolidada e distribuições.
4. Usuário ajusta qualidade da cesta (remove outliers justificados).
5. Sistema gera relatório com fundamentação, estatísticas e fontes.

---

## 4) Stack tecnológica recomendada e justificativas

- **Frontend:** React + TypeScript + Material UI
  - alta produtividade para dashboards, tabelas complexas e filtros avançados.
- **Backend/API:** Python FastAPI
  - desempenho bom para APIs, tipagem com Pydantic e fácil integração com ciência de dados.
- **Coleta assíncrona:** Celery/RQ + Redis (ou RabbitMQ)
  - controle de filas, retentativas, backoff e escalabilidade horizontal.
- **Extração/Parsing:** httpx, BeautifulSoup/lxml, pandas, openpyxl, pypdf
  - cobertura robusta de formatos heterogêneos.
- **Banco de dados principal:** PostgreSQL
  - integridade relacional, JSONB para flexibilidade, ótimo custo-benefício.
- **Busca textual/fuzzy:** PostgreSQL trigram (`pg_trgm`) ou OpenSearch
  - melhora matching de descrições com erros/variações.
- **Object storage:** MinIO/S3
  - armazenamento de anexos e artefatos de evidência.
- **Observabilidade:** Prometheus + Grafana + Sentry
  - monitoração de jobs, erros de parsing e desempenho.
- **Empacotamento desktop opcional:** Tauri
  - cliente local para órgãos com restrições de instalação.

---

## 5) Plano para “quebra de barreiras” (compliance-first)

> “Quebra de barreiras” aqui significa **superar dificuldades técnicas legítimas de acesso e estruturação de dados públicos**, sem burlar autenticação, segurança ou termos de uso.

### 5.1 Barreiras comuns e mitigação

1. **Paginação complexa e resultados truncados**
   - crawler por estado de paginação com checkpoint persistente;
   - idempotência por chave natural do registro.

2. **Rate limit / indisponibilidade temporária**
   - retry exponencial com jitter;
   - controle de concorrência e janela de coleta fora de pico.

3. **Dados inconsistentes entre formatos**
   - precedência de fonte (hierarquia de confiabilidade);
   - reconciliação por regras e auditoria de divergências.

4. **Documentos anexos sem padrão**
   - extração de texto com fallback por OCR quando permitido;
   - validação humana assistida para casos de baixa confiança.

5. **Descrições de item com baixa padronização**
   - normalização lexical (stopwords técnicas, stemming leve);
   - similaridade híbrida (trigram + embeddings) com score explicável.

6. **Mudanças frequentes de layout/endpoints**
   - conectores versionados por fonte;
   - testes de contrato (contract tests) e alertas de quebra.

### 5.2 Governança técnica para não sobrecarregar o PNCP

- cache local por período e parâmetros;
- ingestão incremental em vez de varreduras completas repetitivas;
- limitação de QPS e fila com prioridade;
- respeito a robots/termos de uso e boas práticas de acesso.

---

## 6) Modelo de dados (resumo)

Entidades principais:
- `licitacao` (id_pncp, órgão, modalidade, situação, datas, link origem)
- `item_licitacao` (descrição original, descrição normalizada, unidade, quantidade)
- `resultado_item` (valor unitário homologado/adjudicado, fornecedor, marca/modelo)
- `fornecedor` (CNPJ, razão social, porte)
- `fonte_documental` (tipo arquivo, hash, url, data coleta)
- `auditoria_consulta` (usuário, filtros, versão dataset, timestamp)
- `regra_conformidade` e `alerta_conformidade`

Índices:
- btree para filtros temporais/órgão/modalidade;
- GIN/trgm para busca textual fuzzy;
- partição mensal para alto volume histórico.

---

## 7) UI/UX e wireframes (texto)

## 7.1 Tela inicial de pesquisa

```text
+--------------------------------------------------------------------------------+
| [Logo] Inteligência de Preços PNCP                           [Usuário] [Ajuda] |
+--------------------------------------------------------------------------------+
| Busca do item: [ cimento cp ii 50kg                          ] [Pesquisar]      |
| Filtros: [Período v] [Órgão v] [UF v] [Modalidade v] [Situação: Concluída v]   |
|          [Faixa de valor min-max] [Unidade] [Fornecedor] [Apenas homologadas]  |
+--------------------------------------------------------------------------------+
| Resultados (412)                                                               |
|--------------------------------------------------------------------------------|
| Item normalizado | Mediana | Média | Mín | Máx | Amostra | Fornecedores | Ver  |
| CIMENTO CP II... | 38,20   | 39,10 | 31  | 51  | 117     | 34           | [>]  |
+--------------------------------------------------------------------------------+
```

## 7.2 Tela de análise detalhada

```text
+--------------------------------------------------------------------------------+
| Item: CIMENTO CP II 50KG  | Score de confiabilidade: 0,87 | [Gerar relatório] |
+--------------------------------------------------------------------------------+
| [Gráfico Boxplot] [Histograma] [Série temporal por mês]                         |
|--------------------------------------------------------------------------------|
| Tabela de evidências                                                            |
| Data | Órgão | Modalidade | Fornecedor | Valor Unit. | Situação | Link Origem |
| ...                                                                          [>]|
+--------------------------------------------------------------------------------+
| Alertas de conformidade:                                                        |
| - 12% da amostra com descrição ambígua (revisão recomendada).                  |
| - 3 registros fora de 1,5 IQR (outliers sinalizados).                          |
+--------------------------------------------------------------------------------+
```

## 7.3 Tela de relatório

```text
+------------------------------ Relatório de Justificativa ----------------------+
| Identificação do item | metodologia | estatísticas | evidências | conclusão    |
| [Editar texto padrão normativo] [Exportar PDF] [Assinar] [Compartilhar link]  |
+--------------------------------------------------------------------------------+
```

---

## 8) Estratégias de conformidade legal e normativa

## 8.1 Base normativa embarcada (motor de regras)

- parametrizar regras vinculadas a:
  - Lei nº 14.133/2021 (fase preparatória, pesquisa de preços e motivação);
  - regulamentos infralegais e instruções normativas vigentes;
  - orientações de órgãos de controle aplicáveis.

## 8.2 Controles de conformidade no produto

1. **Checklist obrigatório antes de exportar relatório**
   - mínimo de evidências por item;
   - recência da amostra;
   - justificativa para exclusão de outliers.

2. **Rastreabilidade completa**
   - versionamento de dataset e parâmetros usados na pesquisa;
   - hash dos documentos anexos e carimbo temporal.

3. **Transparência metodológica**
   - relatório sempre explicita método estatístico aplicado;
   - distinção entre preço coletado e preço de referência sugerido.

4. **Alertas preventivos de risco jurídico**
   - baixa competitividade (poucos fornecedores);
   - concentração excessiva em único fornecedor;
   - amostra desatualizada para itens voláteis.

## 8.3 Governança e LGPD

- coletar apenas dados necessários à finalidade pública;
- perfis de acesso por papel (comprador, auditor, gestor);
- retenção e descarte conforme política institucional.

---

## 9) Roadmap de implementação

**Fase 1 (MVP - 8 a 12 semanas)**
- busca de item, filtros essenciais, ingestão de fontes prioritárias;
- estatísticas básicas + relatório simples com links de origem.

**Fase 2 (12 a 20 semanas)**
- fuzzy search avançado, dashboards, alertas de conformidade;
- trilha de auditoria completa e melhoria de qualidade dos dados.

**Fase 3 (20+ semanas)**
- integrações corporativas (SEI/ERP), assinatura digital, motor avançado de regras.

---

## 10) Métricas de sucesso

- redução do tempo médio de pesquisa de preços;
- aumento da rastreabilidade (percentual de relatórios com evidência completa);
- taxa de reaproveitamento de cestas de preços;
- redução de apontamentos em auditorias por falha metodológica.

---

## 11) Restrições e boas práticas operacionais

- respeitar termos de uso, política de privacidade e limites técnicos do PNCP;
- evitar coleta agressiva (throttling obrigatório);
- priorizar dados de licitações **realizadas/concluídas** para justificativa de preços.

