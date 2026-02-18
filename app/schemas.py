from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from statistics import mean, median, stdev
from typing import Iterable


@dataclass
class LicitacaoItem:
    id: str
    descricao: str
    descricao_normalizada: str
    unidade: str
    valor_unitario: float
    orgao: str
    modalidade: str
    status: str
    data_homologacao: date
    fornecedor: str
    link_origem: str


@dataclass
class SearchFilters:
    termo: str
    data_inicio: date | None = None
    data_fim: date | None = None
    orgao: str | None = None
    modalidade: str | None = None
    status: str | None = None
    valor_min: float | None = None
    valor_max: float | None = None
    limite: int = 100


@dataclass
class PriceStats:
    quantidade: int
    media: float
    mediana: float
    minimo: float
    maximo: float
    desvio_padrao: float

    @classmethod
    def from_values(cls, values: Iterable[float]) -> "PriceStats":
        values = list(values)
        if not values:
            return cls(0, 0, 0, 0, 0, 0)

        spread = stdev(values) if len(values) > 1 else 0
        return cls(
            quantidade=len(values),
            media=round(mean(values), 2),
            mediana=round(median(values), 2),
            minimo=round(min(values), 2),
            maximo=round(max(values), 2),
            desvio_padrao=round(spread, 2),
        )


@dataclass
class ComplianceAlert:
    nivel: str
    codigo: str
    mensagem: str


@dataclass
class SearchResponse:
    filtros: SearchFilters
    gerado_em: datetime
    itens: list[LicitacaoItem] = field(default_factory=list)
    estatisticas: PriceStats = field(default_factory=lambda: PriceStats(0, 0, 0, 0, 0, 0))
    alertas: list[ComplianceAlert] = field(default_factory=list)


@dataclass
class ReportResponse:
    conteudo_markdown: str
    gerado_em: datetime
