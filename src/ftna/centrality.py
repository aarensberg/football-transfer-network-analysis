"""A4. Centralités des clubs.

Mesures (graphe orienté vendeur → acheteur) :
- degrés et forces entrants/sortants ;
- PageRank pondéré (destinations recevant des joueurs de clubs eux-mêmes centraux) ;
- PageRank inverse, sur le graphe transposé (fournisseurs de clubs centraux) ;
- closeness entrante/sortante exacte sur la CFC géante, et sur tout le graphe avec la
  correction de Wasserman et Faust (formule du cours pour un graphe non connexe) ;
- betweenness exacte (non pondérée), parallélisée par paquets de sources ;
- centralité de vecteur propre (graphe non orienté pondéré, CFF géante), pour montrer
  pourquoi le PageRank lui est préféré (localisation sur le sous-réseau le plus dense) ;
- contrôle du PageRank avec α = 0,8 (valeur du cours) au lieu de 0,85.

Validation externe : valeur marchande actuelle (`clubs.current_mv`) et valeur marchande
moyenne sur les saisons de la fenêtre (`club_league`, cohérente avec la période du graphe).

Usage : `uv run python -m ftna.centrality` (`--plot-only` : figure seule)
Sorties : `results/centrality.md`, `results/tables/centrality.csv`,
`results/figures/pagerank_map.{pdf,png}`.
"""

import os
import sys
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import shortest_path

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
from ftna.communities import undirected_weighted
from ftna.data import load_raw
from ftna.distances import CHUNK, all_distances
from ftna.graph import GraphConfig

PAGERANK_ALPHA = 0.85
COURSE_ALPHA = 0.8  # facteur d'amortissement du cours (β)
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


def _partial_edge_betweenness(sources: list[int]) -> dict[tuple[int, int], float]:
    assert _WORKER_GRAPH is not None
    return nx.edge_betweenness_centrality_subset(
        _WORKER_GRAPH, sources, list(_WORKER_GRAPH), normalized=False
    )


def _parallel_sum(graph: nx.DiGraph, worker, processes: int | None) -> dict:
    """Somme des contributions de paquets disjoints de sources (Brandes par paquets)."""
    nodes = list(graph)
    processes = processes or os.cpu_count() or 1
    chunks = [nodes[i :: processes * 4] for i in range(processes * 4)]
    total: dict = {}
    with ProcessPoolExecutor(
        processes, initializer=_init_worker, initargs=(list(graph.edges()), nodes)
    ) as pool:
        for partial in pool.map(worker, chunks):
            for key, value in partial.items():
                total[key] = total.get(key, 0.0) + value
    return total


def exact_betweenness(graph: nx.DiGraph, processes: int | None = None) -> pd.Series:
    """Betweenness exacte non pondérée, normalisée par (n - 1)(n - 2) comme NetworkX.

    Les contributions de paquets disjoints de sources s'additionnent (vérifié contre
    `nx.betweenness_centrality` sur un graphe test : écart < 1e-12).
    """
    n = graph.number_of_nodes()
    total = pd.Series(_parallel_sum(graph, _partial_betweenness, processes))
    return total.reindex(list(graph), fill_value=0.0) / ((n - 1) * (n - 2))


def exact_edge_betweenness(
    graph: nx.DiGraph, processes: int | None = None
) -> pd.Series:
    """Betweenness exacte des arêtes (non pondérée), normalisée par n(n - 1) comme
    NetworkX pour un graphe orienté ; même décomposition par paquets de sources."""
    n = graph.number_of_nodes()
    total = pd.Series(_parallel_sum(graph, _partial_edge_betweenness, processes))
    total.index = pd.MultiIndex.from_tuples(total.index, names=["u", "v"])
    return total / (n * (n - 1))


def wf_closeness(graph: nx.DiGraph) -> tuple[pd.Series, pd.Series]:
    """Closeness entrante et sortante sur tout le graphe, corrigée par Wasserman et Faust.

    Pour un nœud atteignant r autres nœuds à une distance totale S :
    closeness = (r / (N - 1)) · (r / S) ; 0 si r = 0. C'est la formule du cours pour un
    graphe non connexe (et celle de `nx.closeness_centrality`, `wf_improved=True`).
    """
    nodes = list(graph)
    matrix = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight=None, format="csr")
    n = len(nodes)
    out_r, out_s = np.zeros(n), np.zeros(n)
    in_r, in_s = np.zeros(n), np.zeros(n)
    for start in range(0, n, CHUNK):
        rows = np.arange(start, min(start + CHUNK, n))
        dist = shortest_path(matrix, directed=True, unweighted=True, indices=rows)
        finite = np.isfinite(dist) & (dist > 0)
        dist = np.where(finite, dist, 0.0)
        out_r[rows], out_s[rows] = finite.sum(axis=1), dist.sum(axis=1)
        in_r += finite.sum(axis=0)
        in_s += dist.sum(axis=0)

    def formula(r: np.ndarray, total: np.ndarray) -> pd.Series:
        with np.errstate(divide="ignore", invalid="ignore"):
            values = np.where(r > 0, (r / (n - 1)) * (r / total), 0.0)
        return pd.Series(values, index=nodes)

    return formula(in_r, in_s), formula(out_r, out_s)


