from __future__ import annotations

from datetime import datetime

from app.schemas import ComplianceAlert, LicitacaoItem, PriceStats


def build_markdown_report(
    termo: str,
    itens: list[LicitacaoItem],
    stats: PriceStats,
    alertas: list[ComplianceAlert],
) -> str:
    lines = [
        f"# Relatório de Justificativa de Preços - {termo}",
        "",
        f"Gerado em: {datetime.utcnow().isoformat()}Z",
        "",
        "## Resumo estatístico",
        f"- Quantidade de evidências: {stats.quantidade}",
        f"- Média: R$ {stats.media}",
        f"- Mediana: R$ {stats.mediana}",
        f"- Mínimo: R$ {stats.minimo}",
        f"- Máximo: R$ {stats.maximo}",
        f"- Desvio padrão: R$ {stats.desvio_padrao}",
        "",
        "## Evidências",
    ]

    for item in itens:
        lines.append(
            f"- {item.data_homologacao} | {item.orgao} | {item.fornecedor} | R$ {item.valor_unitario} | [origem]({item.link_origem})"
        )

    if alertas:
        lines.extend(["", "## Alertas de conformidade"])
        for alerta in alertas:
            lines.append(f"- [{alerta.nivel}] {alerta.codigo}: {alerta.mensagem}")

    lines.extend(
        [
            "",
            "## Observação legal",
            "Este relatório é um subsídio técnico e deve ser validado pela área demandante conforme Lei nº 14.133/2021 e normativos locais.",
        ]
    )

    return "\n".join(lines)
