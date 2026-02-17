from __future__ import annotations

from datetime import date, timedelta
from difflib import SequenceMatcher

from app.schemas import ComplianceAlert, LicitacaoItem, PriceStats
from app.services.normalization import normalize_text


FUZZY_THRESHOLD = 0.55


def fuzzy_match(term: str, target: str) -> bool:
    term_norm = normalize_text(term)
    target_norm = normalize_text(target)

    if not term_norm:
        return False
    if term_norm in target_norm:
        return True

    return SequenceMatcher(a=term_norm, b=target_norm).ratio() >= FUZZY_THRESHOLD


def compute_price_stats(items: list[LicitacaoItem]) -> PriceStats:
    return PriceStats.from_values(item.valor_unitario for item in items)


def compute_compliance_alerts(items: list[LicitacaoItem], stats: PriceStats) -> list[ComplianceAlert]:
    alerts: list[ComplianceAlert] = []

    if len(items) < 3:
        alerts.append(
            ComplianceAlert(
                nivel="warning",
                codigo="AMOSTRA_INSUFICIENTE",
                mensagem="A amostra contém menos de 3 evidências. Recomenda-se ampliar o período ou filtros.",
            )
        )

    if items:
        cutoff = date.today() - timedelta(days=180)
        old_records = [i for i in items if i.data_homologacao < cutoff]
        if len(old_records) / len(items) > 0.4:
            alerts.append(
                ComplianceAlert(
                    nivel="warning",
                    codigo="RECENCIA_BAIXA",
                    mensagem="Mais de 40% dos registros são antigos (>180 dias). Avalie atualização da cesta.",
                )
            )

    if stats.media > 0 and stats.desvio_padrao / stats.media > 0.5:
        alerts.append(
            ComplianceAlert(
                nivel="risk",
                codigo="ALTA_VARIABILIDADE",
                mensagem="Alta dispersão de preços detectada. Revise outliers e comparabilidade dos itens.",
            )
        )

    return alerts
