"""Configuration du backend pays.

Une seule image, paramétrée par la variable d'environnement COUNTRY
(brazil | ecuador | colombia). Les seuils, le responsable et l'email
proviennent du référentiel ci-dessous — identique à COUNTRIES_CONFIG du front.
"""
import os

# Référentiel des 3 pays (seuils du cahier des charges = tolérances du front).
COUNTRIES = {
    "brazil": {
        "id": "brazil", "name": "Brésil", "code": "BR", "emoji": "🇧🇷",
        "ideal_temp": 29, "ideal_humidity": 55,
        "tolerance_temp": 3, "tolerance_humidity": 2,
        "manager": "Carlos Oliveira", "manager_email": "c.oliveira@futurekawa.com",
    },
    "ecuador": {
        "id": "ecuador", "name": "Équateur", "code": "EC", "emoji": "🇪🇨",
        "ideal_temp": 31, "ideal_humidity": 60,
        "tolerance_temp": 3, "tolerance_humidity": 2,
        "manager": "María García", "manager_email": "m.garcia@futurekawa.com",
    },
    "colombia": {
        "id": "colombia", "name": "Colombie", "code": "CO", "emoji": "🇨🇴",
        "ideal_temp": 26, "ideal_humidity": 80,
        "tolerance_temp": 3, "tolerance_humidity": 2,
        "manager": "Andrés Martínez", "manager_email": "a.martinez@futurekawa.com",
    },
}

COUNTRY = os.getenv("COUNTRY", "brazil").lower()
if COUNTRY not in COUNTRIES:
    raise RuntimeError(
        f"COUNTRY='{COUNTRY}' invalide. Valeurs: {list(COUNTRIES)}"
    )

CONFIG = COUNTRIES[COUNTRY]

# Base de données (une base par pays).
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://futurekawa:futurekawa@localhost:5432/futurekawa_{COUNTRY}",
)

# Broker MQTT (partagé, topics namespacés par pays).
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = f"futurekawa/{COUNTRY}/+/measurement"

# Règles métier.
LOT_MAX_AGE_DAYS = int(os.getenv("LOT_MAX_AGE_DAYS", "365"))
LOT_NEAR_EXPIRY_DAYS = int(os.getenv("LOT_NEAR_EXPIRY_DAYS", "330"))

# Email (mode démo console si SMTP non configuré).
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "alertes@futurekawa.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


def temp_range():
    return (CONFIG["ideal_temp"] - CONFIG["tolerance_temp"],
            CONFIG["ideal_temp"] + CONFIG["tolerance_temp"])


def humidity_range():
    return (CONFIG["ideal_humidity"] - CONFIG["tolerance_humidity"],
            CONFIG["ideal_humidity"] + CONFIG["tolerance_humidity"])
