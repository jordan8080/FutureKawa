"""Accès aux données + règles de tri (FIFO) et helpers métier."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import config, models
from .email_service import send_alert_email


def _now():
    return datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    """Garantit un datetime tz-aware (Postgres peut renvoyer naive selon le driver)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def lot_age_days(lot: models.Lot) -> int:
    return (_now() - _aware(lot.stored_at)).days


# ─── Entrepôts ────────────────────────────────────────────────────────────────
def get_warehouses(db: Session):
    return db.query(models.Warehouse).order_by(models.Warehouse.id).all()


def get_warehouse(db: Session, warehouse_id: str):
    return db.get(models.Warehouse, warehouse_id)


# ─── Lots (tri FIFO : les plus anciens d'abord) ───────────────────────────────
def get_lots(db: Session):
    return db.query(models.Lot).order_by(models.Lot.stored_at.asc()).all()


def get_lots_by_warehouse(db: Session, warehouse_id: str):
    return (db.query(models.Lot)
            .filter(models.Lot.warehouse_id == warehouse_id)
            .order_by(models.Lot.stored_at.asc())
            .all())


def get_lot(db: Session, lot_id: str):
    return db.get(models.Lot, lot_id)


def create_lot(db: Session, data) -> models.Lot:
    new_id = f"FK-{config.CONFIG['code']}-{uuid.uuid4().hex[:6].upper()}"
    lot = models.Lot(
        id=new_id,
        warehouse_id=data.warehouse_id,
        country=config.COUNTRY,
        exploitation=data.exploitation,
        stored_at=_now(),
        status="conforme",
        weight=data.weight,
        variety=data.variety,
        grade=data.grade,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


def update_lot_status(db: Session, lot_id: str, status: str):
    lot = get_lot(db, lot_id)
    if not lot:
        return None
    lot.status = status
    db.commit()
    db.refresh(lot)
    return lot


def delete_lot(db: Session, lot_id: str) -> bool:
    lot = get_lot(db, lot_id)
    if not lot:
        return False
    # nettoie les alertes liées à ce lot
    db.query(models.Alert).filter(models.Alert.lot_id == lot_id).delete()
    db.delete(lot)
    db.commit()
    return True


def create_warehouse(db: Session, data) -> models.Warehouse:
    new_id = f"w-{config.CONFIG['code'].lower()}-{uuid.uuid4().hex[:6]}"
    wh = models.Warehouse(
        id=new_id,
        name=data.name,
        country=config.COUNTRY,
        location=data.location,
        exploitation=data.exploitation,
        current_temp=config.CONFIG["ideal_temp"],
        current_humidity=config.CONFIG["ideal_humidity"],
    )
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh


def delete_warehouse(db: Session, warehouse_id: str) -> str:
    """Renvoie 'ok' | 'not_found' | 'has_lots'."""
    wh = get_warehouse(db, warehouse_id)
    if not wh:
        return "not_found"
    if get_lots_by_warehouse(db, warehouse_id):
        return "has_lots"
    db.query(models.Measurement).filter(
        models.Measurement.warehouse_id == warehouse_id).delete()
    db.query(models.Alert).filter(
        models.Alert.warehouse_id == warehouse_id).delete()
    db.delete(wh)
    db.commit()
    return "ok"


# ─── Mesures capteurs ─────────────────────────────────────────────────────────
def add_measurement(db: Session, warehouse_id: str, temperature: float, humidity: float):
    m = models.Measurement(
        warehouse_id=warehouse_id,
        temperature=temperature,
        humidity=humidity,
        timestamp=_now(),
    )
    db.add(m)
    # met à jour l'état courant de l'entrepôt (consommé par le front)
    wh = get_warehouse(db, warehouse_id)
    if wh:
        wh.current_temp = temperature
        wh.current_humidity = humidity
    db.commit()
    db.refresh(m)
    return m


def get_measurements(db: Session, warehouse_id: str, limit: int | None = None):
    q = (db.query(models.Measurement)
         .filter(models.Measurement.warehouse_id == warehouse_id)
         .order_by(models.Measurement.timestamp.asc()))
    rows = q.all()
    if limit:
        rows = rows[-limit:]
    return rows


def get_latest_measurement(db: Session, warehouse_id: str):
    return (db.query(models.Measurement)
            .filter(models.Measurement.warehouse_id == warehouse_id)
            .order_by(models.Measurement.timestamp.desc())
            .first())


def sensors_latest(db: Session):
    out = []
    for wh in get_warehouses(db):
        m = get_latest_measurement(db, wh.id)
        out.append({
            "warehouse_id": wh.id,
            "warehouse_name": wh.name,
            "timestamp": m.timestamp if m else None,
            "temperature": m.temperature if m else wh.current_temp,
            "humidity": m.humidity if m else wh.current_humidity,
        })
    return out


def sensors_current(db: Session):
    out = []
    for wh in get_warehouses(db):
        m = get_latest_measurement(db, wh.id)
        out.append({
            "warehouse_id": wh.id,
            "warehouse_name": wh.name,
            "country": wh.country,
            "temperature": wh.current_temp,
            "humidity": wh.current_humidity,
            "last_updated": m.timestamp if m else _now(),
        })
    return out


# ─── Alertes ──────────────────────────────────────────────────────────────────
def get_alerts(db: Session, country=None, type=None, status=None):
    q = db.query(models.Alert)
    if type:
        q = q.filter(models.Alert.type == type)
    if status:
        q = q.filter(models.Alert.status == status)
    # country est implicite (une base par pays) mais on respecte le filtre
    if country:
        q = q.filter(models.Alert.country == country)
    return q.order_by(models.Alert.created_at.desc()).all()


def resolve_alert(db: Session, alert_id: str):
    alert = db.get(models.Alert, alert_id)
    if not alert:
        return None
    alert.status = "resolved"
    db.commit()
    db.refresh(alert)
    return alert


def alert_count(db: Session):
    active = db.query(func.count(models.Alert.id)).filter(models.Alert.status == "active").scalar()
    total = db.query(func.count(models.Alert.id)).scalar()
    return {"active": int(active or 0), "total": int(total or 0)}


def create_alert(db: Session, *, type, severity, warehouse, lot_id, message, dedup_key):
    """Crée une alerte si aucune alerte ACTIVE de même dedup_key n'existe (anti-duplication)."""
    existing = (db.query(models.Alert)
                .filter(models.Alert.dedup_key == dedup_key,
                        models.Alert.status == "active")
                .first())
    if existing:
        return None

    alert = models.Alert(
        id=f"{config.CONFIG['code']}-AL-{uuid.uuid4().hex[:8]}",
        type=type,
        severity=severity,
        country=config.COUNTRY,
        warehouse_id=warehouse.id,
        warehouse_name=warehouse.name,
        lot_id=lot_id,
        message=message,
        created_at=_now(),
        status="active",
        dedup_key=dedup_key,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    send_alert_email(
        subject=f"[FutureKawa {config.CONFIG['name']}] Alerte {type} ({severity})",
        body=f"{message}\nEntrepôt : {warehouse.name}\nResponsable : {config.CONFIG['manager']}",
    )
    return alert


# ─── KPIs / FIFO ──────────────────────────────────────────────────────────────
def kpis(db: Session):
    lots = get_lots(db)
    total = len(lots)
    conforme = sum(1 for l in lots if l.status == "conforme")
    perime = sum(1 for l in lots if l.status == "perime")
    alerte = sum(1 for l in lots if l.status == "alerte")
    active_alerts = db.query(func.count(models.Alert.id)).filter(
        models.Alert.status == "active").scalar()
    return {
        "country": config.COUNTRY,
        "totalLots": total,
        "conformeLots": conforme,
        "perimeLots": perime,
        "alerteLots": alerte,
        "conformePct": round(conforme / total * 100) if total else 100,
        "activeAlerts": int(active_alerts or 0),
        "warehouses": len(get_warehouses(db)),
    }


def fifo(db: Session, limit: int = 10):
    """Lots à expédier en priorité (les plus anciens), hors expédiés."""
    lots = [l for l in get_lots(db) if l.status != "expedie"]
    return lots[:limit]
