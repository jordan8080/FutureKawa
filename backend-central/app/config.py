import os

# Registre des pays connectés
# Pour ajouter un pays : ajouter ici l'URL de son backend
COUNTRIES = {
    "brazil": os.getenv("BRAZIL_API_URL", "http://localhost:8000"),
    # "colombia": os.getenv("COLOMBIA_API_URL", "http://localhost:8002"),
    # "ecuador":  os.getenv("ECUADOR_API_URL",  "http://localhost:8003"),
}

COUNTRY_NAMES = {
    "brazil": "Brésil",
    "colombia": "Colombie",
    "ecuador": "Équateur",
}
