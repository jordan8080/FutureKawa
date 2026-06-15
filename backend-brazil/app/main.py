from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from .database import SessionLocal, engine
from . import models, schemas, crud
from .mqtt import start_mqtt
from .alerts import check_lot_age_and_expiration, check_and_create_alerts_from_mesure
from .seed import seed_if_empty

app = FastAPI(title="FutureKawa Brazil API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================
# DB DEPENDENCY
# ========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================
# STARTUP
# ========================

@app.on_event("startup")
def startup_event():
    seed_if_empty()
    start_mqtt()


# ========================
# ROOT
# ========================

@app.get("/")
def root():
    return {"message": "FutureKawa Brazil Backend", "status": "running"}


# ========================
# PAYS
# ========================

@app.get("/pays")
def get_pays(db: Session = Depends(get_db)):
    return crud.get_all_pays(db)


# ========================
# ENTREPOTS
# ========================

@app.get("/entrepots")
def get_entrepots(db: Session = Depends(get_db)):
    return crud.get_entrepots(db)


@app.post("/entrepots")
def create_entrepot(
    entrepot: schemas.EntrepotCreate,
    db: Session = Depends(get_db)
):
    return crud.create_entrepot(db, entrepot)


# ========================
# LOTS
# ========================

@app.get("/lots")
def get_lots(db: Session = Depends(get_db)):
    return crud.get_lots(db)


@app.get("/lots/fifo")
def get_lots_fifo(db: Session = Depends(get_db)):
    """Retourne les lots triés FIFO (plus anciens en premier — à expédier en priorité)"""
    return crud.get_lots_fifo(db)


@app.post("/lots")
def create_lot(
    lot: schemas.LotCreate,
    db: Session = Depends(get_db)
):
    return crud.create_lot(db, lot)


@app.get("/lots/{lot_id}")
def get_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = crud.get_lot_by_id(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return lot


@app.put("/lots/{lot_id}")
def update_lot(
    lot_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    lot = crud.update_lot(db, lot_id, data)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return lot


@app.delete("/lots/{lot_id}")
def delete_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = crud.delete_lot(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return {"message": f"Lot {lot_id} supprimé"}


@app.post("/lots/check-expiration")
def check_lots_expiration(db: Session = Depends(get_db)):
    """
    Vérifie tous les lots : âge > 365 jours (règle officielle),
    expiration et pré-expiration. Crée les alertes + envoie les emails.
    """
    check_lot_age_and_expiration(db)
    return {"message": "Vérification âge/expiration terminée"}


# ========================
# MESURES
# ========================

@app.get("/mesures")
def get_mesures(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_mesures(db, limit=limit)


@app.get("/mesures/latest")
def get_latest_mesure(db: Session = Depends(get_db)):
    mesure = crud.get_latest_mesure(db)
    if not mesure:
        return {"message": "Aucune mesure disponible"}
    return mesure


@app.post("/mesures")
def create_mesure(
    mesure: schemas.MesureCreate,
    db: Session = Depends(get_db)
):
    """Crée une mesure et vérifie automatiquement les alertes (par entrepôt)"""
    db_mesure = crud.create_mesure(db, mesure)

    # Vérification automatique alertes sur l'entrepôt mesuré
    check_and_create_alerts_from_mesure(
        db=db,
        temperature=mesure.temperature,
        humidite=mesure.humidite,
        entrepot_id=mesure.Id_entrepot
    )

    return db_mesure


# ========================
# ALERTS
# ========================

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    return crud.get_alerts(db)


@app.get("/alerts/critical")
def get_critical_alerts(db: Session = Depends(get_db)):
    return crud.get_alerts_critical(db)


# ========================
# KPIs
# ========================

@app.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """KPIs globaux du backend Brésil"""
    lots = crud.get_lots(db)
    alerts = crud.get_alerts(db)
    mesures = crud.get_mesures(db, limit=100)
    latest = crud.get_latest_mesure(db)

    stats = {
        "conforme": 0,
        "alerte": 0,
        "expiration_proche": 0,
        "expire": 0
    }
    total_quantite = 0

    for lot in lots:
        statut = lot.statut or "conforme"
        if statut in stats:
            stats[statut] += 1
        total_quantite += lot.quantite or 0

    avg_temp = None
    avg_hum = None
    if mesures:
        temps = [float(m.temperature) for m in mesures if m.temperature is not None]
        hums = [float(m.humidite) for m in mesures if m.humidite is not None]
        avg_temp = round(sum(temps) / len(temps), 1) if temps else None
        avg_hum = round(sum(hums) / len(hums), 1) if hums else None

    return {
        "total_lots": len(lots),
        "total_alerts": len(alerts),
        "total_mesures": len(mesures),
        "lots_conformes": stats["conforme"],
        "lots_alerte": stats["alerte"],
        "lots_expiration_proche": stats["expiration_proche"],
        "lots_expires": stats["expire"],
        "total_quantite_kg": total_quantite,
        "derniere_temperature": float(latest.temperature) if latest and latest.temperature else None,
        "derniere_humidite": float(latest.humidite) if latest and latest.humidite else None,
        "temperature_moyenne": avg_temp,
        "humidite_moyenne": avg_hum
    }
