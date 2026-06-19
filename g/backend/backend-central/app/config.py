"""Registre des backends pays interrogés par le central."""
import os

COUNTRIES = {
    "brazil": {
        "id": "brazil", "name": "Brésil", "code": "BR", "emoji": "🇧🇷",
        "url": os.getenv("BRAZIL_URL", "http://backend-brazil:8000"),
    },
    "ecuador": {
        "id": "ecuador", "name": "Équateur", "code": "EC", "emoji": "🇪🇨",
        "url": os.getenv("ECUADOR_URL", "http://backend-ecuador:8000"),
    },
    "colombia": {
        "id": "colombia", "name": "Colombie", "code": "CO", "emoji": "🇨🇴",
        "url": os.getenv("COLOMBIA_URL", "http://backend-colombia:8000"),
    },
}

def code_to_country():
    """Map dynamique code (BR/EC/CO) -> id pays (recalculée car le registre évolue)."""
    return {c["code"].upper(): c["id"] for c in COUNTRIES.values()}


def add_country(country: dict):
    COUNTRIES[country["id"]] = country


def remove_country(country_id: str):
    return COUNTRIES.pop(country_id, None)

# Origine autorisée pour CORS (utile si le front attaque le central en direct).
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
