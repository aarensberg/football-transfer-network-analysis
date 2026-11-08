"""A4. Centralités des clubs.

Mesures (graphe orienté vendeur → acheteur) :
- degrés et forces entrants/sortants ;
- PageRank pondéré (destinations recevant des joueurs de clubs eux-mêmes centraux) ;
- PageRank inverse, sur le graphe transposé (fournisseurs de clubs centraux) ;
- closeness entrante/sortante exacte sur la CFC géante ;
- betweenness exacte (non pondérée), parallélisée par paquets de sources.

Usage : `uv run python -m ftna.centrality` (`--plot-only` : figure seule)
Sorties : `results/centrality.md`, `results/tables/centrality.csv`,
`results/figures/pagerank_map.{pdf,png}`.
"""

import os
import sys
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from ftna.common import (
    NEUTRAL,
    SEED,
    SERIES,
    TABLES_DIR,
    TEXT_PRIMARY,
    main_graph,
    md_table,
    save_figure,
    save_table,
    setup_style,
    write_report,
)
from ftna.distances import all_distances

PAGERANK_ALPHA = 0.85
TOP = 20

_WORKER_GRAPH: nx.DiGraph | None = None


def _init_worker(edges: list[tuple[int, int]], nodes: list[int]) -> None:
    global _WORKER_GRAPH
    _WORKER_GRAPH = nx.DiGraph()
    _WORKER_GRAPH.add_nodes_from(nodes)
    _WORKER_GRAPH.add_edges_from(edges)


def _partial_betweenness(sources: list[int]) -> dict[int, float]:
    assert _WORKER_GRAPH is not None
    return nx.betweenness_centrality_subset(
        _WORKER_GRAPH, sources, list(_WORKER_GRAPH), normalized=False
    )


def exact_betweenness(graph: nx.DiGraph, processes: int | None = None) -> pd.Series:
    """Betweenness exacte non pondérée, normalisée par (n - 1)(n - 2) comme NetworkX.

    Les contributions de paquets disjoints de sources s'additionnent (vérifié contre
    `nx.betweenness_centrality` sur un graphe test : écart < 1e-12).
    """
    nodes = list(graph)
    processes = processes or os.cpu_count() or 1
    chunks = [nodes[i :: processes * 4] for i in range(processes * 4)]
    total = pd.Series(0.0, index=nodes)
    with ProcessPoolExecutor(
        processes, initializer=_init_worker, initargs=(list(graph.edges()), nodes)
    ) as pool:
        for partial in pool.map(_partial_betweenness, chunks):
            total = total.add(pd.Series(partial), fill_value=0.0)
    n = len(nodes)
    return total / ((n - 1) * (n - 2))


def compute_centralities(
    graph: nx.DiGraph, exact: bool = True, k: int = 1000
) -> pd.DataFrame:
    """Table des centralités par club ; `exact=False` échantillonne `k` sources pour la
    betweenness (analyses de sensibilité)."""
    core = graph.subgraph(max(nx.strongly_connected_components(graph), key=len))
    distances = all_distances(core, directed=True)
    if exact:
        betweenness = exact_betweenness(graph)
    else:
        betweenness = pd.Series(nx.betweenness_centrality(graph, k=k, seed=SEED))
    table = pd.DataFrame(
        {
            "name": dict(graph.nodes(data="name")),
            "country": dict(graph.nodes(data="country")),
            "league": dict(graph.nodes(data="league")),
            "youth_or_reserve": dict(graph.nodes(data="youth_or_reserve")),
            "current_mv": dict(graph.nodes(data="current_mv")),
            "in_degree": dict(graph.in_degree()),
            "out_degree": dict(graph.out_degree()),
            "in_strength": dict(graph.in_degree(weight="weight")),
            "out_strength": dict(graph.out_degree(weight="weight")),
            "pagerank": nx.pagerank(graph, alpha=PAGERANK_ALPHA, weight="weight"),
            "reverse_pagerank": nx.pagerank(
                graph.reverse(copy=False), alpha=PAGERANK_ALPHA, weight="weight"
            ),
            "in_closeness": pd.Series(distances.closeness("in"), index=distances.nodes),
            "out_closeness": pd.Series(
                distances.closeness("out"), index=distances.nodes
            ),
            "betweenness": betweenness,
        }
    )
    fees = pd.DataFrame(
        [(u, v, f) for u, v, f in graph.edges(data="total_fee")],
        columns=["u", "v", "fee"],
    )
    table["fees_received"] = (
        fees.groupby("u").fee.sum().reindex(table.index, fill_value=0)
    )
    table["fees_paid"] = fees.groupby("v").fee.sum().reindex(table.index, fill_value=0)
    table.index.name = "club_id"
    return table


