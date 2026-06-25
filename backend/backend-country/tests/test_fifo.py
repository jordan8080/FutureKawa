"""Tests unitaires du tri FIFO (First In, First Out) — app.crud.

Règle métier : on expédie en priorité les lots les plus anciens.
`get_lots` trie par stored_at ASC ; `fifo` fait de même en excluant les expédiés.
"""
from app import crud
from conftest import make_lot, make_warehouse


def test_get_lots_tri_du_plus_ancien_au_plus_recent(db_session):
    make_warehouse(db_session)
    # Insertion volontairement dans le désordre.
    make_lot(db_session, "LOT-RECENT", days_ago=10)
    make_lot(db_session, "LOT-ANCIEN", days_ago=300)
    make_lot(db_session, "LOT-MOYEN", days_ago=100)

    lots = crud.get_lots(db_session)
    ids = [lot.id for lot in lots]

    assert ids == ["LOT-ANCIEN", "LOT-MOYEN", "LOT-RECENT"]


def test_fifo_ordonne_les_plus_anciens_en_premier(db_session):
    make_warehouse(db_session)
    make_lot(db_session, "A", days_ago=5)
    make_lot(db_session, "B", days_ago=50)
    make_lot(db_session, "C", days_ago=500, status="conforme")

    fifo = crud.fifo(db_session, limit=10)
    ids = [lot.id for lot in fifo]

    # Plus ancien (C=500j) d'abord, plus récent (A=5j) en dernier.
    assert ids == ["C", "B", "A"]


def test_fifo_exclut_les_lots_expedies(db_session):
    make_warehouse(db_session)
    make_lot(db_session, "EXPEDIE", days_ago=400, status="expedie")
    make_lot(db_session, "EN-STOCK", days_ago=20, status="conforme")

    fifo = crud.fifo(db_session, limit=10)
    ids = [lot.id for lot in fifo]

    assert "EXPEDIE" not in ids
    assert ids == ["EN-STOCK"]


def test_fifo_respecte_la_limite(db_session):
    make_warehouse(db_session)
    for i in range(5):
        make_lot(db_session, f"LOT-{i}", days_ago=100 - i * 10)

    fifo = crud.fifo(db_session, limit=2)

    assert len(fifo) == 2
    # Les 2 plus anciens : days_ago=100 (LOT-0) puis 90 (LOT-1).
    assert [lot.id for lot in fifo] == ["LOT-0", "LOT-1"]
