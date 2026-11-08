"""Construction du réseau orienté et pondéré des transferts entre clubs.

Usage : `uv run python -m ftna.graph`
- graphe : `data/processed/transfer_network.graphml` (non versionné) ;
- résumé : `results/graph_summary.md`.
"""

from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import pandas as pd

from ftna.data import (
    PROJECT_ROOT,
    PSEUDO_CLUB_IDS,
    YOUTH_LEAGUE_PATTERN,
    YOUTH_RESERVE_PATTERN,
    RawData,
    load_raw,
)

GRAPH_PATH = PROJECT_ROOT / "data" / "processed" / "transfer_network.graphml"
SUMMARY_PATH = PROJECT_ROOT / "results" / "graph_summary.md"

# Correspondance entre `transfer_type` et le suffixe des attributs d'arête.
TYPE_ATTRIBUTES = {"Not loan": "n_permanent", "Loan": "n_loan", "Unknown": "n_unknown"}


@dataclass(frozen=True)
class GraphConfig:
    """Règles de filtrage validées (voir docs/PROJECT_LOG.md, 2026-11-08)."""

    start_year: int = 2010
    end_year: int = 2023
    excluded_types: tuple[str, ...] = ("End of loan",)


@dataclass(frozen=True)
class FilterStep:
    """Une étape du filtrage et le nombre de lignes restantes."""

    label: str
    rows: int


def filter_transfers(
    raw: RawData, config: GraphConfig
) -> tuple[pd.DataFrame, list[FilterStep]]:
    """Applique les filtres dans l'ordre et trace l'effectif après chaque étape."""
    t = raw.transfers
    described = set(raw.clubs.id) - PSEUDO_CLUB_IDS
    steps = [FilterStep("Lignes brutes", len(t))]

    t = t[t.year.between(config.start_year, config.end_year)]
    steps.append(FilterStep(f"Années {config.start_year}–{config.end_year}", len(t)))

    t = t[~t.transfer_type.isin(config.excluded_types)]
    steps.append(
        FilterStep(f"Types exclus : {', '.join(config.excluded_types)}", len(t))
    )

    pseudo = t.left_club_id.isin(PSEUDO_CLUB_IDS) | t.joined_club_id.isin(
        PSEUDO_CLUB_IDS
    )
    t = t[~pseudo]
    steps.append(FilterStep("Sans pseudo-clubs (-5, 75, 515)", len(t)))

    t = t[t.left_club_id.isin(described) & t.joined_club_id.isin(described)]
    steps.append(FilterStep("Deux clubs décrits dans clubs.csv", len(t)))

    t = t[t.left_club_id != t.joined_club_id]
    steps.append(FilterStep("Sans boucles", len(t)))
    return t, steps


def club_attributes(raw: RawData, end_year: int) -> pd.DataFrame:
    """Attributs de nœud : nom, pays, dernière ligue connue, valeur marchande actuelle
    et indicateur `youth_or_reserve` (heuristique sur le nom du club ou de sa ligue).

    Le pays vient de la ligue de la saison la plus récente (≤ `end_year`) dans
    `club_league`, ce qui évite la multiplication de lignes d'une jointure sur
    (club, saison) ; à défaut, de la ligue actuelle (`id_current_league`).
    """
    leagues = raw.leagues.set_index("id")
    history = raw.club_league[raw.club_league.season <= end_year]
    # Une seule ligne par club : saison la plus récente, puis valeur marchande la
    # plus élevée et code de ligue pour départager de façon déterministe.
    latest = (
        history.sort_values(
            ["club_id", "season", "market_value", "league_id"],
            ascending=[True, False, False, True],
        )
        .drop_duplicates("club_id")
        .set_index("club_id")
        .league_id
    )
    clubs = raw.clubs.set_index("id")
    league_id = latest.reindex(clubs.index).fillna(clubs.id_current_league)
    league = league_id.map(leagues.league_name).fillna("")
    youth = clubs.club_name.str.contains(YOUTH_RESERVE_PATTERN) | league.str.contains(
        YOUTH_LEAGUE_PATTERN
    )
    return pd.DataFrame(
        {
            "name": clubs.club_name,
            "league_id": league_id.fillna(""),
            "league": league,
            "country": league_id.map(leagues.country).fillna(""),
            "current_mv": clubs.current_mv,
            "youth_or_reserve": youth,
        }
    )