MEASURES = [
    "in_degree",
    "out_degree",
    "in_strength",
    "out_strength",
    "pagerank",
    "reverse_pagerank",
    "in_closeness",
    "out_closeness",
    "betweenness",
]


def top_table(table: pd.DataFrame, measure: str, n: int = TOP) -> pd.DataFrame:
    top = table.nlargest(n, measure)
    return pd.DataFrame(
        {
            "rang": range(1, len(top) + 1),
            "club": top.name,
            "pays": top.country,
            measure: top[measure],
            "jeunes/réserve": top.youth_or_reserve.map({True: "oui", False: ""}),
        }
    )


def annotate_without_overlap(ax: plt.Axes, rows: pd.DataFrame) -> None:
    """Étiquette des points en décalant verticalement les textes trop proches."""
    fig = ax.figure
    fig.canvas.draw()
    to_points = 72 / fig.dpi
    width = fig.get_size_inches()[0] * fig.dpi
    placed: list[tuple[float, float]] = []
    points = [
        (row["name"], *ax.transData.transform((row.reverse_pagerank, row.pagerank)))
        for _, row in rows.iterrows()
    ]
    for name, x, y in sorted(points, key=lambda p: -p[2]):
        left = x > 0.7 * width  # texte à gauche du point près du bord droit
        y_text = y
        while any(abs(x - px) < 150 and abs(y_text - py) < 11 for px, py in placed):
            y_text -= 11
        placed.append((x, y_text))
        ax.annotate(
            name,
            ax.transData.inverted().transform((x, y)),
            xytext=(-4 if left else 4, (y_text - y) * to_points),
            textcoords="offset points",
            ha="right" if left else "left",
            va="center",
            fontsize=6.5,
            color=TEXT_PRIMARY,
            arrowprops={"arrowstyle": "-", "color": NEUTRAL, "linewidth": 0.5}
            if y_text != y
            else None,
        )


