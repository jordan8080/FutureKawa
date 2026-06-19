"""Tables SQLAlchemy (une base par pays)."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    exploitation = Column(String, nullable=False)
    current_temp = Column(Float, nullable=False, default=0.0)
    current_humidity = Column(Float, nullable=False, default=0.0)


class Lot(Base):
    __tablename__ = "lots"

    id = Column(String, primary_key=True)
    warehouse_id = Column(String, ForeignKey("warehouses.id"), nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    exploitation = Column(String, nullable=False)
    stored_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="conforme")  # conforme|alerte|perime|expedie
    weight = Column(Integer, nullable=False)
    variety = Column(String, nullable=False)
    grade = Column(String, nullable=False)


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String, ForeignKey("warehouses.id"), nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)       # temperature|humidity|lot_age
    severity = Column(String, nullable=False)   # critical|high|medium|low
    country = Column(String, nullable=False, index=True)
    warehouse_id = Column(String, nullable=False)
    warehouse_name = Column(String, nullable=False)
    lot_id = Column(String, nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    status = Column(String, nullable=False, default="active")  # active|resolved
    dedup_key = Column(String, nullable=False, index=True)
