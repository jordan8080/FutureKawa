from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Pays(Base):
    __tablename__ = "pays"

    Id_pays = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50))
    temp_tolerance = Column(Numeric(15, 2))
    humidity_tolerance = Column(Numeric(15, 2))
    temp_min = Column(Numeric(15, 2))
    temp_max = Column(Numeric(15, 2))
    humidity_min = Column(Numeric(15, 2))
    humidity_max = Column(Numeric(15, 2))

    exploitations = relationship("Exploitation", back_populates="pays")


class Exploitation(Base):
    __tablename__ = "exploitation"

    Id_exploitation = Column(Integer, primary_key=True, index=True)
    ville = Column(String(50))
    adresse = Column(String(50))
    nom_exploitation = Column(String(50))
    Id_pays = Column(Integer, ForeignKey("pays.Id_pays"))

    pays = relationship("Pays", back_populates="exploitations")
    entrepots = relationship("Entrepot", back_populates="exploitation")


class Entrepot(Base):
    __tablename__ = "entrepot"

    Id_entrepot = Column(Integer, primary_key=True, index=True)
    localisation = Column(String(50))
    nom = Column(String(50))
    capacite_stockage = Column(Integer)
    Id_exploitation = Column(Integer, ForeignKey("exploitation.Id_exploitation"))

    exploitation = relationship("Exploitation", back_populates="entrepots")
    lots = relationship("Lot", back_populates="entrepot")
    mesures = relationship("Mesure", back_populates="entrepot")


class Lot(Base):
    __tablename__ = "lot"

    Id_lot = Column(Integer, primary_key=True, index=True)
    date_stockage = Column(Date)
    statut = Column(String(50), default="conforme")
    quantite = Column(Integer)
    date_expiration = Column(Date)
    Id_entrepot = Column(Integer, ForeignKey("entrepot.Id_entrepot"))

    entrepot = relationship("Entrepot", back_populates="lots")
    alerts = relationship("Alert", back_populates="lot")


class Mesure(Base):
    __tablename__ = "mesure"

    Id_measure = Column(Integer, primary_key=True, index=True)
    temperature = Column(Numeric(15, 2))
    humidite = Column(Numeric(15, 2))
    date_mesure = Column(DateTime, default=datetime.utcnow)
    Id_entrepot = Column(Integer, ForeignKey("entrepot.Id_entrepot"))

    entrepot = relationship("Entrepot", back_populates="mesures")


class Alert(Base):
    __tablename__ = "alert"

    Id_alert = Column(Integer, primary_key=True, index=True)
    message = Column(String(200))
    type_alerte = Column(String(50))
    niveau = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    Id_lot = Column(Integer, ForeignKey("lot.Id_lot"))

    lot = relationship("Lot", back_populates="alerts")
