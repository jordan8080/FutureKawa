from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .mqtt import start_mqtt
from .database import SessionLocal, engine
from .lot_checker import (
update_lot_status
)
from . import models
from . import schemas
from . import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# =========================
# DATABASE
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================
# ROOT
# =========================

@app.get("/")
def root():

    return {
        "message": "FutureKawa Brazil Backend"
    }


# =========================
# LOTS
# =========================

@app.post("/lots")
def create_lot(
    lot: schemas.LotCreate,
    db: Session = Depends(get_db)
):

    return crud.create_lot(db, lot)


@app.get("/lots")
def get_lots(
    db: Session = Depends(get_db)
):

    return crud.get_lots(db)


# =========================
# MESURES
# =========================

@app.post("/mesures")
def create_mesure(
    mesure: schemas.MesureCreate,
    db: Session = Depends(get_db)
):

    return crud.create_mesure(db, mesure)


@app.get("/mesures")
def get_mesures(
    db: Session = Depends(get_db)
):

    return crud.get_mesures(db)


# =========================
# ALERTS
# =========================

@app.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db)
):

    return crud.get_alerts(db)

@app.on_event("startup")
def startup_event():

    start_mqtt()


@app.get(
"/lots/fifo"
)
def fifo(
db:
Session
=
Depends(
get_db
)
):

    return (

        db

        .query(
            models.Lot
        )

        .order_by(
            models.Lot.date_stockage.asc()
        )

        .all()

    )

@app.post(
"/lots/check"
)
def check_lots(

db:
Session
=
Depends(
get_db
)

):

    update_lot_status(
        db
    )

    return {

        "message":
        "lots updated"

    }