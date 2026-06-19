"""Règles d'alerte automatiques + réconciliation des statuts de lots.

Types d'alerte (alignés sur le front) : temperature | humidity | lot_age.
Anti-duplication via dedup_key (une alerte active par cause).
"""
from sqlalchemy.orm import Session

from . import config, crud, models


def _severity_from_excess(excess: float) -> str:
    if excess >= 3:
        return "critical"
    if excess >= 1.5:
        return "high"
    if excess >= 0.5:
        return "medium"
    return "low"


def evaluate_measurement(db: Session, warehouse: models.Warehouse,
                         temperature: float, humidity: float):
    """Évalue une mesure : alertes température/humidité + statut des lots."""
    tmin, tmax = config.temp_range()
    hmin, hmax = config.humidity_range()

    temp_ok = tmin <= temperature <= tmax
    hum_ok = hmin <= humidity <= hmax

    if not temp_ok:
        if temperature > tmax:
            msg = f"Température hors plage : {temperature}°C (max autorisé : {tmax}°C)"
            excess = temperature - tmax
        else:
            msg = f"Température hors plage : {temperature}°C (min autorisé : {tmin}°C)"
            excess = tmin - temperature
        crud.create_alert(
            db, type="temperature", severity=_severity_from_excess(excess),
            warehouse=warehouse, lot_id=None, message=msg,
            dedup_key=f"temperature:{warehouse.id}",
        )

    if not hum_ok:
        if humidity > hmax:
            msg = f"Humidité hors plage : {humidity}% (max autorisé : {hmax}%)"
            excess = humidity - hmax
        else:
            msg = f"Humidité hors plage : {humidity}% (min autorisé : {hmin}%)"
            excess = hmin - humidity
        crud.create_alert(
            db, type="humidity", severity=_severity_from_excess(excess),
            warehouse=warehouse, lot_id=None, message=msg,
            dedup_key=f"humidity:{warehouse.id}",
        )

    reconcile_warehouse_lots(db, warehouse, in_range=(temp_ok and hum_ok))


def reconcile_warehouse_lots(db: Session, warehouse: models.Warehouse, in_range: bool):
    """Aligne le statut des lots d'un entrepôt sur les conditions courantes.

    - âge > limite => perime (terminal)
    - sinon, hors plage => alerte, dans la plage => conforme
    - perime / expedie ne sont jamais rétrogradés
    """
    changed = False
    for lot in crud.get_lots_by_warehouse(db, warehouse.id):
        if crud.lot_age_days(lot) > config.LOT_MAX_AGE_DAYS:
            if lot.status != "perime":
                lot.status = "perime"
                changed = True
            continue
        if lot.status in ("perime", "expedie"):
            continue
        new_status = "conforme" if in_range else "alerte"
        if lot.status != new_status:
            lot.status = new_status
            changed = True
    if changed:
        db.commit()


def evaluate_lots_age(db: Session):
    """Parcourt tous les lots : alertes d'âge (expiré / proche expiration)."""
    warehouses = {w.id: w for w in crud.get_warehouses(db)}
    for lot in crud.get_lots(db):
        if lot.status == "expedie":
            continue
        days = crud.lot_age_days(lot)
        wh = warehouses.get(lot.warehouse_id)
        if wh is None:
            continue

        if days > config.LOT_MAX_AGE_DAYS:
            if lot.status != "perime":
                lot.status = "perime"
                db.commit()
            crud.create_alert(
                db, type="lot_age", severity="critical", warehouse=wh, lot_id=lot.id,
                message=(f"Lot {lot.id} stocké depuis {days} jours "
                         f"(limite : {config.LOT_MAX_AGE_DAYS} jours)"),
                dedup_key=f"lot_age:{lot.id}",
            )
        elif days >= config.LOT_NEAR_EXPIRY_DAYS:
            crud.create_alert(
                db, type="lot_age", severity="high", warehouse=wh, lot_id=lot.id,
                message=(f"Lot {lot.id} proche de la limite de stockage : {days} jours "
                         f"(limite : {config.LOT_MAX_AGE_DAYS} jours)"),
                dedup_key=f"lot_age_near:{lot.id}",
            )
