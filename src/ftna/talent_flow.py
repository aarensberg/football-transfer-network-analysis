"""Produit « Paris Talent Flow » : où partent les joueurs formés au PSG et qui capte leur valeur ?

Outil d'aide à la décision pour le directeur sportif du PSG (voir `docs/PROJECT_LOG.md`,
2026-11-09). Quatre volets :
1. radar de fuite : carrière des joueurs formés, valeur réalisée ailleurs, comparatif
   de 15 académies (`ftna.careers`) ;
2. tremplins : clubs d'où les joueurs atteignent l'élite en 1 ou 2 sauts
   (`ftna.springboards`) ;
3. concurrents : clubs étrangers qui recrutent dans les équipes de jeunes françaises ;
4. comparables : valeur ultérieure par poste et âge au départ, pour fixer les clauses.
Analyses de graphe : PageRank personnalisé depuis le PSG, communautés Louvain (A5),
coefficient de participation (A10).

Usage : `uv run python -m ftna.talent_flow` (après `ftna.communities` et `ftna.roles`)
Sorties : `results/talent_flow.md`, `results/tables/talent_flow_*.csv`,
`results/figures/{academy_value_capture,springboards}.{pdf,png}`.
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from ftna.careers import (
    ACADEMIES,
    ELITE_HORIZON,
    ELITE_TOP_N,
    ENTRY_YEARS,
    LAST_EVALUATED_DEPARTURE,
    PSG,
    academy_summary,
    elite_seasons,
    pooled_departures,
    prepare_moves,
)
from ftna.common import (
    NEUTRAL,
    SERIES,
    TABLES_DIR,
    TEXT_SECONDARY,
    main_graph,
    md_table,
    save_figure,
    save_table,
    setup_style,
    write_report,
)
from ftna.data import RETIRED_ID, UNKNOWN_ID, WITHOUT_CLUB_ID, load_raw
from ftna.graph import GraphConfig, filter_transfers
from ftna.springboards import (
    EXIT_YEARS,
    EXTRA_RESERVE_IDS,
    HORIZON,
    MIN_EXITS,
    springboard_exits,
    springboard_rates,
)

SENSITIVITY_TOP_N = 30
FRENCH_ACADEMIES = ("PSG", "Lyon", "Rennes", "Monaco", "Lille", "Marseille")
BRIDGE_P = 0.6  # seuil de participation d'un club passerelle (A10)
MIN_CELL = 10  # effectif minimal d'une cellule de comparables
MIN_PAID = 5  # joueurs revendus minimaux pour afficher les quantiles
MIN_PERIOD_EXITS = 15  # sorties minimales par période pour comparer des taux
COMPETITOR_PERIODS = ((2010, 2016), (2017, 2023))
AGE_BANDS = ((0, 19, "≤ 19"), (20, 21, "20–21"), (22, 23, "22–23"), (24, 99, "≥ 24"))
POSITIONS = {
    "Goalkeeper": "Gardien",
    "Defender": "Défenseur",
    "Midfield": "Milieu",
    "Attack": "Attaquant",
}
PSEUDO_LABELS = {
    RETIRED_ID: "Retraite",
    UNKNOWN_ID: "Inconnu",
    WITHOUT_CLUB_ID: "Sans club",
}


def meur(value: float) -> str:
    """Montant en millions d'euros, une décimale."""
    return f"{value / 1e6:.1f}"


class Clubs:
    """Libellés des clubs : nom de `clubs.csv` et pays du graphe principal."""

    def __init__(self, clubs: pd.DataFrame, graph: nx.DiGraph) -> None:
        self.names = clubs.set_index("id").club_name
        self.country = pd.Series(dict(graph.nodes(data="country")), dtype=object)

    def name(self, club: object) -> str:
        if pd.isna(club):
            return ""
        club = int(club)
        if club in PSEUDO_LABELS:
            return PSEUDO_LABELS[club]
        return str(self.names.get(club, f"club {club}"))

    def label(self, club: object) -> str:
        """Nom suivi du pays, si connu."""
        name = self.name(club)
        country = self.country.get(int(club)) if not pd.isna(club) else None
        return f"{name} ({country})" if country else name


