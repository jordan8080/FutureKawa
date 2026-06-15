from datetime import date, timedelta
from sqlalchemy.orm import Session

from . import models, crud
from .crud import create_alert_if_new
from .email_service import send_alert_email


def _emit_alert(db, message, type_alerte, niveau, lot_id, pays_nom):
    """
    Crée l'alerte si elle est nouvelle ET envoie un email au responsable.
    L'email n'est envoyé que si l'alerte vient d'être créée (anti-spam).
    """
    alert = create_alert_if_new(
        db=db,
        message=message,
        type_alerte=type_alerte,
        niveau=niveau,
        lot_id=lot_id
    )
    if alert:  # nouvelle alerte uniquement
        send_alert_email(
            message=message,
            type_alerte=type_alerte,
            niveau=niveau,
            pays=pays_nom or "Brazil",
            lot_id=lot_id
        )
    return alert


def check_temperature(temperature: float, pays) -> bool:
    if pays is None:
        return temperature < 26 or temperature > 32
    return temperature < float(pays.temp_min) or temperature > float(pays.temp_max)


def check_humidity(humidite: float, pays) -> bool:
    if pays is None:
        return humidite < 53 or humidite > 57
    return humidite < float(pays.humidity_min) or humidite > float(pays.humidity_max)


def check_and_create_alerts_from_mesure(
    db: Session,
    temperature: float,
    humidite: float,
    entrepot_id: int
):
    """
    Vérifie température et humidité d'une mesure et crée des alertes
    pour les lots présents dans l'entrepôt concerné (Cas 1 du sujet).
    Les seuils proviennent du pays de l'entrepôt.
    """
    pays = crud.get_pays_by_entrepot(db, entrepot_id)
    pays_nom = pays.nom if pays else "Brazil"

    # Lots concernés par cet entrepôt
    lots = crud.get_lots_by_entrepot(db, entrepot_id)
    # On rattache l'alerte au lot le plus ancien (le plus à risque / priorité FIFO)
    # Si aucun lot, on ne peut pas créer d'alerte (Id_lot NOT NULL) -> on log seulement.
    target_lot = lots[0] if lots else None

    # --- Température ---
    if check_temperature(temperature, pays):
        temp_min = float(pays.temp_min) if pays else 26
        temp_max = float(pays.temp_max) if pays else 32
        niveau = "critical" if (temperature < temp_min - 3 or temperature > temp_max + 3) else "warning"
        msg = f"Température anormale entrepôt #{entrepot_id} : {temperature}°C (seuil {pays_nom} : {temp_min}-{temp_max}°C)"
        if target_lot:
            _emit_alert(db, msg, "temperature", niveau, target_lot.Id_lot, pays_nom)
            # le statut du lot passe en alerte
            if target_lot.statut not in ("expire", "expiration_proche"):
                target_lot.statut = "alerte"
                db.commit()
        else:
            print(f"[ALERT] {msg} (aucun lot dans l'entrepôt — alerte non persistée)")

    # --- Humidité ---
    if check_humidity(humidite, pays):
        hum_min = float(pays.humidity_min) if pays else 53
        hum_max = float(pays.humidity_max) if pays else 57
        niveau = "critical" if (humidite < hum_min - 5 or humidite > hum_max + 5) else "warning"
        msg = f"Humidité anormale entrepôt #{entrepot_id} : {humidite}% (seuil {pays_nom} : {hum_min}-{hum_max}%)"
        if target_lot:
            _emit_alert(db, msg, "humidite", niveau, target_lot.Id_lot, pays_nom)
            if target_lot.statut not in ("expire", "expiration_proche"):
                target_lot.statut = "alerte"
                db.commit()
        else:
            print(f"[ALERT] {msg} (aucun lot dans l'entrepôt — alerte non persistée)")


def check_lot_age_and_expiration(db: Session):
    """
    Vérifie l'âge et l'expiration de tous les lots (Cas 2 du sujet).
    Règle officielle du cahier des charges :
      - Lot trop ancien : > 365 jours depuis la date de stockage
    Règles complémentaires (gestion fine de l'expiration) :
      - Lot expiré : date_expiration dépassée
      - Pré-expiration : expiration dans <= 30 jours
    Met aussi à jour le statut des lots.
    """
    lots = db.query(models.Lot).all()
    today = date.today()

    for lot in lots:
        pays = crud.get_pays_by_entrepot(db, lot.Id_entrepot)
        pays_nom = pays.nom if pays else "Brazil"

        # --- Règle officielle : > 365 jours de stockage ---
        if lot.date_stockage is not None:
            age_jours = (today - lot.date_stockage).days
            if age_jours > 365:
                _emit_alert(
                    db,
                    message=f"Lot #{lot.Id_lot} stocké depuis {age_jours} jours (> 365 j) — à expédier en priorité (FIFO)",
                    type_alerte="lot_ancien",
                    niveau="warning",
                    lot_id=lot.Id_lot,
                    pays_nom=pays_nom
                )

        # --- Gestion de l'expiration (statut + alertes) ---
        if lot.date_expiration is not None:
            if lot.date_expiration <= today:
                lot.statut = "expire"
                _emit_alert(
                    db,
                    message=f"Lot #{lot.Id_lot} expiré depuis le {lot.date_expiration}",
                    type_alerte="expiration",
                    niveau="critical",
                    lot_id=lot.Id_lot,
                    pays_nom=pays_nom
                )
            elif lot.date_expiration <= today + timedelta(days=30):
                lot.statut = "expiration_proche"
                jours = (lot.date_expiration - today).days
                _emit_alert(
                    db,
                    message=f"Lot #{lot.Id_lot} expire dans {jours} jours ({lot.date_expiration})",
                    type_alerte="expiration_proche",
                    niveau="warning",
                    lot_id=lot.Id_lot,
                    pays_nom=pays_nom
                )
            else:
                # ne pas écraser un statut "alerte" posé par les conditions
                if lot.statut not in ("alerte",):
                    lot.statut = "conforme"

    db.commit()
