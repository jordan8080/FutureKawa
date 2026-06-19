"""Seed de démo idempotent (ne s'exécute que si la base du pays est vide).

Insère entrepôts + lots + historique de mesures (7 j), puis laisse le moteur
d'alertes calculer les statuts de lots et générer les alertes initiales.
"""
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from . import alerts, config, crud, models

# (id, name, location, exploitation, base_temp, base_humidity)
WAREHOUSES = {
    "brazil": [
        ("w-br-1", "Entrepôt São Paulo", "São Paulo", "Fazenda Aurora", 28.3, 54.2),
        ("w-br-2", "Entrepôt Minas Gerais", "Minas Gerais", "Fazenda Verde", 32.7, 56.1),
    ],
    "ecuador": [
        ("w-ec-1", "Entrepôt Quitoo", "Quito", "Hacienda del Sol", 30.8, 60.5),
        ("w-ec-2", "Entrepôt Guayaquil", "Guayaquil", "Finca La Esperanza", 27.9, 59.4),
    ],
    "colombia": [
        ("w-co-1", "Entrepôt Bogotá", "Bogotá", "Finca Cafetera Nacional", 26.2, 79.8),
        ("w-co-2", "Entrepôt Medellín", "Medellín", "Hacienda El Paraíso", 25.7, 82.6),
    ],
}

# (id, warehouse_id, exploitation, days_ago, weight, variety, grade)
LOTS = {
    "brazil": [
        ("FK-BR-SP-001", "w-br-1", "Fazenda Aurora", 387, 2500, "Arabica", "Grade 2"),
        ("FK-BR-SP-002", "w-br-1", "Fazenda Aurora", 210, 1800, "Arabica", "Grade 1"),
        ("FK-BR-SP-003", "w-br-1", "Fazenda Aurora", 145, 3200, "Robusta", "Grade 1"),
        ("FK-BR-SP-004", "w-br-1", "Fazenda Aurora", 67, 1500, "Arabica", "Grade 1"),
        ("FK-BR-SP-005", "w-br-1", "Fazenda Aurora", 12, 2100, "Arabica", "Grade 2"),
        ("FK-BR-MG-001", "w-br-2", "Fazenda Verde", 320, 2800, "Arabica", "Grade 1"),
        ("FK-BR-MG-002", "w-br-2", "Fazenda Verde", 198, 1600, "Robusta", "Grade 2"),
        ("FK-BR-MG-003", "w-br-2", "Fazenda Verde", 89, 2200, "Arabica", "Grade 1"),
        ("FK-BR-MG-004", "w-br-2", "Fazenda Verde", 34, 900, "Robusta", "Grade 2"),
    ],
    "ecuador": [
        ("FK-EC-QT-001", "w-ec-1", "Hacienda del Sol", 290, 3500, "Arabica", "Specialty"),
        ("FK-EC-QT-002", "w-ec-1", "Hacienda del Sol", 178, 2100, "Arabica", "Grade 1"),
        ("FK-EC-QT-003", "w-ec-1", "Hacienda del Sol", 95, 1800, "Arabica", "Specialty"),
        ("FK-EC-QT-004", "w-ec-1", "Hacienda del Sol", 41, 2700, "Arabica", "Grade 1"),
        ("FK-EC-QT-005", "w-ec-1", "Hacienda del Sol", 8, 1200, "Robusta", "Grade 2"),
        ("FK-EC-GU-001", "w-ec-2", "Finca La Esperanza", 412, 1400, "Robusta", "Grade 2"),
        ("FK-EC-GU-002", "w-ec-2", "Finca La Esperanza", 254, 2000, "Arabica", "Grade 1"),
        ("FK-EC-GU-003", "w-ec-2", "Finca La Esperanza", 120, 3100, "Arabica", "Grade 1"),
        ("FK-EC-GU-004", "w-ec-2", "Finca La Esperanza", 55, 1700, "Robusta", "Grade 2"),
    ],
    "colombia": [
        ("FK-CO-BG-001", "w-co-1", "Finca Cafetera Nacional", 340, 4200, "Arabica", "Specialty"),
        ("FK-CO-BG-002", "w-co-1", "Finca Cafetera Nacional", 215, 2800, "Arabica", "Specialty"),
        ("FK-CO-BG-003", "w-co-1", "Finca Cafetera Nacional", 130, 1900, "Arabica", "Grade 1"),
        ("FK-CO-BG-004", "w-co-1", "Finca Cafetera Nacional", 72, 3300, "Arabica", "Specialty"),
        ("FK-CO-BG-005", "w-co-1", "Finca Cafetera Nacional", 19, 2100, "Robusta", "Grade 1"),
        ("FK-CO-MD-001", "w-co-2", "Hacienda El Paraíso", 298, 2600, "Arabica", "Grade 1"),
        ("FK-CO-MD-002", "w-co-2", "Hacienda El Paraíso", 167, 1500, "Arabica", "Specialty"),
        ("FK-CO-MD-003", "w-co-2", "Hacienda El Paraíso", 88, 2900, "Robusta", "Grade 2"),
        ("FK-CO-MD-004", "w-co-2", "Hacienda El Paraíso", 23, 1800, "Arabica", "Grade 1"),
    ],
}