# ---------------------------------------------------------------- radar de fuite


def academy_table(table: pd.DataFrame) -> pd.DataFrame:
    """Comparatif lisible, trié par ratio de capture croissant."""
    t = table.sort_values("capture_ratio")
    return pd.DataFrame(
        {
            "académie": [f"**{a}**" if a == PSG.name else a for a in t.index],
            "joueurs formés": t.players,
            "départs évalués": t.departures,
            "départs payés": t.paid_departures,
            "indemnités de départ (M€)": t.departure_fees.map(meur),
            "revendus ensuite avec indemnité": t.later_paid,
            "dont ≥ 10 M€": t.later_ge_10m,
            "Σ plus grosses indemnités ultérieures (M€)": t.later_max_sum.map(meur),
            "ratio de capture": t.capture_ratio.round(2),
            "IC 95 % bootstrap": [
                f"[{lo:.2f} ; {hi:.2f}]" for lo, hi in zip(t.ci_low, t.ci_high)
            ],
            "ratio sans les 2 plus gros cas": t.ratio_without_top2.round(2),
            "part ayant joué dans l'élite": t.reached_elite_share.round(3),
            "rachetés ensuite": t.bought_back,
        }
    )


def alumni_table(
    detail: pd.DataFrame, players: pd.DataFrame, clubs: Clubs
) -> pd.DataFrame:
    """Fiche des anciens du PSG (tous les départs, évaluables ou non)."""
    info = players.set_index("id").reindex(detail.index)
    birth_year = pd.to_datetime(info.birth_date, errors="coerce").dt.year
    out = pd.DataFrame(
        {
            "player_id": detail.index,
            "name": info.name.values,
            "position": info.main_position.values,
            "birth_year": birth_year.astype("Int64").values,
            "entry_year": detail.entry_year.values,
            "departure_year": detail.year.values,
            "departure_from": detail.left_club_id.map(clubs.name).values,
            "departure_to": detail.joined_club_id.map(clubs.label).values,
            "departure_fee": detail.transfer_fee.values,
            "later_max_fee": detail.later_max_fee.values,
            "later_buyer": detail.later_buyer.map(clubs.label).values,
            "reached_elite": detail.reached_elite.values,
            "bought_back": detail.bought_back.values,
            "evaluable": detail.evaluable.values,
        }
    )
    return out.sort_values(
        ["later_max_fee", "departure_fee", "player_id"], ascending=[False, False, True]
    ).reset_index(drop=True)


def alumni_view(alumni: pd.DataFrame, n: int) -> pd.DataFrame:
    rows = alumni.head(n)
    return pd.DataFrame(
        {
            "joueur": rows.name,
            "poste": rows.position,
            # années en texte : `md_table` mettrait un séparateur de milliers
            "naissance": rows.birth_year.astype("string").fillna(""),
            "départ": rows.departure_year.astype(str),
            "vers": rows.departure_to,
            "indemnité de départ (M€)": rows.departure_fee.map(meur),
            "plus grosse indemnité ultérieure (M€)": rows.later_max_fee.map(meur),
            "payée par": rows.later_buyer,
            "élite": rows.reached_elite.map({True: "oui", False: "non"}),
        }
    )


def captors(detail: dict[str, pd.DataFrame], names: tuple[str, ...]) -> pd.DataFrame:
    """Premier club d'accueil des départs évaluables, pondéré par la valeur ultérieure."""
    frames = [detail[name].assign(academy=name) for name in names]
    deps = pd.concat(frames)
    deps = deps[deps.evaluable]
    grouped = deps.groupby("joined_club_id").agg(
        players=("later_max_fee", "size"),
        later=("later_max_fee", "sum"),
        academies=("academy", lambda a: ", ".join(sorted(set(a)))),
    )
    return grouped.sort_values(["later", "players"], ascending=False)


def captors_view(table: pd.DataFrame, clubs: Clubs, n: int) -> pd.DataFrame:
    rows = table[table.later > 0].head(n)
    return pd.DataFrame(
        {
            "premier club d'accueil": rows.index.map(clubs.label),
            "joueurs": rows.players,
            "Σ plus grosses indemnités ultérieures (M€)": rows.later.map(meur),
            "académies d'origine": rows.academies,
        }
    )


