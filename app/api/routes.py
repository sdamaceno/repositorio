from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.schemas import ReportResponse, SearchFilters, SearchResponse
from app.services.analytics import compute_compliance_alerts, compute_price_stats
from app.services.reporting import build_markdown_report
from app.services.repository import InMemoryRepository

router = APIRouter(prefix="/api", tags=["pncp-pricing"])


def get_repo() -> InMemoryRepository:
    return InMemoryRepository()


@router.post("/search", response_model=SearchResponse)
def search_items(filters: SearchFilters, repo: InMemoryRepository = Depends(get_repo)) -> SearchResponse:
    items = repo.search(filters)
    stats = compute_price_stats(items)
    alerts = compute_compliance_alerts(items, stats)
    return SearchResponse(
        filtros=filters,
        gerado_em=datetime.utcnow(),
        itens=items,
        estatisticas=stats,
        alertas=alerts,
    )


@router.post("/report", response_model=ReportResponse)
def generate_report(filters: SearchFilters, repo: InMemoryRepository = Depends(get_repo)) -> ReportResponse:
    items = repo.search(filters)
    stats = compute_price_stats(items)
    alerts = compute_compliance_alerts(items, stats)
    report = build_markdown_report(filters.termo, items, stats, alerts)
    return ReportResponse(conteudo_markdown=report, gerado_em=datetime.utcnow())
