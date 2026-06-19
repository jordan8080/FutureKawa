"""Client HTTP vers les backends pays + helpers de routage/consolidation."""
import asyncio
import re

import httpx

from . import config
from .config import COUNTRIES

_client = httpx.AsyncClient(timeout=10.0)


async def close_client():
    await _client.aclose()


def country_from_id(identifier: str):
    """Déduit le pays à partir d'un id (w-br-1, FK-BR-SP-001, BR-AL-xxxx)."""
    code_map = config.code_to_country()
    for token in re.split(r"[-_]", identifier.upper()):
        if token in code_map:
            return code_map[token]
    return None


async def call(country: str, method: str, path: str, *, params=None, json=None):
    """Appel d'un backend pays. Renvoie (status_code, data)."""
    base = COUNTRIES[country]["url"]
    resp = await _client.request(method, f"{base}{path}", params=params, json=json)
    data = resp.json() if resp.content else None
    return resp.status_code, data


async def get(country: str, path: str, params=None):
    _, data = await call(country, "GET", path, params=params)
    return data


async def fan_out(method: str, path: str, *, params=None):
    """Interroge les 3 pays en parallèle. Renvoie la liste des résultats (pays joignables)."""
    async def _one(country):
        try:
            _, data = await call(country, method, path, params=params)
            return data
        except Exception as exc:  # noqa: BLE001
            print(f"[CENTRAL] {country} injoignable sur {path}: {exc}", flush=True)
            return None

    results = await asyncio.gather(*[_one(c) for c in COUNTRIES])
    return [r for r in results if r is not None]


async def fan_out_concat(path: str, *, params=None):
    """Concatène les listes renvoyées par chaque pays."""
    merged = []
    for data in await fan_out("GET", path, params=params):
        if isinstance(data, list):
            merged.extend(data)
    return merged
