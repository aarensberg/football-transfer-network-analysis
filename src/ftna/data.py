"""Chargement des fichiers bruts du dataset (lecture seule de `data/raw/`)."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Racine du dépôt : src/ftna/data.py -> parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Pseudo-clubs utilisés par Transfermarkt pour des situations qui ne sont pas des clubs.
# -5 et 75 sont nommés dans clubs.csv ; 515 n'y figure pas et son sens est déduit
# des données (voir docs/PROJECT_LOG.md) : joueur sans club / libre.
RETIRED_ID = -5
UNKNOWN_ID = 75
WITHOUT_CLUB_ID = 515
PSEUDO_CLUB_IDS = frozenset({RETIRED_ID, UNKNOWN_ID, WITHOUT_CLUB_ID})

# Heuristiques (pas de lien club parent dans les données) repérant les équipes de
# jeunes et réserves d'après le nom du club ou celui de sa ligue. Révisées après
# vérification manuelle (voir docs/PROJECT_LOG.md, 2026-11-09) :
# - « B » et « II » seulement en fin de nom ou avant une parenthèse ou « / »
#   (« Sparta Prague B », « Kjöbenhavns Boldklub (FCK II) »), pas « Willem II Tilburg »
#   ni « Holbaek B&I » ;
# - « Juniors » n'est pas un marqueur fiable (Boca Juniors, Argentinos Juniors sont
#   des équipes premières) : seules les réserves autrichiennes et équatoriennes
#   connues sont retenues ;
# - suffixe « 2 » des équipes réserves russes, ukrainiennes et de MLS (« Zenit 2 »,
#   « Portland Timbers 2 »), sauf noms de dates (« 2 de Mayo », « 2 Korriku ») ;
# - « Under 17 » (équipes italiennes) et « Amateure » (réserves autrichiennes).
YOUTH_RESERVE_PATTERN = (
    r"\b(?:U-?\d{2}|Under[ -]?\d{2}|Sub[- ]?\d{2}|Youth|Primavera|Castilla|Jong"
    r"|Academy|Reserves?|Reservas?|Juniorit)\b"
    r"|\bAmateure\b(?! Steyr)"
    r"|\b(?:B|II)(?=\s*(?:$|[()/]))"
    r"|[\s-]2\b(?! (?:de|Korriku)\b)"
    r"|\b(?:St\. Pölten|Altach|Red Bull|Independiente) Juniors\b|\bJuniors OÖ\b"
)
YOUTH_LEAGUE_PATTERN = (
    r"U\d{2}|Under \d{2}|\bO\d{2}\b|Youth|Junior|Reserve|Primavera|Sub-|Nachwuchs"
)


@dataclass(frozen=True)
class RawData:
    """Les cinq tables brutes, sans aucune transformation."""

    transfers: pd.DataFrame
    clubs: pd.DataFrame
    leagues: pd.DataFrame
    club_league: pd.DataFrame
    players: pd.DataFrame


def load_raw(
    raw_dir: Path = RAW_DIR, players_columns: list[str] | None = None
) -> RawData:
    """Charge les CSV bruts.

    `players.csv` est volumineux : `players_columns` permet de n'en lire qu'une partie.
    """
    # `id_current_league` et les identifiants de ligue sont des codes texte (ex. "GB1").
    return RawData(
        transfers=pd.read_csv(raw_dir / "transfers.csv"),
        clubs=pd.read_csv(raw_dir / "clubs.csv", dtype={"id_current_league": "string"}),
        leagues=pd.read_csv(raw_dir / "leagues.csv", dtype={"id": "string"}),
        club_league=pd.read_csv(
            raw_dir / "club_league.csv", dtype={"league_id": "string"}
        ),
        players=pd.read_csv(raw_dir / "players.csv", usecols=players_columns),
    )
