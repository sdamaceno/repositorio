from datetime import date

from app.schemas import LicitacaoItem
from app.services.analytics import compute_price_stats, fuzzy_match
from app.services.normalization import normalize_text


def test_normalize_text():
    assert normalize_text("Cimento, CP II 50KG") == "cimento cp ii 50kg"


def test_fuzzy_match_variations():
    assert fuzzy_match("cimento cp2 50kg", "Cimento Portland CP II 50 KG")


def test_stats_generation():
    items = [
        LicitacaoItem(
            id="1",
            descricao="x",
            descricao_normalizada="x",
            unidade="un",
            valor_unitario=10,
            orgao="a",
            modalidade="pregao",
            status="concluida",
            data_homologacao=date(2025, 1, 1),
            fornecedor="f1",
            link_origem="http://example.com/1",
        ),
        LicitacaoItem(
            id="2",
            descricao="x",
            descricao_normalizada="x",
            unidade="un",
            valor_unitario=20,
            orgao="a",
            modalidade="pregao",
            status="concluida",
            data_homologacao=date(2025, 1, 2),
            fornecedor="f2",
            link_origem="http://example.com/2",
        ),
    ]

    stats = compute_price_stats(items)
    assert stats.quantidade == 2
    assert stats.media == 15
    assert stats.mediana == 15