def plot_pagerank_map(table: pd.DataFrame) -> None:
    """Carte destinations (PageRank) × fournisseurs (PageRank inverse), log-log."""
    setup_style()
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    youth = table.youth_or_reserve
    ax.scatter(
        table.reverse_pagerank[~youth],
        table.pagerank[~youth],
        s=4,
        alpha=0.35,
        color=SERIES[0],
        linewidths=0,
        label="clubs",
    )
    ax.scatter(
        table.reverse_pagerank[youth],
        table.pagerank[youth],
        s=4,
        alpha=0.35,
        color=SERIES[1],
        linewidths=0,
        label="jeunes / réserves",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    lims = [
        min(ax.get_xlim()[0], ax.get_ylim()[0]),
        max(ax.get_xlim()[1], ax.get_ylim()[1]),
    ]
    ax.plot(lims, lims, color=NEUTRAL, linewidth=1, linestyle="--")
    # Étiquettes : 3 premières destinations, 3 premiers fournisseurs et les 5 clubs
    # les plus valorisés (pour situer l'élite dans la carte).
    labelled = pd.concat(
        [
            table.nlargest(3, "pagerank"),
            table.nlargest(3, "reverse_pagerank"),
            table.nlargest(5, "current_mv"),
        ]
    ).drop_duplicates(subset="name")
    annotate_without_overlap(ax, labelled)
    ax.set_xlabel("PageRank inverse (fournisseur de joueurs)")
    ax.set_ylabel("PageRank (destination de joueurs)")
    ax.set_title("Destinations et fournisseurs du réseau des transferts")
    ax.legend(loc="upper left", markerscale=3)
    save_figure(fig, "pagerank_map")


def country_concentration(table: pd.DataFrame, measure: str, n: int = 100) -> str:
    counts = table.nlargest(n, measure).country.replace("", "?").value_counts().head(6)
    return ", ".join(f"{c} {k}" for c, k in counts.items())


def main() -> None:
    if "--plot-only" in sys.argv:  # régénère la figure depuis la table sauvegardée
        plot_pagerank_map(pd.read_csv(TABLES_DIR / "centrality.csv"))
        return
    graph = main_graph()
    table = compute_centralities(graph, exact=True)
    save_table(table.reset_index(), "centrality")
    plot_pagerank_map(table)

    # Contrôle de l'approximation utilisée dans les analyses de sensibilité.
    approx = pd.Series(nx.betweenness_centrality(graph, k=1000, seed=SEED))
    approx_rho = table.betweenness.corr(approx, method="spearman")
    top100 = set(table.betweenness.nlargest(100).index)
    approx_overlap = len(top100 & set(approx.nlargest(100).index)) / 100

    corr = table[MEASURES].corr(method="spearman")
    corr.insert(0, "mesure", corr.index)
    valued = table[table.current_mv > 0]
    mv_corr = pd.DataFrame(
        {
            "mesure": MEASURES,
            "Spearman avec current_mv": [
                valued[m].corr(valued.current_mv, method="spearman") for m in MEASURES
            ],
            "Spearman avec montants payés": [
                table[m].corr(table.fees_paid, method="spearman") for m in MEASURES
            ],
        }
    )
    outlier = table.nlargest(3, "out_strength")[
        ["name", "country", "out_strength", "out_degree"]
    ]

    lines = [
        "# A4. Centralités",
        "",
        "Généré par `uv run python -m ftna.centrality`. Table complète : `results/tables/centrality.csv`.",
        "",
        (
            f"- PageRank : α = {PAGERANK_ALPHA}, pondéré par le nombre de transferts ; PageRank inverse "
            "calculé sur le graphe transposé."
        ),
        "- Closeness : exacte, sur la CFC géante (distances en sauts).",
        "- Betweenness : exacte, non pondérée, normalisée par (n − 1)(n − 2).",
        (
            f"- Contrôle de l'approximation (k = 1000 sources, graine {SEED}) : Spearman = {approx_rho:.3f} "
            f"avec la valeur exacte ; recouvrement du top 100 = {approx_overlap:.0%}."
        ),
        "",
        "## Valeurs extrêmes de force sortante",
        "",
        md_table(outlier.reset_index(drop=True)),
        "",
    ]
    for measure in (
        "pagerank",
        "reverse_pagerank",
        "betweenness",
        "in_closeness",
        "out_closeness",
        "in_strength",
        "out_strength",
        "in_degree",
        "out_degree",
    ):
        lines += [
            f"## Top {TOP} : {measure}",
            "",
            md_table(top_table(table, measure), floatfmt=".4g"),
            "",
            f"Pays du top 100 : {country_concentration(table, measure)}.",
            "",
        ]
    lines += [
        "## Corrélations de Spearman entre mesures",
        "",
        md_table(corr, floatfmt=".2f"),
        "",
        "## Validation externe",
        "",
        f"Clubs avec valeur marchande actuelle > 0 : {len(valued):,}.",
        "",
        md_table(mv_corr, floatfmt=".2f"),
        "",
        "Figure : `results/figures/pagerank_map.pdf`.",
    ]
    write_report("centrality", lines)


if __name__ == "__main__":
    main()
