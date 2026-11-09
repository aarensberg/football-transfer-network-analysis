"""Carrières des joueurs formés dans un centre de formation et valeur captée par le club.

Les carrières sont reconstituées à partir de `transfers.csv` **brut**, pas du graphe
filtré : l'entrée au centre passe souvent par des clubs absents de `clubs.csv`
(ex. 54295, centre de formation du PSG, à l'origine des arrivées en U19).

Conventions (produit « Paris Talent Flow », voir `docs/PROJECT_LOG.md`, 2026-11-09) :
- organisation d'une académie = équipe première + équipes de jeunes et réserves ;
- joueur formé = première arrivée dans une équipe de jeunes ou réserve entre 2008
  et 2019 ;
- élite = 20 premiers clubs de la saison par valeur d'effectif (`club_league`).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

ENTRY_YEARS = (2008, 2019)
LAST_EVALUATED_DEPARTURE = 2021
ELITE_TOP_N = 20
ELITE_HORIZON = 3  # années après le départ pour « avoir joué dans l'élite »


@dataclass(frozen=True)
class Academy:
    """Centre de formation : équipe première et équipes de jeunes/réserves associées.

    L'association est manuelle : les données ne relient pas une réserve à son club.
    """

    name: str
    first_team: int
    youth_teams: frozenset[int]

    @property
    def organisation(self) -> frozenset[int]:
        """Toutes les équipes du club : un mouvement entre elles n'est pas un départ."""
        return self.youth_teams | {self.first_team}


# Identifiants vérifiés dans `clubs.csv` le 2026-11-09 (test `test_academy_ids_exist_in_clubs_csv`).
ACADEMIES: tuple[Academy, ...] = (
    Academy("PSG", 583, frozenset({6326, 8512})),
    Academy("Lyon", 1041, frozenset({7813, 12764})),
    Academy("Rennes", 273, frozenset({8154})),
    Academy("Monaco", 162, frozenset({9668, 9669})),
    Academy("Lille", 1082, frozenset({7875, 12765})),
    Academy("Marseille", 244, frozenset({8058, 8524})),
    Academy("Ajax", 610, frozenset({2824, 8817, 52068})),
    Academy("Benfica", 294, frozenset({10330, 41582, 68780})),
    Academy("Sporting CP", 336, frozenset({10949, 67909})),
    Academy("Barcelone", 131, frozenset({2464, 41584})),
    Academy("Real Madrid", 418, frozenset({6767, 92878})),
    Academy("Chelsea", 631, frozenset({6918, 9250, 41573})),
    Academy("Manchester City", 281, frozenset({6930, 9265})),
    Academy("Bayern", 27, frozenset({28, 1462, 21058})),
    Academy("Juventus", 506, frozenset({11008, 41101, 49567})),
)
PSG = ACADEMIES[0]


def prepare_moves(transfers: pd.DataFrame) -> pd.DataFrame:
    """Mouvements de carrière : sans « End of loan », avec l'ordre du fichier brut.

    `row` (position dans le fichier) sert seulement à un tri déterministe : l'ordre du
    fichier dans une même année n'est **pas** chronologique (revue du 2026-11-09 :
    56 % des paires consécutives d'une même année se lisent à l'envers). Les calculs
    raisonnent donc à l'année près.
    """
    moves = transfers.assign(row=range(len(transfers)))
    moves = moves[moves.transfer_type != "End of loan"]
    return moves.sort_values(["player_id", "year", "row"]).reset_index(drop=True)


def elite_seasons(
    club_league: pd.DataFrame, top_n: int = ELITE_TOP_N
) -> frozenset[tuple[int, int]]:
    """Couples (club, saison) des `top_n` clubs les plus valorisés de chaque saison.

    Un club présent dans deux ligues la même saison garde sa valeur maximale (évite la
    multiplication de lignes). Rang relatif à la saison : un seuil absolu gonflerait
    avec l'inflation des valeurs marchandes.
    """
    values = club_league.groupby(["club_id", "season"]).market_value.max()
    values = values[values > 0].reset_index()
    rank = values.groupby("season").market_value.rank(ascending=False, method="first")
    top = values[rank <= top_n]
    return frozenset(zip(top.club_id.astype(int), top.season.astype(int)))


