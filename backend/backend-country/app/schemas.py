"""Schémas Pydantic — sérialisés en camelCase pour coller au front."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class WarehouseOut(CamelModel):
    id: str
    name: str
    country: str
    location: str
    exploitation: str
    current_temp: float
    current_humidity: float


class LotOut(CamelModel):
    id: str
    warehouse_id: str
    country: str
    exploitation: str
    stored_at: datetime
    status: str
    weight: int
    variety: str
    grade: str


class LotCreate(CamelModel):
    warehouse_id: str
    country: str
    exploitation: str
    weight: int
    variety: str
    grade: str


class StatusUpdate(CamelModel):
    status: str


class WarehouseCreate(CamelModel):
    name: str
    location: str
    exploitation: str


class MeasurementOut(CamelModel):
    timestamp: datetime
    temperature: float
    humidity: float


class SensorLatest(CamelModel):
    warehouse_id: str
    warehouse_name: str
    timestamp: Optional[datetime] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None


class SensorCurrent(CamelModel):
    warehouse_id: str
    warehouse_name: str
    country: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    last_updated: Optional[datetime] = None


class AlertOut(CamelModel):
    id: str
    type: str
    severity: str
    country: str
    warehouse_id: str
    warehouse_name: str
    lot_id: Optional[str] = None
    message: str
    created_at: datetime
    status: str


class AlertCount(CamelModel):
    active: int
    total: int
