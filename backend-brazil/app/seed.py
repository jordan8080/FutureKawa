"""
Initialisation des données de démonstration (idempotent).
Appelé au démarrage du backend : crée les tables si besoin et insère
un jeu de données Brésil seulement si la base est vide.
"""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import models


def seed_if_empty():
    # Crée les tables si elles n'existent pas
    models.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Ne seed qu'une seule fois
        if db.query(models.Pays).first():
            print("[SEED] Données déjà présentes — seeding ignoré")
            return

        print("[SEED] Base vide — insertion des données de démonstration")

        # --- Pays Brésil (seuils = idéal ± tolérance du cahier des charges) ---
        brazil = models.Pays(
            nom="Brazil",
            temp_tolerance=3.0,
            humidity_tolerance=2.0,
            temp_min=26.0, temp_max=32.0,      # 29°C ± 3
            humidity_min=53.0, humidity_max=57.0  # 55% ± 2
        )
        db.add(brazil)
        db.flush()

        # --- Exploitation ---
        expl = models.Exploitation(
            nom_exploitation="Exploitation São Paulo",
            ville="São Paulo",
            adresse="Rua do Café, 100",
            Id_pays=brazil.Id_pays
        )
        db.add(expl)
        db.flush()

        # --- Entrepôt ---
        entrepot = models.Entrepot(
            nom="Entrepôt Principal SP",
            localisation="Zone Sud, São Paulo",
            capacite_stockage=10000,
            Id_exploitation=expl.Id_exploitation
        )
        db.add(entrepot)
        db.flush()

        today = date.today()

        # --- Lots (cas variés pour la démo) ---
        lots = [
            # conforme
            models.Lot(date_stockage=today - timedelta(days=60), date_expiration=today + timedelta(days=300),
                       quantite=800, statut="conforme", Id_entrepot=entrepot.Id_entrepot),
            models.Lot(date_stockage=today - timedelta(days=120), date_expiration=today + timedelta(days=200),
                       quantite=600, statut="conforme", Id_entrepot=entrepot.Id_entrepot),
            # lot trop ancien (> 365 jours de stockage)
            models.Lot(date_stockage=today - timedelta(days=400), date_expiration=today + timedelta(days=90),
                       quantite=500, statut="conforme", Id_entrepot=entrepot.Id_entrepot),
            # pré-expiration (< 30 jours)
            models.Lot(date_stockage=today - timedelta(days=30), date_expiration=today + timedelta(days=20),
                       quantite=300, statut="conforme", Id_entrepot=entrepot.Id_entrepot),
            # expiré
            models.Lot(date_stockage=today - timedelta(days=370), date_expiration=today - timedelta(days=5),
                       quantite=200, statut="conforme", Id_entrepot=entrepot.Id_entrepot),
        ]
        db.add_all(lots)
        db.flush()

        # --- Mesures (dont une hors seuil) ---
        mesures = [
            models.Mesure(temperature=28.5, humidite=55.0,
                          date_mesure=datetime.utcnow() - timedelta(hours=2), Id_entrepot=entrepot.Id_entrepot),
            models.Mesure(temperature=29.0, humidite=54.5,
                          date_mesure=datetime.utcnow() - timedelta(hours=1), Id_entrepot=entrepot.Id_entrepot),
            models.Mesure(temperature=29.5, humidite=55.5,
                          date_mesure=datetime.utcnow(), Id_entrepot=entrepot.Id_entrepot),
        ]
        db.add_all(mesures)

        db.commit()
        print(f"[SEED] OK — 1 pays, 1 exploitation, 1 entrepôt, {len(lots)} lots, {len(mesures)} mesures")

    except Exception as e:
        db.rollback()
        print(f"[SEED] Erreur : {e}")
    finally:
        db.close()
