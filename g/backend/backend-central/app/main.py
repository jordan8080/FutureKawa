"""Backend CENTRAL (siège) — sans base. Consolide les 3 backends pays.

Le frontend parle UNIQUEMENT à ce service. Toutes les routes sont préfixées /api.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from . import country_client as cc
from .config import CORS_ORIGINS, COUNTRIES


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await cc.close_client()


app = FastAPI(title="FutureKawa — Backend Central", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Le front lit `err.message` → on aligne le format des erreurs.
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


def _require_country(country: str):
    if country not in COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Pays inconnu: {country}")


async def _route_by_id(identifier: str, method: str, path: str, *, json=None):
    """Route une requête vers le bon pays d'après l'id ; 404 si introuvable."""
    country = cc.country_from_id(identifier)
    if country is None:
        raise HTTPException(status_code=404, detail=f"Ressource introuvable: {identifier}")
    status, data = await cc.call(country, method, path, json=json)
    if status >= 400:
        raise HTTPException(status_code=status, detail=(data or {}).get("detail", "Erreur"))
    return data


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "central"}


@app.get("/api/countries")
async def list_countries():
    return [{k: v for k, v in c.items() if k != "url"} for c in COUNTRIES.values()]


@app.post("/api/countries", status_code=201)
async def add_country(request: Request):
    """Enregistre un pays dans le routage central (registre en mémoire).

    Limite : n'instancie PAS de backend/base/broker — l'`url` doit pointer vers
    un backend pays déjà déployé. La suppression retire seulement du routage.
    """
    body = await request.json()
    missing = [f for f in ("id", "name", "code", "url") if not body.get(f)]
    if missing:
        raise HTTPException(status_code=400, detail=f"Champs manquants: {missing}")
    if body["id"] in COUNTRIES:
        raise HTTPException(status_code=409, detail="Pays déjà enregistré")
    country = {
        "id": body["id"], "name": body["name"], "code": body["code"].upper(),
        "emoji": body.get("emoji", "🏳️"), "url": body["url"],
    }
    config.add_country(country)
    return {k: v for k, v in country.items() if k != "url"}


@app.delete("/api/countries/{country_id}")
async def remove_country(country_id: str):
    if country_id not in COUNTRIES:
        raise HTTPException(status_code=404, detail="Pays inconnu")
    config.remove_country(country_id)
    return {"ok": True, "id": country_id}


# ─── Lots ─────────────────────────────────────────────────────────────────────
@app.get("/api/lots")
async def all_lots():
    lots = await cc.fan_out_concat("/lots")
    return sorted(lots, key=lambda l: l.get("storedAt") or "")  # FIFO global


@app.get("/api/countries/{country}/lots")
async def country_lots(country: str):
    _require_country(country)
    return await cc.get(country, "/lots")


@app.get("/api/warehouses/{warehouse_id}/lots")
async def warehouse_lots(warehouse_id: str):
    return await _route_by_id(warehouse_id, "GET", f"/warehouses/{warehouse_id}/lots")


@app.get("/api/lots/{lot_id}")
async def lot_detail(lot_id: str):
    country = cc.country_from_id(lot_id)
    if country is None:
        return None
    return await cc.get(country, f"/lots/{lot_id}")


@app.post("/api/lots", status_code=201)
async def create_lot(request: Request):
    body = await request.json()
    country = body.get("country") or cc.country_from_id(body.get("warehouseId", ""))
    if country not in COUNTRIES:
        raise HTTPException(status_code=400, detail="Pays manquant ou invalide")
    status, data = await cc.call(country, "POST", "/lots", json=body)
    if status >= 400:
        raise HTTPException(status_code=status, detail=(data or {}).get("detail", "Erreur"))
    return data


@app.patch("/api/lots/{lot_id}/status")
async def update_lot_status(lot_id: str, request: Request):
    body = await request.json()
    return await _route_by_id(lot_id, "PATCH", f"/lots/{lot_id}/status", json=body)


@app.delete("/api/lots/{lot_id}")
async def delete_lot(lot_id: str):
    return await _route_by_id(lot_id, "DELETE", f"/lots/{lot_id}")


# ─── Capteurs ─────────────────────────────────────────────────────────────────
@app.get("/api/warehouses/{warehouse_id}/sensors")
async def warehouse_sensors(warehouse_id: str, limit: int | None = None):
    country = cc.country_from_id(warehouse_id)
    if country is None:
        return []
    params = {"limit": limit} if limit else None
    return await cc.get(country, f"/warehouses/{warehouse_id}/sensors", params=params)


@app.get("/api/countries/{country}/sensors/latest")
async def country_sensors_latest(country: str):
    _require_country(country)
    return await cc.get(country, "/sensors/latest")


@app.get("/api/sensors/current")
async def sensors_current():
    return await cc.fan_out_concat("/sensors/current")


# ─── Entrepôts ────────────────────────────────────────────────────────────────
@app.get("/api/warehouses")
async def all_warehouses():
    return await cc.fan_out_concat("/warehouses")


@app.get("/api/countries/{country}/warehouses")
async def country_warehouses(country: str):
    _require_country(country)
    return await cc.get(country, "/warehouses")


@app.post("/api/warehouses", status_code=201)
async def create_warehouse(request: Request):
    body = await request.json()
    country = body.get("country") or cc.country_from_id(body.get("id", ""))
    if country not in COUNTRIES:
        raise HTTPException(status_code=400, detail="Pays manquant ou invalide")
    status, data = await cc.call(country, "POST", "/warehouses", json=body)
    if status >= 400:
        raise HTTPException(status_code=status, detail=(data or {}).get("detail", "Erreur"))
    return data


@app.get("/api/warehouses/{warehouse_id}")
async def warehouse_detail(warehouse_id: str):
    country = cc.country_from_id(warehouse_id)
    if country is None:
        return None
    return await cc.get(country, f"/warehouses/{warehouse_id}")


@app.delete("/api/warehouses/{warehouse_id}")
async def delete_warehouse(warehouse_id: str):
    return await _route_by_id(warehouse_id, "DELETE", f"/warehouses/{warehouse_id}")


# ─── Alertes ──────────────────────────────────────────────────────────────────
@app.get("/api/alerts")
async def all_alerts(country: str | None = None, type: str | None = None,
                     status: str | None = None):
    params = {k: v for k, v in {"type": type, "status": status}.items() if v}
    if country and country != "all":
        _require_country(country)
        alerts = await cc.get(country, "/alerts", params=params) or []
    else:
        alerts = await cc.fan_out_concat("/alerts", params=params)
    return sorted(alerts, key=lambda a: a.get("createdAt") or "", reverse=True)


@app.get("/api/alerts/count")
async def alerts_count():
    active = total = 0
    for data in await cc.fan_out("GET", "/alerts/count"):
        active += (data or {}).get("active", 0)
        total += (data or {}).get("total", 0)
    return {"active": active, "total": total}


@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    return await _route_by_id(alert_id, "POST", f"/alerts/{alert_id}/resolve")


# ─── Consolidation / KPIs ─────────────────────────────────────────────────────
@app.get("/api/dashboard")
async def dashboard():
    per_country = []
    totals = {"totalLots": 0, "conformeLots": 0, "perimeLots": 0, "activeAlerts": 0}
    for data in await cc.fan_out("GET", "/kpis"):
        if not data:
            continue
        per_country.append(data)
        for k in totals:
            totals[k] += data.get(k, 0)
    totals["conformePct"] = (
        round(totals["conformeLots"] / totals["totalLots"] * 100)
        if totals["totalLots"] else 100
    )
    return {"totals": totals, "countries": per_country}


@app.get("/api/countries/{country}/kpis")
async def country_kpis(country: str):
    _require_country(country)
    return await cc.get(country, "/kpis")


@app.get("/api/countries/{country}/fifo")
async def country_fifo(country: str, limit: int = 10):
    _require_country(country)
    return await cc.get(country, "/fifo", params={"limit": limit})
