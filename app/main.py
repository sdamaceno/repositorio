from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="PNCP Pricing Intelligence",
    version="0.1.0",
    description="API MVP para pesquisa de preços de licitações concluídas e geração de justificativas.",
)

app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