def _generate_readings(wh_id, base_temp, base_hum, days=7, interval_hours=3):
    rng = random.Random(sum(ord(c) for c in wh_id))
    now = datetime.now(timezone.utc)
    points = (days * 24) // interval_hours
    out = []
    for i in range(points, -1, -1):
        ts = now - timedelta(hours=i * interval_hours)
        spike = (rng.random() - 0.5) * 9 if rng.random() < 0.08 else 0
        temp = round(base_temp + (rng.random() - 0.5) * 5 + spike, 1)
        hum = round(max(0, min(100, base_hum + (rng.random() - 0.5) * 4 + spike * 0.4)), 1)
        out.append((ts, temp, hum))
    return out


def run_seed(db: Session):
    if db.query(models.Warehouse).count() > 0:
        print(f"[SEED] Base {config.COUNTRY} déjà peuplée — seed ignoré.", flush=True)
        return

    print(f"[SEED] Peuplement de la base {config.COUNTRY}…", flush=True)
    now = datetime.now(timezone.utc)

    # Entrepôts
    for wid, name, loc, expl, t, h in WAREHOUSES[config.COUNTRY]:
        db.add(models.Warehouse(
            id=wid, name=name, country=config.COUNTRY, location=loc,
            exploitation=expl, current_temp=t, current_humidity=h,
        ))
    db.commit()  # entrepôts d'abord (contrainte FK des lots)

    # Lots (statut initial conforme — corrigé ensuite par le moteur d'alertes)
    for lid, wid, expl, days_ago, weight, variety, grade in LOTS[config.COUNTRY]:
        db.add(models.Lot(
            id=lid, warehouse_id=wid, country=config.COUNTRY, exploitation=expl,
            stored_at=now - timedelta(days=days_ago), status="conforme",
            weight=weight, variety=variety, grade=grade,
        ))
    db.commit()

    # Historique de mesures (7 derniers jours)
    for wid, name, loc, expl, base_t, base_h in WAREHOUSES[config.COUNTRY]:
        for ts, temp, hum in _generate_readings(wid, base_t, base_h):
            db.add(models.Measurement(
                warehouse_id=wid, temperature=temp, humidity=hum, timestamp=ts))
    db.commit()

    # Calcul des statuts de lots + alertes initiales à partir de l'état courant
    for wh in crud.get_warehouses(db):
        alerts.evaluate_measurement(db, wh, wh.current_temp, wh.current_humidity)
    alerts.evaluate_lots_age(db)

    print(f"[SEED] {config.COUNTRY} : "
          f"{db.query(models.Warehouse).count()} entrepôts, "
          f"{db.query(models.Lot).count()} lots, "
          f"{db.query(models.Alert).count()} alertes.", flush=True)
