from datetime import date
from datetime import timedelta

from . import models


# ====================
# CONDITIONS
# ====================

def is_temperature_invalid(
    temperature,
    pays
):

    return (
        temperature < pays.temp_min
        or
        temperature > pays.temp_max
    )


def is_humidity_invalid(
    humidite,
    pays
):

    return (
        humidite < pays.humidity_min
        or
        humidite > pays.humidity_max
    )


# ====================
# EXPIRATION
# ====================

def lot_expired(lot):

    return (
        lot.date_expiration
        <=
        date.today()
    )


def lot_approaching_expiration(
    lot
):

    return (
        lot.date_expiration
        <=
        date.today()
        + timedelta(days=30)
    )