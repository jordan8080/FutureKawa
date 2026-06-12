from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ========================
# PAYS
# ========================

class PaysResponse(BaseModel):
    Id_pays: int
    nom: Optional[str]
    temp_min: Optional[float]
    temp_max: Optional[float]
    humidity_min: Optional[float]
    humidity_max: Optional[float]

    class Config:
        from_attributes = True


# ========================
# ENTREPOT
# ========================

class EntrepotCreate(BaseModel):
    nom: str
    localisation: str
    capacite_stockage: int
    Id_exploitation: int


class EntrepotResponse(BaseModel):
    Id_entrepot: int
    nom: Optional[str]
    localisation: Optional[str]
    capacite_stockage: Optional[int]

    class Config:
        from_attributes = True


# ========================
# LOT
# ========================

class LotCreate(BaseModel):
    date_stockage: date
    statut: str = "conforme"
    quantite: int
    date_expiration: date
    Id_entrepot: int


class LotResponse(BaseModel):
    Id_lot: int
    date_stockage: Optional[date]
    statut: Optional[str]
    quantite: Optional[int]
    date_expiration: Optional[date]
    Id_entrepot: Optional[int]

    class Config:
        from_attributes = True


# ========================
# MESURE
# ========================

class MesureCreate(BaseModel):
    temperature: float
    humidite: float
    Id_entrepot: int


class MesureResponse(BaseModel):
    Id_measure: int
    temperature: Optional[float]
    humidite: Optional[float]
    date_mesure: Optional[datetime]
    Id_entrepot: Optional[int]

    class Config:
        from_attributes = True


# ========================
# ALERT
# ========================

class AlertResponse(BaseModel):
    Id_alert: int
    message: Optional[str]
    type_alerte: Optional[str]
    niveau: Optional[str]
    created_at: Optional[datetime]
    Id_lot: Optional[int]

    class Config:
        from_attributes = True
