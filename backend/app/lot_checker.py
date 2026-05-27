from datetime import date
from sqlalchemy.orm import Session

from . import models

from .alerts import (
    lot_expired,
    lot_approaching_expiration
)


def update_lot_status(
    db: Session
):

    lots = db.query(
        models.Lot
    ).all()

    for lot in lots:

        if lot_expired(lot):

            lot.statut = "expire"

        elif lot_approaching_expiration(lot):

            lot.statut = "expiration_proche"

        else:

            lot.statut = "conforme"

    db.commit()