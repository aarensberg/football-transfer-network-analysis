"""Clubs tremplins : d'où les joueurs atteignent-ils l'élite en un ou deux transferts ?

Pour chaque sortie définitive d'un club hors élite, on regarde si le joueur rejoint un
club d'élite directement (même mouvement) ou au mouvement suivant (hors prêt) dans un
horizon de 3 ans. C'est une atteignabilité en k ≤ 2 sauts sur les chemins de carrière,
pas sur le graphe agrégé (qui ne conserve pas l'identité des joueurs).

Élite : `ftna.careers.elite_seasons` (20 premiers clubs de la saison par valeur).
"""

import math

import pandas as pd

from ftna.data import PSEUDO_CLUB_IDS

# Réserves non détectées par `YOUTH_RESERVE_PATTERN` (vérifiées le 2026-11-09) : leurs
# « sorties » vers l'équipe première sont des promotions internes, pas des tremplins.
EXTRA_RESERVE_IDS = frozenset(
    {
        2464,  # FC Barcelona Atlètic
        6182,  # Valencia Mestalla
        41101,  # Juventus Next Gen
        8519,  # Sevilla Atlético
    }
)
EXIT_YEARS = (2010, 2020)
HORIZON = 3
MIN_EXITS = 30
EARLY_PERIOD_END = (
    2015  # 2010–2015 contre 2016–2020 pour repérer les tremplins émergents
)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalle de confiance de Wilson d'une proportion k / n (NaN si n = 0).

    Préféré à l'intervalle de Wald, faux pour les petites proportions et petits n.
    """
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (center - half, center + half)


def _in_elite(
    clubs: pd.Series, years: pd.Series, elite: frozenset[tuple[int, int]]
) -> pd.Series:
    flags = [(c, y) in elite for c, y in zip(clubs, years)]
    return pd.Series(flags, index=clubs.index, dtype=bool)


def springboard_exits(
    moves: pd.DataFrame,
    elite: frozenset[tuple[int, int]],
    excluded_sources: frozenset[int],
    exit_years: tuple[int, int] = EXIT_YEARS,
    horizon: int = HORIZON,
) -> pd.DataFrame:
    """Sorties définitives des clubs hors élite et atteinte de l'élite.

    Sortie : mouvement `Not loan` ou `Unknown` vers un vrai club, depuis un club ni
    exclu ni dans l'élite cette saison-là. Sont exclus les joueurs arrivés dans la
    source par un prêt depuis un club d'élite (mouvement précédent) et les retours vers
    un club qui avait prêté le joueur à la source : leur « montée » est un retour.
    - `direct` : l'arrivée est un club d'élite la saison du mouvement ;
    - `two_hop` : sinon, le mouvement suivant du joueur, hors prêt, arrive dans
      l'élite au plus tard `horizon` ans après ;
    - `reached` = `direct` ou `two_hop`.
    `moves` doit venir de `ftna.careers.prepare_moves` (trié par joueur et ordre).
    """
    by_player = moves.groupby("player_id")
    frame = moves.assign(
        prev_type=by_player.transfer_type.shift(1),
        prev_left=by_player.left_club_id.shift(1),
        prev_year=by_player.year.shift(1),
        next_joined=by_player.joined_club_id.shift(-1),
        next_year=by_player.year.shift(-1),
        next_type=by_player.transfer_type.shift(-1),
    )
    exits = frame[
        frame.year.between(*exit_years)
        & frame.transfer_type.isin(["Not loan", "Unknown"])
        & ~frame.joined_club_id.isin(PSEUDO_CLUB_IDS)
        & ~frame.left_club_id.isin(excluded_sources)
    ]
    exits = exits[~_in_elite(exits.left_club_id, exits.year, elite)]
    loaned_in = (exits.prev_type == "Loan") & _in_elite(
        exits.prev_left, exits.prev_year, elite
    )
    exits = exits[~loaned_in]

    # Retour vers un club qui avait prêté le joueur à la source (à n'importe quel
    # moment avant, ou la même année quel que soit l'ordre du fichier) : pas un tremplin.
    loans = moves.loc[
        moves.transfer_type == "Loan",
        ["player_id", "left_club_id", "joined_club_id", "year"],
    ].rename(
        columns={
            "left_club_id": "lender",
            "joined_club_id": "borrower",
            "year": "loan_year",
        }
    )
    pairs = exits.reset_index().merge(
        loans,
        left_on=["player_id", "left_club_id", "joined_club_id"],
        right_on=["player_id", "borrower", "lender"],
    )
    back_to_lender = set(pairs.loc[pairs.loan_year <= pairs.year, "index"])
    exits = exits[~exits.index.isin(back_to_lender)]

    direct = _in_elite(exits.joined_club_id, exits.year, elite)
    two_hop = (
        ~direct
        & (exits.next_type != "Loan")
        & exits.next_type.notna()
        & (exits.next_year <= exits.year + horizon)
        & _in_elite(exits.next_joined, exits.next_year, elite)
    )
    columns = ["player_id", "left_club_id", "joined_club_id", "year", "transfer_fee"]
    return exits[columns].assign(
        direct=direct, two_hop=two_hop, reached=direct | two_hop
    )


def springboard_rates(exits: pd.DataFrame, min_exits: int = MIN_EXITS) -> pd.DataFrame:
    """Taux d'atteinte de l'élite par club source, avec intervalle de Wilson.

    Clubs avec au moins `min_exits` sorties, triés par borne basse décroissante (un
    taux élevé sur peu de sorties ne passe pas devant un taux solide).
    """
    early = exits.year <= EARLY_PERIOD_END
    exits = exits.assign(
        exits_early=early,
        exits_late=~early,
        reached_early=exits.reached & early,
        reached_late=exits.reached & ~early,
    )
    rates = exits.groupby("left_club_id").agg(
        exits=("player_id", "size"),
        direct=("direct", "sum"),
        two_hop=("two_hop", "sum"),
        reached=("reached", "sum"),
        exits_early=("exits_early", "sum"),
        exits_late=("exits_late", "sum"),
        reached_early=("reached_early", "sum"),
        reached_late=("reached_late", "sum"),
    )
    rates = rates[rates.exits >= min_exits].copy()
    rates["rate"] = rates.reached / rates.exits
    bounds = [wilson_interval(k, n) for k, n in zip(rates.reached, rates.exits)]
    rates["ci_low"] = [low for low, _ in bounds]
    rates["ci_high"] = [high for _, high in bounds]
    # taux par période (NaN si aucune sortie) : les comptes bruts ne sont pas
    # comparables entre périodes de longueurs et d'activité différentes
    for period in ("early", "late"):
        n = rates[f"exits_{period}"]
        rates[f"rate_{period}"] = rates[f"reached_{period}"] / n.where(n > 0)
    order = ["exits", "direct", "two_hop", "reached", "rate", "ci_low", "ci_high"]
    periods = [
        f"{kind}_{period}"
        for period in ("early", "late")
        for kind in ("exits", "reached", "rate")
    ]
    rates = rates[[*order, *periods]]
    return rates.sort_values(["ci_low", "exits"], ascending=[False, False])
