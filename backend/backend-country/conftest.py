"""Configuration commune des tests (fixtures + base isolée).

Placé à la RACINE de backend-country : pytest insère ce dossier dans sys.path,
donc `import app.xxx` fonctionne sans installer le package.

Choix d'isolation :
- On force COUNTRY=brazil et SMTP_HOST="" AVANT d'importer l'app, pour figer
  les seuils testés et garder l'email en mode console (aucun envoi réseau).
- Base SQLite EN MÉMOIRE (StaticPool) : on ne touche jamais au PostgreSQL réel.
- Le TestClient est créé SANS context manager : le lifespan de l'app
  (connexion Postgres + MQTT + seed + thread d'âge) n'est donc PAS déclenché.
"""
import os

# IMPORTANT : doit être défini avant tout import de app.config / app.database.
os.environ.setdefault("COUNTRY", "brazil")
os.environ["SMTP_HOST"] = ""  # mode démo console → pas d'envoi SMTP réel
os.environ.setdefault("DATABASE_URL", "sqlite://")  # garde-fou : jamais Postgres en test

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (enregistre les tables sur Base.metadata)
from app.database import Base, get_db
from app.main import app

# Un seul moteur SQLite en mémoire, partagé entre threads (StaticPool).
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=TEST_ENGINE, autocommit=False, autoflush=False
)


@pytest.fixture()
def db_session():
    """Session DB isolée : schéma créé puis supprimé à chaque test."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def client(db_session):
    """TestClient FastAPI utilisant la base de test (get_db surchargé)."""
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    # Pas de `with` : on évite volontairement le lifespan (Postgres/MQTT/seed).
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()


# ─── Helpers de fabrication de données (réutilisés par plusieurs tests) ──────
def make_warehouse(db, wid="w-br-1", name="Entrepôt Test", **kwargs):
    wh = models.Warehouse(
        id=wid,
        name=name,
        country="brazil",
        location=kwargs.get("location", "São Paulo"),
        exploitation=kwargs.get("exploitation", "Fazenda Test"),
        current_temp=kwargs.get("current_temp", 29.0),
        current_humidity=kwargs.get("current_humidity", 55.0),
    )
    db.add(wh)
    db.commit()
    return wh


def make_lot(db, lid, warehouse_id="w-br-1", days_ago=10, status="conforme", **kwargs):
    from datetime import datetime, timedelta, timezone
    lot = models.Lot(
        id=lid,
        warehouse_id=warehouse_id,
        country="brazil",
        exploitation=kwargs.get("exploitation", "Fazenda Test"),
        stored_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
        status=status,
        weight=kwargs.get("weight", 1000),
        variety=kwargs.get("variety", "Arabica"),
        grade=kwargs.get("grade", "Grade 1"),
    )
    db.add(lot)
    db.commit()
    return lot
