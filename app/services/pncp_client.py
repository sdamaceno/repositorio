from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class PNCPClientConfig:
    base_url: str = "https://pncp.gov.br/api"
    timeout_s: float = 20.0
    max_retries: int = 3
    qps_limit: float = 2.0


class PNCPClient:
    """Cliente HTTP com comportamento educado para coleta incremental.

    - limita taxa de chamadas (qps_limit)
    - aplica retry com backoff exponencial
    - itera paginação sem sobrecarregar a origem
    """

    def __init__(self, cfg: PNCPClientConfig | None = None) -> None:
        self.cfg = cfg or PNCPClientConfig()
        self._min_interval = 1.0 / self.cfg.qps_limit
        self._last_call = 0.0

    async def _throttle(self) -> None:
        now = asyncio.get_running_loop().time()
        remaining = self._min_interval - (now - self._last_call)
        if remaining > 0:
            await asyncio.sleep(remaining)
        self._last_call = asyncio.get_running_loop().time()

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}

        async with httpx.AsyncClient(base_url=self.cfg.base_url, timeout=self.cfg.timeout_s) as client:
            for attempt in range(self.cfg.max_retries + 1):
                await self._throttle()
                try:
                    response = await client.get(path, params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError:
                    if attempt >= self.cfg.max_retries:
                        raise
                    await asyncio.sleep(2**attempt)

        return {}

    async def paged_fetch(self, path: str, initial_params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        params = dict(initial_params or {})
        page = 1
        records: list[dict[str, Any]] = []

        while True:
            params["pagina"] = page
            payload = await self.get_json(path, params=params)
            page_items = payload.get("data", [])
            if not page_items:
                break
            records.extend(page_items)
            page += 1

        return records
