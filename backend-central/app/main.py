from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from .config import COUNTRIES, COUNTRY_NAMES
from . import country_client as cc

app = FastAPI(title="FutureKawa Central API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _check(country: str):
    if country not in COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Pays '{country}' non connecté")


# ========================
# INFOS
# ========================

@app.get("/")
def root():
    return {
        "message": "FutureKawa Central Backend",
        "pays_connectes": list(COUNTRIES.keys()),
        "status": "running"
    }


@app.get("/countries")
def list_countries():
    return [
        {"code": code, "nom": COUNTRY_NAMES.get(code, code)}
        for code in COUNTRIES
    ]


# ========================
# LECTURES PAR PAYS
# ========================

@app.get("/countries/{country}/lots")
async def c_lots(country: str):
    _check(country)
    return await cc.get_lots(country)


@app.get("/countries/{country}/lots/fifo")
async def c_fifo(country: str):
    _check(country)
    return await cc.get_lots_fifo(country)


@app.get("/countries/{country}/mesures")
async def c_mesures(country: str, limit: int = 50):
    _check(country)
    return await cc.get_mesures(country, limit)


@app.get("/countries/{country}/alerts")
async def c_alerts(country: str):
    _check(country)
    return await cc.get_alerts(country)


@app.get("/countries/{country}/alerts/critical")
async def c_alerts_crit(country: str):
    _check(country)
    return await cc.get_alerts_critical(country)


@app.get("/countries/{country}/kpis")
async def c_kpis(country: str):
    _check(country)
    return await cc.get_kpis(country)


@app.get("/countries/{country}/entrepots")
async def c_entrepots(country: str):
    _check(country)
    return await cc.get_entrepots(country)


@app.get("/countries/{country}/dashboard")
async def c_dashboard(country: str):
    """Dashboard d'un pays (KPIs + dernières alertes + dernières mesures)."""
    _check(country)
    kpis = await cc.get_kpis(country)
    alerts = await cc.get_alerts(country)
    mesures = await cc.get_mesures(country, 20)
    return {
        "country": country,
        "kpis": kpis or {},
        "latest_alerts": (alerts or [])[:6],
        "latest_mesures": mesures or [],
    }


# ========================
# ÉCRITURES PAR PAYS (proxy)
# ========================

@app.post("/countries/{country}/lots")
async def c_create_lot(country: str, body: dict = Body(...)):
    _check(country)
    res = await cc.create_lot(country, body)
    if res is None:
        raise HTTPException(status_code=502, detail="Backend pays injoignable")
    return res


@app.post("/countries/{country}/mesures")
async def c_create_mesure(country: str, body: dict = Body(...)):
    _check(country)
    res = await cc.create_mesure(country, body)
    if res is None:
        raise HTTPException(status_code=502, detail="Backend pays injoignable")
    return res


@app.delete("/countries/{country}/lots/{lot_id}")
async def c_delete_lot(country: str, lot_id: int):
    _check(country)
    res = await cc.delete_lot(country, lot_id)
    if res is None:
        raise HTTPException(status_code=502, detail="Backend pays injoignable")
    return res


@app.post("/countries/{country}/lots/check-expiration")
async def c_check_expiration(country: str):
    _check(country)
    res = await cc.check_expiration(country)
    if res is None:
        raise HTTPException(status_code=502, detail="Backend pays injoignable")
    return res


# ========================
# CONSOLIDATION GLOBALE (tous pays)
# ========================

@app.get("/dashboard")
async def global_dashboard():
    """Consolidation de tous les pays connectés."""
    totals = {
        "total_lots": 0, "total_alerts": 0, "total_mesures": 0,
        "lots_conformes": 0, "lots_expires": 0,
        "lots_expiration_proche": 0, "lots_alerte": 0,
        "total_quantite_kg": 0,
    }
    par_pays = {}
    for country in COUNTRIES:
        kpis = await cc.get_kpis(country)
        if kpis:
            par_pays[country] = kpis
            for k in totals:
                totals[k] += kpis.get(k, 0)
    return {
        "pays_connectes": len(COUNTRIES),
        **totals,
        "kpis_par_pays": par_pays,
    }


@app.get("/lots")
async def global_lots():
    out = []
    for c in COUNTRIES:
        for lot in await cc.get_lots(c):
            lot["_country"] = c
            out.append(lot)
    return out


@app.get("/lots/fifo")
async def global_fifo():
    out = []
    for c in COUNTRIES:
        for lot in await cc.get_lots_fifo(c):
            lot["_country"] = c
            out.append(lot)
    out.sort(key=lambda x: x.get("date_stockage") or "")
    return out


@app.get("/alerts")
async def global_alerts():
    out = []
    for c in COUNTRIES:
        for a in await cc.get_alerts(c):
            a["_country"] = c
            out.append(a)
    return out


@app.get("/mesures")
async def global_mesures(limit: int = 50):
    out = []
    for c in COUNTRIES:
        for m in await cc.get_mesures(c, limit):
            m["_country"] = c
            out.append(m)
    return out