# ---------------------------------------------------------------- analyses de graphe


def personalized_pagerank(graph: nx.DiGraph, clubs: Clubs, n: int = 15) -> pd.DataFrame:
    """PageRank personnalisé : où se diffusent les flux partant des équipes du PSG."""
    seeds = {club: 1.0 for club in PSG.organisation if club in graph}
    scores = pd.Series(
        nx.pagerank(graph, alpha=0.85, personalization=seeds, weight="weight")
    )
    scores = scores.drop(list(seeds)).sort_values(ascending=False).head(n)
    return pd.DataFrame(
        {"club": scores.index.map(clubs.label), "PageRank personnalisé": scores.values}
    )


def community_exits(
    detail: dict[str, pd.DataFrame], communities: pd.Series
) -> pd.DataFrame:
    """Part des départs (et de la valeur ultérieure) qui quittent la communauté du club."""
    rows = []
    for name in FRENCH_ACADEMIES:
        academy = next(a for a in ACADEMIES if a.name == name)
        home = communities.get(academy.first_team)
        deps = detail[name]
        deps = deps[deps.evaluable]
        dest = deps.joined_club_id.map(communities)
        known = deps[dest.notna()]
        outside = dest[dest.notna()] != home
        total = known.later_max_fee.sum()
        rows.append(
            {
                "académie": name,
                "communauté": f"C{home}",
                "départs vers un club du graphe": len(known),
                "part hors communauté": outside.mean(),
                "part de la valeur ultérieure hors communauté": (
                    known.later_max_fee[outside].sum() / total if total else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def bridge_effect(
    detail: dict[str, pd.DataFrame],
    participation: pd.Series,
    elite: frozenset[tuple[int, int]],
) -> pd.DataFrame:
    """Les jeunes envoyés dans un club passerelle (P ≥ 0,6) atteignent-ils plus l'élite ?

    Départs évaluables des 15 académies vers un club hors élite (les départs directs
    vers l'élite sont exclus), selon la participation du premier club d'accueil.
    """
    deps = pooled_departures(detail)
    deps = deps[deps.evaluable]
    direct = [(c, y) in elite for c, y in zip(deps.joined_club_id, deps.year)]
    deps = deps[~np.array(direct, dtype=bool)]
    p = deps.joined_club_id.map(participation)
    deps = deps[p.notna()].assign(bridge=p[p.notna()] >= BRIDGE_P)
    rows = []
    for bridge, group in deps.groupby("bridge"):
        rows.append(
            {
                "premier club d'accueil": (
                    f"passerelle (P ≥ {BRIDGE_P})" if bridge else f"P < {BRIDGE_P}"
                ),
                "départs": len(group),
                "part atteignant ensuite l'élite": group.reached_elite.mean(),
                "part revendue avec indemnité": (group.later_max_fee > 0).mean(),
                "médiane plus grosse indemnité si revendu (M€)": meur(
                    group.later_max_fee[group.later_max_fee > 0].median()
                ),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- tremplins


def excluded_sources(moves: pd.DataFrame, graph: nx.DiGraph) -> frozenset[int]:
    """Sources exclues : clubs hors graphe principal, jeunes/réserves, réserves connues."""
    eligible = {
        club
        for club, youth in graph.nodes(data="youth_or_reserve")
        if not youth and club not in EXTRA_RESERVE_IDS
    }
    return frozenset(set(moves.left_club_id) - eligible)


def springboard_view(rates: pd.DataFrame, clubs: Clubs, n: int) -> pd.DataFrame:
    rows = rates.head(n)
    return pd.DataFrame(
        {
            "club": rows.index.map(clubs.label),
            "sorties": rows.exits,
            "directes": rows.direct,
            "en 2 sauts": rows.two_hop,
            "taux": rows.rate.round(3),
            "IC 95 % (Wilson)": [
                f"[{lo:.3f} ; {hi:.3f}]" for lo, hi in zip(rows.ci_low, rows.ci_high)
            ],
            "2010–2015": rows.reached_early,
            "2016–2020": rows.reached_late,
        }
    )


def springboard_sensitivity(
    moves: pd.DataFrame,
    raw_club_league: pd.DataFrame,
    excluded: frozenset[int],
    reference: pd.DataFrame,
) -> dict[str, float]:
    """Élite à 30 clubs : corrélation des taux et recouvrement du top 20."""
    elite30 = elite_seasons(raw_club_league, SENSITIVITY_TOP_N)
    rates30 = springboard_rates(springboard_exits(moves, elite30, excluded))
    common = reference.index.intersection(rates30.index)
    rho = reference.rate[common].corr(rates30.rate[common], method="spearman")
    overlap = len(set(reference.index[:20]) & set(rates30.index[:20])) / 20
    return {
        "clubs communs": len(common),
        "Spearman des taux": rho,
        "recouvrement top 20": overlap,
    }


def emerging_view(rates: pd.DataFrame, clubs: Clubs, n: int) -> pd.DataFrame:
    rows = rates.head(n)
    return pd.DataFrame(
        {
            "club": rows.index.map(clubs.label),
            "sorties 2010–2015": rows.exits_early,
            "taux 2010–2015": rows.rate_early.round(3),
            "sorties 2016–2020": rows.exits_late,
            "taux 2016–2020": rows.rate_late.round(3),
            "hausse": (rows.rate_late - rows.rate_early).round(3),
        }
    )


# ---------------------------------------------------------------- concurrents


def competitors(
    transfers: pd.DataFrame, graph: nx.DiGraph, clubs: Clubs
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recrutement étranger dans les équipes de jeunes et réserves françaises.

    Seuls les transferts hors prêt (`Not loan`, `Unknown`) comptent : un prêt n'est
    pas un recrutement.
    """
    country = pd.Series(dict(graph.nodes(data="country")), dtype=object)
    youth = pd.Series(dict(graph.nodes(data="youth_or_reserve")), dtype=bool)
    french_youth = set(youth.index[youth & (country == "France")])
    t = transfers[
        transfers.left_club_id.isin(french_youth) & (transfers.transfer_type != "Loan")
    ]
    dest_country = t.joined_club_id.map(country)
    t = t[dest_country.notna() & (dest_country != "France")].assign(
        country=dest_country
    )
    labels = [f"{a}–{b}" for a, b in COMPETITOR_PERIODS]
    t = t.assign(
        period=np.where(t.year <= COMPETITOR_PERIODS[0][1], labels[0], labels[1])
    )

    def pivot(key: str) -> pd.DataFrame:
        table = t.groupby([key, "period"]).size().unstack(fill_value=0)
        table = table.reindex(columns=labels, fill_value=0)
        table["total"] = table.sum(axis=1)
        return table.sort_values(["total", labels[1]], ascending=False)

    by_country = pivot("country").head(10)
    by_club = pivot("joined_club_id").head(15)
    by_club.index = by_club.index.map(clubs.label)
    return (
        by_country.reset_index().rename(columns={"country": "pays"}),
        by_club.reset_index().rename(columns={"joined_club_id": "club"}),
    )


# ---------------------------------------------------------------- comparables


def comparables(detail: dict[str, pd.DataFrame], players: pd.DataFrame) -> pd.DataFrame:
    """Valeur ultérieure par poste × âge au départ (15 académies, départs évaluables)."""
    deps = pooled_departures(detail)
    deps = deps[deps.evaluable]
    info = players.set_index("id").reindex(deps.index)
    age = deps.year - pd.to_datetime(info.birth_date, errors="coerce").dt.year.values
    position = info.main_position.str.split(" - ").str[0].map(POSITIONS)
    band = pd.Series(pd.NA, index=deps.index, dtype=object)
    for low, high, label in AGE_BANDS:
        band[age.between(low, high)] = label
    frame = deps.assign(position=position.values, band=band.values)
    frame = frame.dropna(subset=["position", "band"])
    rows = []
    for (pos, label), group in frame.groupby(["position", "band"], sort=False):
        fees = group.later_max_fee
        paid = fees[fees > 0]  # la plupart des départs ne sont jamais revendus
        if len(paid) < MIN_PAID:  # quantiles instables : laissés vides
            paid = pd.Series(dtype=float)
        rows.append(
            {
                "poste": pos,
                "âge au départ": label,
                "départs": len(group),
                "part revendue avec indemnité": (fees > 0).mean(),
                "valeur moyenne (M€)": fees.mean() / 1e6,
                "médiane si revendu (M€)": paid.median() / 1e6,
                "Q75 si revendu (M€)": paid.quantile(0.75) / 1e6,
                "Q90 si revendu (M€)": paid.quantile(0.9) / 1e6,
                "part ayant joué dans l'élite": group.reached_elite.mean(),
            }
        )
    order_pos = {v: i for i, v in enumerate(POSITIONS.values())}
    order_age = {label: i for i, (_, _, label) in enumerate(AGE_BANDS)}
    out = pd.DataFrame(rows)
    out = out.sort_values(
        ["poste", "âge au départ"],
        key=lambda s: s.map(order_pos if s.name == "poste" else order_age),
    )
    return out[out["départs"] >= MIN_CELL].reset_index(drop=True)


# ---------------------------------------------------------------- figures


def plot_capture(table: pd.DataFrame) -> None:
    """Ratio de capture par académie avec intervalle bootstrap ; PSG mis en avant."""
    setup_style()
    t = table.sort_values("capture_ratio", ascending=False)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    y = np.arange(len(t))
    for i, (name, row) in enumerate(t.iterrows()):
        color = SERIES[1] if name == PSG.name else NEUTRAL
        ax.plot([row.ci_low, row.ci_high], [i, i], color=color, linewidth=2)
        ax.plot(row.capture_ratio, i, "o", color=color, markersize=7)
    ax.axvline(1, color=TEXT_SECONDARY, linewidth=1, linestyle="--")
    ax.text(
        1.03,
        len(t) - 0.6,
        "indemnités de départ\n= valeur ultérieure",
        fontsize=7,
        color=TEXT_SECONDARY,
        va="top",
    )
    ax.set_yticks(y, t.index)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(
        "ratio de capture = Σ indemnités de départ / Σ plus grosses indemnités "
        "ultérieures (IC 95 % bootstrap)"
    )
    ax.set_title(
        f"Valeur captée par les académies (joueurs entrés {ENTRY_YEARS[0]}–"
        f"{ENTRY_YEARS[1]}, partis ≤ {LAST_EVALUATED_DEPARTURE})"
    )
    save_figure(fig, "academy_value_capture")


def plot_springboards(rates: pd.DataFrame, clubs: Clubs, n: int = 20) -> None:
    """Top des tremplins : taux et intervalle de Wilson ; clubs français en couleur."""
    setup_style()
    t = rates.head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    french = False
    for i, (club, row) in enumerate(t.iterrows()):
        is_fr = clubs.country.get(club) == "France"
        french |= is_fr
        color = SERIES[0] if is_fr else NEUTRAL
        ax.plot([row.ci_low, row.ci_high], [i, i], color=color, linewidth=2)
        ax.plot(row.rate, i, "o", color=color, markersize=7)
    ax.set_yticks(np.arange(len(t)), [clubs.name(c) for c in t.index])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(
        f"part des sorties qui atteignent l'élite (top {ELITE_TOP_N}) en ≤ 2 sauts "
        f"et ≤ {HORIZON} ans (IC 95 % Wilson)"
    )
    ax.set_title(
        f"Clubs tremplins vers l'élite (sorties {EXIT_YEARS[0]}–{EXIT_YEARS[1]})"
    )
    handles = [
        plt.Line2D([], [], marker="o", color=SERIES[0], label="club français"),
        plt.Line2D([], [], marker="o", color=NEUTRAL, label="autre club"),
    ]
    if french:
        ax.legend(handles=handles, loc="lower right", fontsize=7)
    save_figure(fig, "springboards")


# ---------------------------------------------------------------- rapport


def main() -> None:
    raw = load_raw(players_columns=["id", "name", "birth_date", "main_position"])
    graph = main_graph()
    clubs = Clubs(raw.clubs, graph)
    moves = prepare_moves(raw.transfers)
    elite = elite_seasons(raw.club_league)

    # 1. Radar de fuite
    table, detail = academy_summary(moves, elite)
    save_table(table.reset_index(), "talent_flow_academies")
    alumni = alumni_table(detail[PSG.name], raw.players, clubs)
    save_table(alumni, "talent_flow_psg_alumni")
    evaluable = alumni[alumni.evaluable]
    recent = alumni[~alumni.evaluable].sort_values(
        ["departure_fee", "departure_year", "player_id"], ascending=[False, False, True]
    )
    psg = table.loc[PSG.name]
    plot_capture(table)

    # 2. Analyses de graphe
    communities = pd.read_csv(TABLES_DIR / "communities.csv").set_index("club_id")
    participation = pd.read_csv(TABLES_DIR / "roles.csv").set_index("club_id").P
    ppr = personalized_pagerank(graph, clubs)
    comm = community_exits(detail, communities.community)
    bridges = bridge_effect(detail, participation, elite)

    # 3. Tremplins
    excluded = excluded_sources(moves, graph)
    exits = springboard_exits(moves, elite, excluded)
    rates = springboard_rates(exits)
    rates_out = rates.assign(
        name=rates.index.map(clubs.name), country=rates.index.map(clubs.country.get)
    )
    save_table(rates_out.reset_index(), "talent_flow_springboards")
    french = rates[rates.index.map(clubs.country.get) == "France"]
    emerging = rates[
        (rates.exits_early >= MIN_PERIOD_EXITS) & (rates.exits_late >= MIN_PERIOD_EXITS)
    ]
    emerging = emerging.assign(delta=emerging.rate_late - emerging.rate_early)
    emerging = emerging.sort_values(["delta", "ci_low"], ascending=False)
    direct = exits[exits.direct]
    top_median = rates.rate[rates.reached > 0].median()  # référence pour le top 20
    sensitivity = springboard_sensitivity(moves, raw.club_league, excluded, rates)
    plot_springboards(rates, clubs)

    # 4. Concurrents
    transfers, _ = filter_transfers(raw, GraphConfig())
    comp_country, comp_club = competitors(transfers, graph, clubs)

    # 5. Comparables
    comps = comparables(detail, raw.players)
    save_table(comps, "talent_flow_comparables")

    lines = [
        "# Paris Talent Flow : où partent les joueurs formés au PSG ?",
        "",
        (
            "Généré par `uv run python -m ftna.talent_flow`. Produit d'aide à la décision "
            "pour le directeur sportif du PSG, construit sur le réseau observé dans ce "
            "dataset (Transfermarkt), pas sur le marché mondial complet."
        ),
        "",
        "## Méthode et conventions",
        "",
        (
            "- Carrières reconstituées à partir de `transfers.csv` **brut** (l'entrée au "
            "centre passe par des clubs absents de `clubs.csv`), sans « End of loan », dans "
            "l'ordre du fichier pour départager une même année."
        ),
        (
            f"- Joueur formé : première arrivée dans une équipe de jeunes ou réserve de "
            f"l'académie entre {ENTRY_YEARS[0]} et {ENTRY_YEARS[1]} (équipes associées "
            "manuellement, 15 académies)."
        ),
        (
            "- Départ : premier mouvement hors prêt de l'organisation (équipe première + "
            "jeunes) vers un autre club ou un pseudo-club (joueur libéré). Évalué si "
            f"l'année est ≤ {LAST_EVALUATED_DEPARTURE} (recul d'au moins deux saisons)."
        ),
        (
            "- Valeur ultérieure : plus grosse indemnité de transfert hors prêt payée pour "
            "le joueur après son départ, hors mouvements impliquant l'académie, jusqu'à "
            "l'année d'un éventuel retour dans l'académie (un rachat ouvre un nouveau "
            "départ). L'ordre des lignes dans une même année n'étant pas chronologique, "
            "les calculs raisonnent à l'année. Sans limite de durée : les cohortes "
            "récentes ont eu moins de temps pour être revendues."
        ),
        (
            "- **Ratio de capture** = Σ indemnités de départ / Σ plus grosses indemnités "
            "ultérieures ; intervalle à 95 % par bootstrap sur les joueurs (1 000 tirages, "
            "graine 42). Un ratio < 1 signifie que la valeur s'est surtout réalisée "
            "ailleurs."
        ),
        (
            f"- Élite : {ELITE_TOP_N} premiers clubs de la saison par valeur d'effectif "
            "(`club_league`) ; sensibilité à "
            f"{SENSITIVITY_TOP_N}. « A joué dans l'élite » : départ ou mouvement (prêt "
            f"compris) vers un club d'élite au plus {ELITE_HORIZON} ans après le départ, "
            "même recul pour toutes les cohortes."
        ),
        (
            "- Montant 0 = transfert gratuit **ou** non divulgué ; les clauses de revente "
            "et de rachat ne sont pas visibles. On parle donc de « valeur réalisée "
            "ailleurs », sans prétendre mesurer un manque à gagner exact."
        ),
        "",
        "## 1. Comparatif des académies",
        "",
        md_table(academy_table(table), floatfmt=".3g"),
        "",
        (
            f"PSG : {int(psg.players)} joueurs formés, {int(psg.departures)} départs évalués, dont "
            f"{1 - psg.paid_departures / psg.departures:.0%} sans indemnité connue. Le "
            f"club a touché {meur(psg.departure_fees)} M€ au départ ; la somme des plus "
            f"grosses indemnités payées ensuite atteint {meur(psg.later_max_sum)} M€, soit "
            f"un ratio de capture de **{psg.capture_ratio:.2f}** "
            f"(IC 95 % [{psg.ci_low:.2f} ; {psg.ci_high:.2f}] ; "
            f"{psg.ratio_without_top2:.2f} sans les deux plus gros cas)."
        ),
        "",
        (
            "Lecture : les écarts entre académies sont larges et les intervalles se "
            "recouvrent souvent (petits effectifs, quelques joueurs dominent la valeur). "
            "La colonne « rachetés ensuite » rend visible un levier absent du ratio : le "
            "rachat (cas Real Madrid, Juventus, Barcelone)."
        ),
        "",
        "Figure : `results/figures/academy_value_capture.pdf`.",
        "",
        "## 2. Anciens du PSG",
        "",
        "### Plus grosses valeurs réalisées après le départ (départs évalués)",
        "",
        md_table(alumni_view(evaluable, 15)),
        "",
        f"### Départs après {LAST_EVALUATED_DEPARTURE} (non encore évaluables)",
        "",
        f"{len(recent)} départs ; les 10 plus grosses indemnités de départ :",
        "",
        md_table(
            alumni_view(recent, 10).drop(
                columns=["plus grosse indemnité ultérieure (M€)", "payée par", "élite"]
            )
        ),
        "",
        "Fiche complète : `results/tables/talent_flow_psg_alumni.csv`.",
        "",
        "### Clubs captants (premier club d'accueil, pondéré par la valeur ultérieure)",
        "",
        "Anciens du PSG :",
        "",
        md_table(captors_view(captors(detail, (PSG.name,)), clubs, 10)),
        "",
        f"Six académies françaises ({', '.join(FRENCH_ACADEMIES)}) :",
        "",
        md_table(captors_view(captors(detail, FRENCH_ACADEMIES), clubs, 15)),
        "",
        "## 3. Analyses de graphe",
        "",
        "### PageRank personnalisé depuis les équipes du PSG",
        "",
        (
            "Marche aléatoire sur le graphe principal (2010–2023, poids = nombre de "
            "transferts, α = 0,85) qui repart toujours des équipes du PSG (583, 6326, "
            "8512) : les clubs où se diffusent les flux de joueurs issus du PSG."
        ),
        "",
        md_table(ppr, floatfmt=".4f"),
        "",
        "### Sortie de la communauté Louvain (A5)",
        "",
        md_table(comm, floatfmt=".2f"),
        "",
        "### Clubs passerelles (participation P, A10)",
        "",
        (
            "Départs évalués des 15 académies (un joueur passé par deux centres compte "
            "une fois) vers un club hors élite, selon le coefficient de participation du "
            "premier club d'accueil."
        ),
        "",
        md_table(bridges, floatfmt=".3f"),
        "",
        (
            "Association, pas causalité : les meilleurs jeunes sont peut-être envoyés "
            "en priorité vers ces clubs (biais de sélection)."
        ),
        "",
        "## 4. Clubs tremplins vers l'élite",
        "",
        (
            f"Sorties définitives (`Not loan` ou `Unknown`) de {EXIT_YEARS[0]} à "
            f"{EXIT_YEARS[1]} depuis un club du graphe principal hors élite cette "
            "saison-là, hors équipes de jeunes et réserves (heuristique + Barça Atlètic, "
            "Valencia Mestalla, Juventus Next Gen, Sevilla Atlético) ; joueurs arrivés en "
            "prêt depuis un club d'élite exclus. Atteinte de l'élite directe ou au "
            f"mouvement suivant (hors prêt) dans les {HORIZON} ans. Clubs avec au moins "
            f"{MIN_EXITS} sorties, triés par borne basse de Wilson."
        ),
        "",
        (
            f"- {len(exits):,} sorties ; {int(exits.reached.sum()):,} atteignent l'élite "
            f"({exits.reached.mean():.2%}, une moyenne tirée vers le bas par les clubs "
            f"amateurs) ; {len(rates):,} clubs affichables, dont "
            f"{(rates.reached > 0).mean():.0%} ont envoyé au moins un joueur dans "
            f"l'élite. Parmi ces derniers, taux médian {top_median:.1%}."
        ),
        (
            f"- {(direct.transfer_fee > 0).mean():.0%} des passages directs vers l'élite "
            "ont une indemnité connue."
        ),
        "",
        "### Top 20",
        "",
        md_table(springboard_view(rates, clubs, 20)),
        "",
        "### Tremplins français",
        "",
        md_table(springboard_view(french, clubs, 10)),
        "",
        "### Tremplins émergents (2016–2020 contre 2010–2015)",
        "",
        (
            f"Clubs avec au moins {MIN_PERIOD_EXITS} sorties dans chaque période, "
            "classés par hausse du taux d'atteinte de l'élite (et non du nombre brut)."
        ),
        "",
        md_table(emerging_view(emerging, clubs, 10)),
        "",
        "### Sensibilité : élite à 30 clubs",
        "",
        md_table(pd.DataFrame([sensitivity]), floatfmt=".3f"),
        "",
        "Le ratio de capture (section 1) ne dépend pas de la définition de l'élite.",
        "",
        "Figure : `results/figures/springboards.pdf`.",
        "",
        "## 5. Concurrents : recrutement étranger dans les équipes de jeunes françaises",
        "",
        (
            "Transferts hors prêt retenus dans le graphe principal depuis une équipe de "
            "jeunes ou réserve française vers un club étranger."
        ),
        "",
        md_table(comp_country),
        "",
        md_table(comp_club),
        "",
        "## 6. Comparables pour les clauses",
        "",
        (
            "Départs évalués des 15 académies (un joueur passé par deux centres compte une "
            "fois), par poste et âge au départ (année de départ "
            "− année de naissance). Valeur = plus grosse indemnité ultérieure : moyenne "
            "sur tous les départs (0 compris, espérance utile pour un pourcentage de "
            "revente), quantiles parmi les joueurs revendus avec indemnité. "
            f"Cellules de moins de {MIN_CELL} départs masquées ; quantiles vides si moins de "
            f"{MIN_PAID} joueurs revendus."
        ),
        "",
        md_table(comps, floatfmt=".2f"),
        "",
        "## Limites",
        "",
        (
            "- Aucune donnée de performance (minutes, statistiques) : le succès est mesuré "
            "par les indemnités et l'accès à l'élite."
        ),
        (
            "- Montant 0 ambigu (gratuit ou non divulgué) ; clauses de revente et de rachat "
            "invisibles."
        ),
        (
            f"- Seules les cohortes parties jusqu'en {LAST_EVALUATED_DEPARTURE} sont "
            "évaluables ; 2024 est incomplet."
        ),
        (
            "- Petits effectifs : une douzaine de joueurs concentre l'essentiel de la "
            "valeur d'une académie (voir le ratio sans les deux plus gros cas)."
        ),
        (
            "- Association manuelle des équipes de jeunes à leur club ; heuristique "
            "jeunes/réserves imparfaite."
        ),
        "- Pas de lieu de naissance : impossible de localiser les viviers régionaux.",
    ]
    write_report("talent_flow", lines)


if __name__ == "__main__":
    main()
