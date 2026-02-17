from __future__ import annotations

from datetime import date

from app.schemas import LicitacaoItem, SearchFilters
from app.services.analytics import fuzzy_match
from app.services.normalization import normalize_text


class InMemoryRepository:
    """Repositório de demonstração para o MVP.

    Em produção, substituir por PostgreSQL com índices trgm/GIN.
    """

    def __init__(self) -> None:
        self.items = [
            LicitacaoItem(
                id="PNCP-001",
                descricao="Cimento CP II 50kg",
                descricao_normalizada=normalize_text("Cimento CP II 50kg"),
                unidade="saco",
                valor_unitario=38.2,
                orgao="Prefeitura Municipal Alfa",
                modalidade="Pregão Eletrônico",
                status="concluida",
                data_homologacao=date(2025, 7, 8),
                fornecedor="Fornecedor A",
                link_origem="https://pncp.gov.br/app/editais/PNCP-001",
            ),
            LicitacaoItem(
                id="PNCP-002",
                descricao="Cimento Portland CP2 50 KG",
                descricao_normalizada=normalize_text("Cimento Portland CP2 50 KG"),
                unidade="saco",
                valor_unitario=40.1,
                orgao="Prefeitura Municipal Beta",
                modalidade="Concorrência",
                status="concluida",
                data_homologacao=date(2025, 5, 12),
                fornecedor="Fornecedor B",
                link_origem="https://pncp.gov.br/app/editais/PNCP-002",
            ),
            LicitacaoItem(
                id="PNCP-003",
                descricao="Cimento CP II saco 50kg",
                descricao_normalizada=normalize_text("Cimento CP II saco 50kg"),
                unidade="saco",
                valor_unitario=35.9,
                orgao="Governo Estadual Gama",
                modalidade="Pregão Eletrônico",
                status="concluida",
                data_homologacao=date(2024, 12, 10),
                fornecedor="Fornecedor C",
                link_origem="https://pncp.gov.br/app/editais/PNCP-003",
            ),
        ]

    def search(self, filters: SearchFilters) -> list[LicitacaoItem]:
        results = [x for x in self.items if fuzzy_match(filters.termo, x.descricao)]

        if filters.data_inicio:
            results = [x for x in results if x.data_homologacao >= filters.data_inicio]
        if filters.data_fim:
            results = [x for x in results if x.data_homologacao <= filters.data_fim]
        if filters.orgao:
            orgao = normalize_text(filters.orgao)
            results = [x for x in results if orgao in normalize_text(x.orgao)]
        if filters.modalidade:
            modalidade = normalize_text(filters.modalidade)
            results = [x for x in results if modalidade in normalize_text(x.modalidade)]
        if filters.status:
            status = normalize_text(filters.status)
            results = [x for x in results if status in normalize_text(x.status)]
        if filters.valor_min is not None:
            results = [x for x in results if x.valor_unitario >= filters.valor_min]
        if filters.valor_max is not None:
            results = [x for x in results if x.valor_unitario <= filters.valor_max]

        return results[: filters.limite]
