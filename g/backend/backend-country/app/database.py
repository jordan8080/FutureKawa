"""Connexion PostgreSQL (SQLAlchemy)."""
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(retries: int = 30, delay: float = 2.0):
    """Attend que Postgres soit prêt (utile au démarrage Docker)."""
    last_err = None
    for _ in range(retries):
        try:
            with engine.connect():
                return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(delay)
    raise RuntimeError(f"Base de données indisponible: {last_err}")


def init_db():
    from . import models  # noqa: F401  (enregistre les tables)
    Base.metadata.create_all(bind=engine)
