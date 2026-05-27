from sqlalchemy.orm import Session

from . import models, schemas
from datetime import date

# =========================
# LOTS
# =========================

def create_lot(db: Session, lot: schemas.LotCreate):

    db_lot = models.Lot(
        date_stockage=lot.date_stockage,
        statut=lot.statut,
        quantite=lot.quantite,
        date_expiration=lot.date_expiration,
        id_entrepot=lot.id_entrepot
    )

    db.add(db_lot)

    db.commit()

    db.refresh(db_lot)

    return db_lot


def get_lots(db: Session):

    return db.query(models.Lot).all()


# =========================
# MESURES
# =========================

def create_mesure(
    db: Session,
    mesure: schemas.MesureCreate
):

    db_mesure = models.Mesure(
        temperature=mesure.temperature,
        humidite=mesure.humidite,
        id_entrepot=mesure.id_entrepot
    )

    db.add(db_mesure)

    db.commit()

    db.refresh(db_mesure)

    return db_mesure


def get_mesures(db: Session):

    return db.query(models.Mesure).all()


# =========================
# ALERTS
# =========================

def get_alerts(
    db
):

    return (
        db
        .query(
            models.Alert
        )
        .order_by(
            models.Alert.created_at.desc()
        )
        .all()
    )

def create_alert(
    db,
    message,
    type_alerte,
    niveau,
    lot_id
):

    exists = (
        db.query(
            models.Alert
        )
        .filter(
            models.Alert.message
            ==
            message
        )
        .first()
    )

    if exists:

        return

    alert = models.Alert(

        message=message,

        type_alerte=type_alerte,

        niveau=niveau,

        id_lot=lot_id
    )

    db.add(alert)

    db.commit()