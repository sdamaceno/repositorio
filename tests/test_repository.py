from datetime import date

from app.schemas import LicitacaoItem, SearchFilters
from app.services.normalization import normalize_text
from app.services.repository import InMemoryRepository


def test_status_filter_uses_exact_normalized_match():
    repo = InMemoryRepository()
    repo.items.append(
        LicitacaoItem(
            id="PNCP-004",
            descricao="Cimento CP II 50kg - lote extra",
            descricao_normalizada=normalize_text("Cimento CP II 50kg - lote extra"),
            unidade="saco",
            valor_unitario=39.0,
            orgao="Prefeitura Municipal Delta",
            modalidade="Pregão Eletrônico",
            status="nao concluida",
            data_homologacao=date(2025, 7, 10),
            fornecedor="Fornecedor D",
            link_origem="https://pncp.gov.br/app/editais/PNCP-004",
        )
    )

    filters = SearchFilters(termo="cimento", status="Concluída")

    results = repo.search(filters)

    assert len(results) == 3
    assert all(normalize_text(item.status) == "concluida" for item in results)
