"""MCP server exposing SAOS judgments search as a tool.
Run with:
    python server.py          # streamable HTTP default
or
    mcp dev server.py         # local testing via Inspector
"""
import typing as _t
from datetime import date

import httpx
from mcp.server.fastmcp import FastMCP

# ---------- CONFIG ----------
SAOS_SEARCH_URL = "https://www.saos.org.pl/api/search/judgments"
SAOS_JUDGMENT_URL_TEMPLATE = "https://www.saos.org.pl/api/judgments/{judgment_id}"
TIMEOUT = 20  # seconds

mcp = FastMCP("SAOS Judgments Search", dependencies=["httpx"])


async def _fetch_json(params: dict[str, _t.Any]) -> dict[str, _t.Any]:
    """Call SAOS API.

    Przy statusie 2xx zwraca wynik JSON.
    Przy błędach 4xx/5xx zwraca strukturę diagnostyczną bez podnoszenia wyjątku,
    aby użytkownik w Cascade widział dokładny komunikat SAOS.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(SAOS_SEARCH_URL, params=params)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as exc:
        resp = exc.response
        try:
            detail: _t.Any = resp.json()
        except ValueError:
            detail = resp.text
        return {
            "error": True,
            "status": resp.status_code,
            "detail": detail,
            "params": params,
        }


# Separate helper for fixed URLs (e.g., judgment details)
async def _fetch_json_url(url: str) -> dict[str, _t.Any]:
    """Call SAOS API for a specific URL.

    Działa analogicznie do `_fetch_json`, ale przyjmuje pełny URL zamiast
    parametrów query string. Używane m.in. do pobierania szczegółów
    pojedynczego orzeczenia.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as exc:
        resp = exc.response
        try:
            detail: _t.Any = resp.json()
        except ValueError:
            detail = resp.text
        return {
            "error": True,
            "status": resp.status_code,
            "detail": detail,
            "url": url,
        }


@mcp.tool(description="Wyszukaj orzeczenia w bazie SAOS według podanych kryteriów.")
async def search_judgments(
    query: str | None = None,
    courtType: str | None = None,
    judgmentType: str | None = None,
    dateFrom: date | None = None,
    dateTo: date | None = None,
    page: int = 0,
    pageSize: int = 20,
) -> dict[str, _t.Any]:
    """Zwraca słownik JSON z wynikami wyszukiwania orzeczeń.

    Parametry odpowiadają dokumentacji SAOS. Wszystkie są opcjonalne poza limitami
    paginacji.
    """
    params: dict[str, _t.Any] = {
        "pageNumber": page,
        "pageSize": pageSize,
    }
    if query:
        params["all"] = query
    if courtType:
        params["courtType"] = courtType
    if judgmentType:
        params["judgmentType"] = judgmentType
    if dateFrom:
        params["judgmentDateFrom"] = dateFrom.strftime("%Y-%m-%d")
    if dateTo:
        params["judgmentDateTo"] = dateTo.strftime("%Y-%m-%d")

    return await _fetch_json(params)


# ---------------------------------------------------------------------------
# Judgments details endpoint
# ---------------------------------------------------------------------------

@mcp.tool(description="Pobierz pełną treść i metadane pojedynczego orzeczenia na podstawie jego ID w SAOS.")
async def get_judgment(judgment_id: int) -> dict[str, _t.Any]:
    """Zwraca szczegóły pojedynczego orzeczenia.

    Argumenty:
        judgment_id: Wewnętrzny identyfikator orzeczenia w SAOS.
    """
    url = SAOS_JUDGMENT_URL_TEMPLATE.format(judgment_id=judgment_id)
    return await _fetch_json_url(url)


if __name__ == "__main__":
    mcp.run(transport="stdio")
