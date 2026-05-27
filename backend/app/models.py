from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


# =========================
# PAYS
# =========================

class Pays(Base):
    __tablename__ = "pays"

    id_pays = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50))
    temp_tolerance = Column(Numeric(15, 2))
    humidity_tolerance = Column(Numeric(15, 2))

    exploitations = relationship("Exploitation", back_populates="pays")


# =========================
# EXPLOITATION
# =========================

class Exploitation(Base):
    __tablename__ = "exploitation"

    id_exploitation = Column(Integer, primary_key=True, index=True)
    ville = Column(String(50))
    adresse = Column(String(50))
    nom_exploitation = Column(String(50))

    id_pays = Column(Integer, ForeignKey("pays.id_pays"))

    pays = relationship("Pays", back_populates="exploitations")

    entrepots = relationship("Entrepot", back_populates="exploitation")


# =========================
# ENTREPOT
# =========================

class Entrepot(Base):
    __tablename__ = "entrepot"

    id_entrepot = Column(Integer, primary_key=True, index=True)
    localisation = Column(String(50))
    nom = Column(String(50))
    capacite_stockage = Column(Integer)

    id_exploitation = Column(
        Integer,
        ForeignKey("exploitation.id_exploitation")
    )

    exploitation = relationship(
        "Exploitation",
        back_populates="entrepots"
    )

    lots = relationship("Lot", back_populates="entrepot")

    mesures = relationship("Mesure", back_populates="entrepot")


# =========================
# LOT
# =========================

class Lot(Base):
    __tablename__ = "lot"

    id_lot = Column(Integer, primary_key=True, index=True)

    date_stockage = Column(Date)

    statut = Column(
    String(50),
    default="conforme"
)

    quantite = Column(Integer)

    date_expiration = Column(Date)

    id_entrepot = Column(
        Integer,
        ForeignKey("entrepot.id_entrepot")
    )

    entrepot = relationship("Entrepot", back_populates="lots")

    alerts = relationship("Alert", back_populates="lot")
    created_at = Column(
    DateTime
)


# =========================
# MESURE
# =========================

class Mesure(Base):
    __tablename__ = "mesure"

    id_measure = Column(Integer, primary_key=True, index=True)

    temperature = Column(Numeric(15, 2))

    humidite = Column(Numeric(15, 2))

    date_mesure = Column(DateTime, default=datetime.utcnow)

    id_entrepot = Column(
        Integer,
        ForeignKey("entrepot.id_entrepot")
    )

    entrepot = relationship("Entrepot", back_populates="mesures")


# =========================
# ALERT
# =========================

class Alert(Base):
    __tablename__ = "alert"

    id_alert = Column(Integer, primary_key=True, index=True)

    message = Column(String(50))

    type_alerte = Column(String(50))

    niveau = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)

    id_lot = Column(
        Integer,
        ForeignKey("lot.id_lot")
    )

    lot = relationship("Lot", back_populates="alerts")