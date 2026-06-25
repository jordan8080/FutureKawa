"""Tests unitaires du moteur d'alertes (app.alerts / app.crud.create_alert).

Pays figé sur 'brazil' (cf. conftest) :
  - température autorisée : [26, 32] °C  (idéal 29 ± 3)
  - humidité autorisée   : [53, 57] %   (idéal 55 ± 2)
  - âge maximum d'un lot  : 365 jours
"""
from app import alerts, crud, models
from conftest import make_lot, make_warehouse


# ─── Température / humidité ──────────────────────────────────────────────────
def test_mesure_hors_seuil_temperature_cree_alerte(db_session):
    wh = make_warehouse(db_session)

    alerts.evaluate_measurement(db_session, wh, temperature=40.0, humidity=55.0)

    actives = crud.get_alerts(db_session, type="temperature")
    assert len(actives) == 1
    assert actives[0].type == "temperature"
    assert actives[0].status == "active"
    assert actives[0].severity == "critical"  # dépassement de 8°C >= 3


def test_mesure_hors_seuil_humidite_cree_alerte(db_session):
    wh = make_warehouse(db_session)

    alerts.evaluate_measurement(db_session, wh, temperature=29.0, humidity=70.0)

    alertes = crud.get_alerts(db_session, type="humidity")
    assert len(alertes) == 1
    assert alertes[0].type == "humidity"


def test_mesure_dans_les_seuils_ne_cree_aucune_alerte(db_session):
    wh = make_warehouse(db_session)

    # 29°C et 55% sont pile au centre des plages autorisées.
    alerts.evaluate_measurement(db_session, wh, temperature=29.0, humidity=55.0)

    assert crud.get_alerts(db_session) == []


def test_bornes_incluses_pas_d_alerte(db_session):
    """Les bornes exactes (32°C / 57%) sont considérées dans la plage."""
    wh = make_warehouse(db_session)

    alerts.evaluate_measurement(db_session, wh, temperature=32.0, humidity=57.0)

    assert crud.get_alerts(db_session) == []


# ─── Règle d'âge des lots (> 365 jours) ──────────────────────────────────────
def test_lot_de_plus_de_365_jours_cree_alerte_age_et_perime(db_session):
    make_warehouse(db_session)
    lot = make_lot(db_session, "FK-BR-OLD-001", days_ago=400, status="conforme")

    alerts.evaluate_lots_age(db_session)

    db_session.refresh(lot)
    assert lot.status == "perime"

    age_alerts = crud.get_alerts(db_session, type="lot_age")
    assert len(age_alerts) == 1
    assert age_alerts[0].severity == "critical"
    assert age_alerts[0].lot_id == "FK-BR-OLD-001"


def test_lot_recent_ne_cree_pas_d_alerte_age(db_session):
    make_warehouse(db_session)
    make_lot(db_session, "FK-BR-NEW-001", days_ago=30, status="conforme")

    alerts.evaluate_lots_age(db_session)

    assert crud.get_alerts(db_session, type="lot_age") == []


# ─── Anti-duplication (dedup_key) ────────────────────────────────────────────
def test_anti_duplication_meme_cause(db_session):
    wh = make_warehouse(db_session)

    # Deux mesures successives hors plage → même dedup_key → une seule alerte.
    alerts.evaluate_measurement(db_session, wh, temperature=40.0, humidity=55.0)
    alerts.evaluate_measurement(db_session, wh, temperature=41.0, humidity=55.0)

    assert len(crud.get_alerts(db_session, type="temperature")) == 1


def test_create_alert_renvoie_none_si_doublon_actif(db_session):
    wh = make_warehouse(db_session)

    first = crud.create_alert(
        db_session, type="temperature", severity="high", warehouse=wh,
        lot_id=None, message="msg", dedup_key="temperature:w-br-1",
    )
    second = crud.create_alert(
        db_session, type="temperature", severity="high", warehouse=wh,
        lot_id=None, message="msg", dedup_key="temperature:w-br-1",
    )

    assert first is not None
    assert second is None
    assert db_session.query(models.Alert).count() == 1


def test_alerte_recreee_apres_resolution(db_session):
    """Une fois l'alerte résolue, une nouvelle même cause redéclenche une alerte."""
    wh = make_warehouse(db_session)

    a1 = crud.create_alert(
        db_session, type="temperature", severity="high", warehouse=wh,
        lot_id=None, message="msg", dedup_key="temperature:w-br-1",
    )
    crud.resolve_alert(db_session, a1.id)

    a2 = crud.create_alert(
        db_session, type="temperature", severity="high", warehouse=wh,
        lot_id=None, message="msg", dedup_key="temperature:w-br-1",
    )

    assert a2 is not None
    assert db_session.query(models.Alert).count() == 2
