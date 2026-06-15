import httpx
from .config import COUNTRIES

TIMEOUT = 8.0


async def _get(country: str, path: str, params: dict = None):
    base = COUNTRIES.get(country)
    if not base:
        return None
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{base}{path}", params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"[CENTRAL] GET {country}{path} -> {e}")
        return None


async def _post(country: str, path: str, json_body: dict = None, params: dict = None):
    base = COUNTRIES.get(country)
    if not base:
        return None
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{base}{path}", json=json_body, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"[CENTRAL] POST {country}{path} -> {e}")
        return None


async def _delete(country: str, path: str):
    base = COUNTRIES.get(country)
    if not base:
        return None
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.delete(f"{base}{path}")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"[CENTRAL] DELETE {country}{path} -> {e}")
        return None


# ---------- Lectures ----------
async def get_lots(country):            return await _get(country, "/lots") or []
async def get_lots_fifo(country):       return await _get(country, "/lots/fifo") or []
async def get_alerts(country):          return await _get(country, "/alerts") or []
async def get_alerts_critical(country): return await _get(country, "/alerts/critical") or []
async def get_mesures(country, limit=50): return await _get(country, "/mesures", {"limit": limit}) or []
async def get_kpis(country):            return await _get(country, "/kpis")
async def get_entrepots(country):       return await _get(country, "/entrepots") or []


# ---------- Écritures (proxy vers le pays) ----------
async def create_lot(country, body):        return await _post(country, "/lots", json_body=body)
async def create_mesure(country, body):     return await _post(country, "/mesures", json_body=body)
async def delete_lot(country, lot_id):      return await _delete(country, f"/lots/{lot_id}")
async def check_expiration(country):        return await _post(country, "/lots/check-expiration")
