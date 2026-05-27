from pydantic import BaseModel
from datetime import date, datetime


# =========================
# LOT
# =========================

class LotCreate(BaseModel):
    date_stockage: date
    statut: str
    quantite: int
    date_expiration: date
    id_entrepot: int


class LotResponse(BaseModel):
    id_lot: int
    statut: str
    quantite: int

    class Config:
        orm_mode = True


# =========================
# MESURE
# =========================

class MesureCreate(BaseModel):
    temperature: float
    humidite: float
    id_entrepot: int


# =========================
# ALERT
# =========================

class AlertResponse(BaseModel):
    id_alert: int
    message: str
    type_alerte: str
    niveau: str

    class Config:
        orm_mode = True