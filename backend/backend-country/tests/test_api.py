"""Tests d'API / intégration (routes HTTP du backend pays) via TestClient.

Le client partage la même base SQLite que la fixture db_session (get_db surchargé
dans conftest), ce qui permet de préparer l'état puis de vérifier via l'API.
Les réponses sont sérialisées en camelCase (cf. schemas.CamelModel).
"""
from app import crud, models
from conftest import make_lot, make_warehouse


# ─── Santé ───────────────────────────────────────────────────────────────────
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["country"] == "brazil"


# ─── Lots : liste / création / suppression ──────────────────────────────────
def test_lister_lots_vide(client):
    resp = client.get("/lots")
    assert resp.status_code == 200
    assert resp.json() == []


def test_lister_lots_tries_fifo(client, db_session):
    make_warehouse(db_session)
    make_lot(db_session, "RECENT", days_ago=5)
    make_lot(db_session, "ANCIEN", days_ago=200)

    resp = client.get("/lots")
    assert resp.status_code == 200
    ids = [lot["id"] for lot in resp.json()]
    assert ids == ["ANCIEN", "RECENT"]  # FIFO : plus ancien d'abord


def test_creer_lot(client, db_session):
    make_warehouse(db_session)

    payload = {
        "warehouseId": "w-br-1",
        "country": "brazil",
        "exploitation": "Fazenda Aurora",
        "weight": 1500,
        "variety": "Arabica",
        "grade": "Grade 1",
    }
    resp = client.post("/lots", json=payload)

    assert resp.status_code == 201
    body = resp.json()
    assert body["warehouseId"] == "w-br-1"
    assert body["status"] == "conforme"
    assert body["id"].startswith("FK-BR-")
    # Vérifie la persistance côté base.
    assert db_session.query(models.Lot).count() == 1


def test_creer_lot_entrepot_inconnu_renvoie_400(client):
    payload = {
        "warehouseId": "w-inexistant",
        "country": "brazil",
        "exploitation": "X",
        "weight": 100,
        "variety": "Arabica",
        "grade": "Grade 1",
    }
    resp = client.post("/lots", json=payload)
    assert resp.status_code == 400


def test_supprimer_lot(client, db_session):
    make_warehouse(db_session)
    make_lot(db_session, "FK-BR-DEL-001", days_ago=10)

    resp = client.delete("/lots/FK-BR-DEL-001")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert db_session.query(models.Lot).count() == 0


def test_supprimer_lot_inexistant_renvoie_404(client):
    resp = client.delete("/lots/PAS-LA")
    assert resp.status_code == 404


# ─── Mesures (capteurs) ──────────────────────────────────────────────────────
def test_lister_mesures_d_un_entrepot(client, db_session):
    make_warehouse(db_session)
    crud.add_measurement(db_session, "w-br-1", temperature=28.5, humidity=54.0)
    crud.add_measurement(db_session, "w-br-1", temperature=29.1, humidity=55.2)

    resp = client.get("/warehouses/w-br-1/sensors")
    assert resp.status_code == 200
    mesures = resp.json()
    assert len(mesures) == 2
    assert {"temperature", "humidity", "timestamp"} <= set(mesures[0].keys())


def test_sensors_current(client, db_session):
    make_warehouse(db_session, current_temp=30.0, current_humidity=56.0)

    resp = client.get("/sensors/current")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["warehouseId"] == "w-br-1"
    assert data[0]["temperature"] == 30.0


# ─── Alertes ─────────────────────────────────────────────────────────────────
def test_lister_alertes_vide(client):
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_lister_alertes_apres_mesure_hors_seuil(client, db_session):
    from app import alerts
    wh = make_warehouse(db_session)
    alerts.evaluate_measurement(db_session, wh, temperature=42.0, humidity=55.0)

    resp = client.get("/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["type"] == "temperature"
    assert data[0]["country"] == "brazil"


def test_alerts_count(client, db_session):
    wh = make_warehouse(db_session)
    crud.create_alert(
        db_session, type="temperature", severity="high", warehouse=wh,
        lot_id=None, message="msg", dedup_key="temperature:w-br-1",
    )

    resp = client.get("/alerts/count")
    assert resp.status_code == 200
    body = resp.json()
    assert body["active"] == 1
    assert body["total"] == 1


def test_filtre_alertes_par_type(client, db_session):
    wh = make_warehouse(db_session)
    crud.create_alert(
        db_session, type="temperature", severity="high", warehouse=wh,
        lot_id=None, message="t", dedup_key="temperature:w-br-1",
    )
    crud.create_alert(
        db_session, type="humidity", severity="high", warehouse=wh,
        lot_id=None, message="h", dedup_key="humidity:w-br-1",
    )

    resp = client.get("/alerts", params={"type": "humidity"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["type"] == "humidity"
