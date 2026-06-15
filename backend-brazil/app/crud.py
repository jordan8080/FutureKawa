from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, timedelta

from . import models, schemas


# ========================
# PAYS
# ========================

def get_pays_brazil(db: Session):
    return db.query(models.Pays).filter(models.Pays.nom == "Brazil").first()


def get_all_pays(db: Session):
    return db.query(models.Pays).all()


def get_pays_by_entrepot(db: Session, entrepot_id: int):
    """Remonte la chaîne entrepot -> exploitation -> pays pour récupérer les seuils."""
    entrepot = db.query(models.Entrepot).filter(
        models.Entrepot.Id_entrepot == entrepot_id
    ).first()
    if not entrepot or entrepot.exploitation is None:
        return get_pays_brazil(db)  # fallback
    return entrepot.exploitation.pays


def get_lots_by_entrepot(db: Session, entrepot_id: int):
    """Lots présents dans un entrepôt, triés FIFO (plus ancien d'abord)."""
    return db.query(models.Lot).filter(
        models.Lot.Id_entrepot == entrepot_id
    ).order_by(models.Lot.date_stockage.asc()).all()


# ========================
# ENTREPOTS
# ========================

def get_entrepots(db: Session):
    return db.query(models.Entrepot).all()


def create_entrepot(db: Session, entrepot: schemas.EntrepotCreate):
    db_entrepot = models.Entrepot(
        nom=entrepot.nom,
        localisation=entrepot.localisation,
        capacite_stockage=entrepot.capacite_stockage,
        Id_exploitation=entrepot.Id_exploitation
    )
    db.add(db_entrepot)
    db.commit()
    db.refresh(db_entrepot)
    return db_entrepot


# ========================
# LOTS
# ========================

def create_lot(db: Session, lot: schemas.LotCreate):
    db_lot = models.Lot(
        date_stockage=lot.date_stockage,
        statut=lot.statut,
        quantite=lot.quantite,
        date_expiration=lot.date_expiration,
        Id_entrepot=lot.Id_entrepot
    )
    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    return db_lot


def get_lots(db: Session):
    return db.query(models.Lot).all()


def get_lot_by_id(db: Session, lot_id: int):
    return db.query(models.Lot).filter(models.Lot.Id_lot == lot_id).first()


def update_lot(db: Session, lot_id: int, data: dict):
    lot = get_lot_by_id(db, lot_id)
    if not lot:
        return None
    for key, value in data.items():
        setattr(lot, key, value)
    db.commit()
    db.refresh(lot)
    return lot


def delete_lot(db: Session, lot_id: int):
    lot = get_lot_by_id(db, lot_id)
    if lot:
        db.delete(lot)
        db.commit()
    return lot


def get_lots_fifo(db: Session):
    """Retourne les lots triés FIFO (les plus anciens en premier)"""
    return db.query(models.Lot).order_by(models.Lot.date_stockage.asc()).all()


def update_lots_statut(db: Session):
    """Met à jour automatiquement le statut de tous les lots"""
    lots = db.query(models.Lot).all()
    today = date.today()

    for lot in lots:
        if lot.date_expiration is None:
            continue
        if lot.date_expiration <= today:
            lot.statut = "expire"
        elif lot.date_expiration <= today + timedelta(days=30):
            lot.statut = "expiration_proche"
        else:
            # Ne pas écraser une alerte de température/humidité
            if lot.statut not in ("alerte",):
                lot.statut = "conforme"

    db.commit()
    return lots


# ========================
# MESURES
# ========================

def create_mesure(db: Session, mesure: schemas.MesureCreate):
    db_mesure = models.Mesure(
        temperature=mesure.temperature,
        humidite=mesure.humidite,
        Id_entrepot=mesure.Id_entrepot
    )
    db.add(db_mesure)
    db.commit()
    db.refresh(db_mesure)
    return db_mesure


def get_mesures(db: Session, limit: int = 50):
    return db.query(models.Mesure).order_by(desc(models.Mesure.date_mesure)).limit(limit).all()


def get_latest_mesure(db: Session):
    return db.query(models.Mesure).order_by(desc(models.Mesure.date_mesure)).first()


# ========================
# ALERTS
# ========================

def alert_exists(db: Session, message: str, lot_id: int):
    """Vérifie si une alerte identique existe déjà (anti-duplication)"""
    return db.query(models.Alert).filter(
        models.Alert.message == message,
        models.Alert.Id_lot == lot_id
    ).first()


def create_alert_if_new(db: Session, message: str, type_alerte: str, niveau: str, lot_id: int):
    """Crée une alerte seulement si elle n'existe pas déjà"""
    if alert_exists(db, message, lot_id):
        return None

    alert = models.Alert(
        message=message,
        type_alerte=type_alerte,
        niveau=niveau,
        Id_lot=lot_id
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    print(f"[ALERT] Nouvelle alerte créée : {message}")
    return alert


def get_alerts(db: Session):
    return db.query(models.Alert).order_by(desc(models.Alert.created_at)).all()


def get_alerts_critical(db: Session):
    return db.query(models.Alert).filter(
        models.Alert.niveau == "critical"
    ).order_by(desc(models.Alert.created_at)).all()
