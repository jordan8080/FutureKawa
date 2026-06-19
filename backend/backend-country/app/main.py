"""Backend PAYS — FastAPI. Logique métier, PostgreSQL, MQTT, alertes, email.

Une seule image, paramétrée par COUNTRY. Routes internes (sans préfixe /api) :
le backend CENTRAL ajoute le préfixe et consolide les 3 pays.
"""
import threading
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from . import alerts, config, crud, schemas
from .database import get_db, init_db, wait_for_db, SessionLocal
from .mqtt import start_mqtt
from .seed import run_seed


def _age_watcher():
    """Vérifie périodiquement l'âge des lots (alertes expiration)."""
    while True:
        time.sleep(3600)
        db = SessionLocal()
        try:
            alerts.evaluate_lots_age(db)
        except Exception as exc:  # noqa: BLE001
            print(f"[AGE] Erreur: {exc}", flush=True)
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    init_db()
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
    start_mqtt()
    threading.Thread(target=_age_watcher, daemon=True, name="age-watcher").start()
    yield


app = FastAPI(title=f"FutureKawa — Backend {config.CONFIG['name']}", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "country": config.COUNTRY}


@app.get("/info")
def info():
    return config.CONFIG


# ─── Entrepôts ────────────────────────────────────────────────────────────────
@app.get("/warehouses", response_model=List[schemas.WarehouseOut])
def list_warehouses(db: Session = Depends(get_db)):
    return crud.get_warehouses(db)


@app.post("/warehouses", response_model=schemas.WarehouseOut, status_code=201)
def create_warehouse(payload: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    return crud.create_warehouse(db, payload)


@app.get("/warehouses/{warehouse_id}", response_model=Optional[schemas.WarehouseOut])
def get_warehouse(warehouse_id: str, db: Session = Depends(get_db)):
    return crud.get_warehouse(db, warehouse_id)


@app.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: str, db: Session = Depends(get_db)):
    result = crud.delete_warehouse(db, warehouse_id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Entrepôt introuvable")
    if result == "has_lots":
        raise HTTPException(
            status_code=400,
            detail="Entrepôt non vide : supprimez ou déplacez d'abord ses lots.")
    return {"ok": True, "id": warehouse_id}


@app.get("/warehouses/{warehouse_id}/lots", response_model=List[schemas.LotOut])
def warehouse_lots(warehouse_id: str, db: Session = Depends(get_db)):
    return crud.get_lots_by_warehouse(db, warehouse_id)


@app.get("/warehouses/{warehouse_id}/sensors", response_model=List[schemas.MeasurementOut])
def warehouse_sensors(warehouse_id: str, limit: Optional[int] = None,
                      db: Session = Depends(get_db)):
    return crud.get_measurements(db, warehouse_id, limit)


@app.get("/sensors/current", response_model=List[schemas.SensorCurrent])
def sensors_current(db: Session = Depends(get_db)):
    return crud.sensors_current(db)


@app.get("/sensors/latest", response_model=List[schemas.SensorLatest])
def sensors_latest(db: Session = Depends(get_db)):
    return crud.sensors_latest(db)


# ─── Lots ─────────────────────────────────────────────────────────────────────
@app.get("/lots", response_model=List[schemas.LotOut])
def list_lots(db: Session = Depends(get_db)):
    return crud.get_lots(db)


@app.get("/lots/{lot_id}", response_model=Optional[schemas.LotOut])
def get_lot(lot_id: str, db: Session = Depends(get_db)):
    return crud.get_lot(db, lot_id)


@app.post("/lots", response_model=schemas.LotOut, status_code=201)
def create_lot(payload: schemas.LotCreate, db: Session = Depends(get_db)):
    if not crud.get_warehouse(db, payload.warehouse_id):
        raise HTTPException(status_code=400, detail="Entrepôt inconnu")
    return crud.create_lot(db, payload)


@app.patch("/lots/{lot_id}/status", response_model=Optional[schemas.LotOut])
def update_status(lot_id: str, payload: schemas.StatusUpdate,
                  db: Session = Depends(get_db)):
    valid = {"conforme", "alerte", "perime", "expedie"}
    if payload.status not in valid:
        raise HTTPException(status_code=422, detail=f"Statut invalide: {payload.status}")
    lot = crud.update_lot_status(db, lot_id, payload.status)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot introuvable")
    return lot


@app.delete("/lots/{lot_id}")
def delete_lot(lot_id: str, db: Session = Depends(get_db)):
    if not crud.delete_lot(db, lot_id):
        raise HTTPException(status_code=404, detail="Lot introuvable")
    return {"ok": True, "id": lot_id}


# ─── Alertes ──────────────────────────────────────────────────────────────────
@app.get("/alerts", response_model=List[schemas.AlertOut])
def list_alerts(country: Optional[str] = None, type: Optional[str] = None,
                status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return crud.get_alerts(db, country=country, type=type, status=status)


@app.get("/alerts/count", response_model=schemas.AlertCount)
def alerts_count(db: Session = Depends(get_db)):
    return crud.alert_count(db)


@app.post("/alerts/{alert_id}/resolve", response_model=Optional[schemas.AlertOut])
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = crud.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    return alert


# ─── KPIs / FIFO ──────────────────────────────────────────────────────────────
@app.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    return crud.kpis(db)


@app.get("/fifo", response_model=List[schemas.LotOut])
def fifo(limit: int = 10, db: Session = Depends(get_db)):
    return crud.fifo(db, limit)