def build_graph(transfers: pd.DataFrame, attributes: pd.DataFrame) -> nx.DiGraph:
    """Agrège les transferts par couple (départ, arrivée) en arêtes pondérées."""
    counts = pd.crosstab(
        [transfers.left_club_id, transfers.joined_club_id], transfers.transfer_type
    ).rename(columns=TYPE_ATTRIBUTES)
    for column in TYPE_ATTRIBUTES.values():
        if column not in counts:
            counts[column] = 0
    edges = counts.assign(
        weight=counts.sum(axis=1),
        total_fee=transfers.groupby(
            ["left_club_id", "joined_club_id"]
        ).transfer_fee.sum(),
    ).reset_index()

    graph = nx.DiGraph()
    nodes = pd.unique(edges[["left_club_id", "joined_club_id"]].to_numpy().ravel())
    # `to_dict` convertit en types Python natifs, sérialisables en GraphML.
    node_attributes = attributes.loc[nodes].to_dict("index")
    graph.add_nodes_from((int(i), attrs) for i, attrs in node_attributes.items())
    for row in edges.itertuples(index=False):
        graph.add_edge(
            int(row.left_club_id),
            int(row.joined_club_id),
            weight=int(row.weight),
            total_fee=int(row.total_fee),
            n_permanent=int(row.n_permanent),
            n_loan=int(row.n_loan),
            n_unknown=int(row.n_unknown),
        )
    return graph


def summarize(graph: nx.DiGraph, steps: list[FilterStep], config: GraphConfig) -> str:
    """Résumé Markdown : filtrage, taille, poids et répartition par pays."""
    weights = pd.Series([w for _, _, w in graph.edges(data="weight")])
    countries = pd.Series(dict(graph.nodes(data="country"))).replace("", "(inconnu)")
    reciprocal = sum(1 for u, v in graph.edges if graph.has_edge(v, u))
    youth = pd.Series(dict(graph.nodes(data="youth_or_reserve")))
    youth_weight = sum(
        w
        for u, v, w in graph.edges(data="weight")
        if graph.nodes[u]["youth_or_reserve"] or graph.nodes[v]["youth_or_reserve"]
    )
    lines = [
        "# Réseau des transferts : construction",
        "",
        "Généré par `uv run python -m ftna.graph` à partir de `data/raw/`.",
        "",
        "## Filtrage",
        "",
        "| Étape | Lignes restantes |",
        "|---|---:|",
        *(f"| {s.label} | {s.rows:,} |" for s in steps),
        "",
        "## Graphe",
        "",
        (
            "- Type : orienté, simple (une arête par couple ordonné de clubs), pondéré "
            "(`weight` = nombre de transferts), sans boucle."
        ),
        f"- Nœuds (clubs) : {graph.number_of_nodes():,}",
        f"- Arêtes (couples orientés distincts) : {graph.number_of_edges():,}",
        f"- Somme des poids (= transferts retenus) : {int(weights.sum()):,}",
        f"- Densité : {nx.density(graph):.2e}",
        (
            f"- Part des arêtes réciproques (u→v et v→u) : "
            f"{reciprocal / graph.number_of_edges():.1%}"
        ),
        (
            f"- Poids : médiane {weights.median():.0f}, moyenne {weights.mean():.2f}, "
            f"max {weights.max():,} ; arêtes de poids 1 : {(weights == 1).mean():.1%}"
        ),
        f"- Clubs sans pays identifié : {(countries == '(inconnu)').sum():,}",
        f"- Pays représentés : {countries[countries != '(inconnu)'].nunique():,}",
        (
            f"- Équipes de jeunes/réserves (heuristique, attribut `youth_or_reserve`) : "
            f"{youth.sum():,} nœuds, {youth_weight / weights.sum():.1%} du poids total "
            "(arêtes touchant au moins une de ces équipes)"
        ),
        "",
        "## Arêtes les plus lourdes",
        "",
        "| Départ | Arrivée | Transferts | dont prêts |",
        "|---|---|---:|---:|",
    ]
    heaviest = sorted(
        graph.edges(data=True), key=lambda e: e[2]["weight"], reverse=True
    )
    names = dict(graph.nodes(data="name"))
    lines += [
        f"| {names[u]} | {names[v]} | {d['weight']} | {d['n_loan']} |"
        for u, v, d in heaviest[:10]
    ]
    lines += [
        "",
        "## Clubs par pays (15 premiers)",
        "",
        "| Pays | Clubs |",
        "|---|---:|",
    ]
    lines += [f"| {c} | {n:,} |" for c, n in countries.value_counts().head(15).items()]
    lines += ["", f"Paramètres : {config}."]
    return "\n".join(lines) + "\n"


def load_graph(path: Path = GRAPH_PATH) -> nx.DiGraph:
    """Relit le graphe sauvegardé (identifiants de clubs en entiers)."""
    return nx.read_graphml(path, node_type=int)


def main() -> None:
    config = GraphConfig()
    raw = load_raw(players_columns=["id"])
    transfers, steps = filter_transfers(raw, config)
    graph = build_graph(transfers, club_attributes(raw, config.end_year))

    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, GRAPH_PATH)
    summary = summarize(graph, steps, config)
    SUMMARY_PATH.write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