def academy_players(
    moves: pd.DataFrame, academy: Academy, entry_years: tuple[int, int] = ENTRY_YEARS
) -> pd.Series:
    """Année d'entrée (première arrivée en jeunes/réserve) des joueurs formés, par joueur."""
    entries = moves[moves.joined_club_id.isin(academy.youth_teams)]
    first = entries.groupby("player_id").year.min()
    return first[first.between(*entry_years)]


def academy_departures(
    moves: pd.DataFrame, academy: Academy, players: pd.Index
) -> pd.DataFrame:
    """Départ définitif de chaque joueur formé : premier mouvement hors de l'organisation.

    Les prêts ne sont pas des départs, ni les mouvements entre équipes du club. Un
    pseudo-club en destination (retraite, sans club) compte : le joueur est libéré.
    Index : `player_id` ; colonnes `year, left_club_id, joined_club_id, transfer_fee, row`.
    """
    org = academy.organisation
    exits = moves[
        moves.player_id.isin(players)
        & moves.left_club_id.isin(org)
        & ~moves.joined_club_id.isin(org)
        & (moves.transfer_type != "Loan")
    ]
    columns = ["year", "left_club_id", "joined_club_id", "transfer_fee", "row"]
    # première ligne entière par joueur (`groupby().first()` mélangerait des lignes en
    # présence de valeurs manquantes)
    return exits.drop_duplicates("player_id").set_index("player_id")[columns]


def later_value(
    moves: pd.DataFrame,
    departures: pd.DataFrame,
    academy: Academy,
    elite: frozenset[tuple[int, int]],
) -> pd.DataFrame:
    """Ajoute aux départs la valeur réalisée ensuite, hors de l'organisation.

    Mouvements ultérieurs : ceux du joueur dont ni le club de départ ni le club
    d'arrivée n'appartient à l'organisation, de l'année du départ (l'ordre du fichier
    dans une année n'est pas fiable) à l'année du premier retour dans l'organisation
    depuis l'extérieur, incluses. Après un retour, la carrière relève d'un nouveau
    départ : un rachat, la revente par l'académie et les ventes suivantes ne comptent
    pas pour le premier départ.
    - `later_max_fee` : plus grosse indemnité ultérieure de transfert hors prêt (0 si
      aucune connue) ; une indemnité de prêt n'est pas une valeur de revente ;
    - `later_fee_sum` : somme de ces indemnités ;
    - `later_buyer` : club qui a payé `later_max_fee` (`<NA>` si aucune indemnité) ;
    - `reached_elite` : le joueur rejoint un club d'élite (le départ lui-même compris,
      prêts compris) au plus `ELITE_HORIZON` ans après le départ : même recul pour
      toutes les cohortes ;
    - `bought_back` : le joueur revient dans l'organisation depuis un autre club une
      année postérieure au départ (rachat ou retour), levier de récupération de valeur
      invisible dans `later_max_fee`. Les montées internes (réserve → équipe première)
      ne comptent pas, même enregistrées après la vente.
    """
    org = academy.organisation
    dep = departures[["year", "row"]].rename(
        columns={"year": "dep_year", "row": "dep_row"}
    )
    after = moves.merge(dep, left_on="player_id", right_index=True)
    after = after[(after.year >= after.dep_year) & (after.row != after.dep_row)]
    returns = after[
        after.joined_club_id.isin(org)
        & ~after.left_club_id.isin(org)
        & (after.year > after.dep_year)
    ]
    return_year = returns.groupby("player_id").year.min()
    cutoff = after.player_id.map(return_year)
    later = after[
        ~after.left_club_id.isin(org)
        & ~after.joined_club_id.isin(org)
        & (cutoff.isna() | (after.year <= cutoff))
    ]

    sales = later[later.transfer_type != "Loan"]
    out = departures.copy()
    out["later_max_fee"] = sales.groupby("player_id").transfer_fee.max()
    out["later_fee_sum"] = sales.groupby("player_id").transfer_fee.sum()
    out[["later_max_fee", "later_fee_sum"]] = out[
        ["later_max_fee", "later_fee_sum"]
    ].fillna(0.0)
    paid = sales[sales.transfer_fee > 0].sort_values(
        ["transfer_fee", "year", "row"], ascending=[False, True, True]
    )
    out["later_buyer"] = paid.groupby("player_id").joined_club_id.first()
    out["later_buyer"] = out.later_buyer.astype("Int64")

    def is_elite(frame: pd.DataFrame) -> pd.Series:
        flags = [(c, y) in elite for c, y in zip(frame.joined_club_id, frame.year)]
        return pd.Series(flags, index=frame.index, dtype=bool)

    soon = later[later.year <= later.dep_year + ELITE_HORIZON]
    later_elite = soon[is_elite(soon)].player_id.unique()
    out["reached_elite"] = is_elite(departures) | departures.index.isin(later_elite)
    out["bought_back"] = departures.index.isin(return_year.index)
    return out


