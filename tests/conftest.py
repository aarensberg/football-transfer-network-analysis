"""Utilitaires partagés par les tests (données synthétiques)."""

import pandas as pd

COLUMNS = [
    "player_id",
    "year",
    "left_club_id",
    "joined_club_id",
    "transfer_fee",
    "transfer_type",
]


def frame(rows: list[tuple]) -> pd.DataFrame:
    """Table de transferts au format brut à partir de tuples ordonnés comme `COLUMNS`."""
    df = pd.DataFrame(rows, columns=COLUMNS)
    return df.astype({"transfer_fee": float})