def eigenvector(graph: nx.DiGraph) -> pd.Series:
    """Centralité de vecteur propre sur la CFF géante non orientée pondérée (le graphe
    orienté n'étant pas fortement connexe, Perron-Frobenius ne s'y applique pas)."""
    undirected = undirected_weighted(graph)
    giant = undirected.subgraph(max(nx.connected_components(undirected), key=len))
    return pd.Series(nx.eigenvector_centrality_numpy(giant, weight="weight"))


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
    if exact:
        in_wf, out_wf = wf_closeness(graph)
        table["in_closeness_wf"], table["out_closeness_wf"] = in_wf, out_wf
        table["eigenvector"] = eigenvector(graph)
        table["pagerank_alpha08"] = nx.pagerank(
            graph, alpha=COURSE_ALPHA, weight="weight"
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


def window_market_value(config: GraphConfig | None = None) -> pd.Series:
    """Valeur marchande moyenne de chaque club sur les saisons de la fenêtre du graphe.

    `club_league` peut contenir deux lignes pour un même couple (club, saison) : on garde
    le maximum (comme en A9), puis on moyenne les saisons de valeur strictement positive.
    """
    config = config or GraphConfig()
    cl = load_raw(players_columns=["id"]).club_league
    cl = cl[cl.season.between(config.start_year, config.end_year)]
    per_season = cl.groupby(["club_id", "season"]).market_value.max()
    return per_season[per_season > 0].groupby("club_id").mean()


MEASURES = [
    "in_degree",
    "out_degree",
    "in_strength",
    "out_strength",
    "pagerank",
    "reverse_pagerank",
    "in_closeness",
    "out_closeness",
    "in_closeness_wf",
    "out_closeness_wf",
    "betweenness",
    "eigenvector",
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
        label="youth / reserve teams",
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
    ax.set_xlabel("Reverse PageRank (supplier of players)")
    ax.set_ylabel("PageRank (destination of players)")
    ax.set_title("Destinations and suppliers in the transfer network")
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
    table["window_mv"] = window_market_value().reindex(table.index)
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
    window_valued = table[table.window_mv > 0]
    mv_corr = pd.DataFrame(
        {
            "mesure": MEASURES,
            "Spearman avec current_mv": [
                valued[m].corr(valued.current_mv, method="spearman") for m in MEASURES
            ],
            "Spearman avec valeur moyenne 2010–2023": [
                window_valued[m].corr(window_valued.window_mv, method="spearman")
                for m in MEASURES
            ],
            "Spearman avec montants payés": [
                table[m].corr(table.fees_paid, method="spearman") for m in MEASURES
            ],
        }
    )
    scc = table.in_closeness.notna()
    wf_rho = {
        d: table.loc[scc, f"{d}_closeness"].corr(
            table.loc[scc, f"{d}_closeness_wf"], method="spearman"
        )
        for d in ("in", "out")
    }
    alpha_rho = table.pagerank.corr(table.pagerank_alpha08, method="spearman")
    alpha_overlap = (
        len(
            set(table.pagerank.nlargest(TOP).index)
            & set(table.pagerank_alpha08.nlargest(TOP).index)
        )
        / TOP
    )
    eig_top = table.nlargest(100, "eigenvector")
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
            "- Closeness de Wasserman et Faust (`*_closeness_wf`) : tout le graphe, "
            "(r/(N−1))·(r/Σd) avec r le nombre de clubs atteignables ; Spearman avec la "
            f"closeness sur la CFC géante (clubs de la CFC) : entrante {wf_rho['in']:.3f}, "
            f"sortante {wf_rho['out']:.3f}. Elle attribue aussi une valeur aux "
            f"{int((~scc).sum())} clubs hors de la CFC géante."
        ),
        (
            f"- PageRank avec α = {COURSE_ALPHA} (valeur du cours) : Spearman = {alpha_rho:.3f} "
            f"avec α = {PAGERANK_ALPHA} ; recouvrement du top {TOP} = {alpha_overlap:.0%}."
        ),
        (
            "- Vecteur propre (CFF géante non orientée pondérée) : top 100 composé de "
            f"{country_concentration(table, 'eigenvector')} ; part de jeunes/réserves "
            f"{eig_top.youth_or_reserve.mean():.0%}. La mesure se **localise** sur le "
            "sous-réseau le plus dense, d'où le choix du PageRank (cours 3)."
        ),
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
        "out_closeness_wf",
        "eigenvector",
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
        (
            f"Clubs avec valeur marchande actuelle > 0 : {len(valued):,} ; avec valeur "
            f"moyenne 2010–2023 > 0 (`club_league`, saisons valorisées) : {len(window_valued):,}. "
            "La valeur moyenne sur la fenêtre est la référence la plus cohérente avec la "
            "période du graphe ; la valeur actuelle reflète la situation postérieure à 2023."
        ),
        "",
        md_table(mv_corr, floatfmt=".2f"),
        "",
        "Figure : `results/figures/pagerank_map.pdf`.",
    ]
    write_report("centrality", lines)


if __name__ == "__main__":
    main()