def capture_ratio(df: pd.DataFrame) -> float:
    """Σ indemnités de départ / Σ plus grosses indemnités ultérieures (NaN si nulle)."""
    denominator = df.later_max_fee.sum()
    return float(df.transfer_fee.sum() / denominator) if denominator > 0 else np.nan


def bootstrap_capture_ci(
    df: pd.DataFrame, n_boot: int = 1000, seed: int = 42
) -> tuple[float, float]:
    """Intervalle à 95 % du ratio de capture par bootstrap sur les joueurs.

    Les tirages sans indemnité ultérieure (ratio indéfini) sont ignorés ; (NaN, NaN)
    si tous le sont.
    """
    fees = df.transfer_fee.to_numpy(float)
    later = df.later_max_fee.to_numpy(float)
    if len(df) == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(df), size=(n_boot, len(df)))
    num, den = fees[idx].sum(axis=1), later[idx].sum(axis=1)
    ratios = np.divide(num, den, out=np.full(n_boot, np.nan), where=den > 0)
    if np.isnan(ratios).all():
        return (np.nan, np.nan)
    low, high = np.nanpercentile(ratios, [2.5, 97.5])
    return (float(low), float(high))


def academy_summary(
    moves: pd.DataFrame,
    elite: frozenset[tuple[int, int]],
    academies: tuple[Academy, ...] = ACADEMIES,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Comparatif des académies et détail des départs par académie.

    Le tableau (index : nom de l'académie) ne compte que les départs évaluables
    (année ≤ `LAST_EVALUATED_DEPARTURE`) ; le détail les garde tous, avec `evaluable`.
    Montants en euros.
    """
    rows, detail = [], {}
    for academy in academies:
        players = academy_players(moves, academy)
        departures = academy_departures(moves, academy, players.index)
        values = later_value(moves, departures, academy, elite)
        values["entry_year"] = players.reindex(values.index)
        values["evaluable"] = values.year <= LAST_EVALUATED_DEPARTURE
        detail[academy.name] = values

        ev = values[values.evaluable]
        low, high = bootstrap_capture_ci(ev)
        rest = ev.drop(ev.later_max_fee.nlargest(2).index)
        rows.append(
            {
                "academy": academy.name,
                "players": len(players),
                "departures": len(ev),
                "paid_departures": int((ev.transfer_fee > 0).sum()),
                "departure_fees": ev.transfer_fee.sum(),
                "later_paid": int((ev.later_max_fee > 0).sum()),
                "later_ge_10m": int((ev.later_max_fee >= 10e6).sum()),
                "later_max_sum": ev.later_max_fee.sum(),
                "capture_ratio": capture_ratio(ev),
                "ci_low": low,
                "ci_high": high,
                "ratio_without_top2": capture_ratio(rest),
                "reached_elite_share": ev.reached_elite.mean() if len(ev) else np.nan,
                "bought_back": int(ev.bought_back.sum()),
            }
        )
    return pd.DataFrame(rows).set_index("academy"), detail


def pooled_departures(detail: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Départs de plusieurs académies regroupés, une ligne par joueur.

    Un joueur passé par deux centres (ex. Denis Suárez) n'est compté qu'une fois, avec
    son premier départ ; colonne `academy` ajoutée.
    """
    frames = [df.assign(academy=name) for name, df in detail.items()]
    pooled = pd.concat(frames).rename_axis("player_id").reset_index()
    pooled = pooled.sort_values(["player_id", "year"], kind="stable")
    return pooled.drop_duplicates("player_id").set_index("player_id")
