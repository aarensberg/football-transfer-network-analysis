"""A3. Distances : diamètre, rayon, centre, périphérie et distribution des distances.

Conventions :
- distances en nombre de sauts (arêtes non pondérées) : le poids mesure une intensité
  d'échange, pas une longueur ;
- orienté : calcul exact sur la plus grande composante fortement connexe (CFC), où
  toutes les distances sont finies ;
- non orienté : calcul exact sur la plus grande composante faiblement connexe (CFF).

Usage : `uv run python -m ftna.distances`
Sorties : `results/distances.md`, `results/figures/distance_distribution.{pdf,png}`.
"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import shortest_path

from ftna.common import (
    club_label,
    main_graph,
    md_table,
    save_figure,
    setup_style,
    write_report,
)

CHUNK = 500  # lignes de la matrice des distances calculées à la fois


@dataclass(frozen=True)
class DistanceResult:
    """Excentricités (sortantes et entrantes) et histogramme de toutes les distances."""

    nodes: list[int]
    out_ecc: np.ndarray  # distance maximale depuis le nœud
    in_ecc: np.ndarray  # distance maximale vers le nœud
    histogram: np.ndarray  # histogram[d] = nombre de couples ordonnés à distance d


def all_distances(graph: nx.Graph, directed: bool) -> DistanceResult:
    """BFS depuis chaque nœud (scipy, en C), par blocs pour limiter la mémoire."""
    nodes = list(graph)
    matrix = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight=None, format="csr")
    n = len(nodes)
    out_ecc = np.zeros(n, dtype=int)
    in_ecc = np.zeros(n, dtype=int)
    histogram = np.zeros(n, dtype=np.int64)
    for start in range(0, n, CHUNK):
        rows = np.arange(start, min(start + CHUNK, n))
        dist = shortest_path(matrix, directed=directed, unweighted=True, indices=rows)
        if np.isinf(dist).any():
            raise ValueError("Composante non connexe : distances infinies.")
        dist = dist.astype(int)
        out_ecc[rows] = dist.max(axis=1)
        in_ecc = np.maximum(in_ecc, dist.max(axis=0))
        histogram += np.bincount(dist.ravel(), minlength=n)[:n]
    histogram[0] = 0  # distance d'un nœud à lui-même
    last = int(np.nonzero(histogram)[0].max())
    return DistanceResult(nodes, out_ecc, in_ecc, histogram[: last + 1])


def mean_distance(histogram: np.ndarray) -> float:
    d = np.arange(len(histogram))
    return float((d * histogram).sum() / histogram.sum())


def extremal_nodes(
    graph: nx.Graph,
    result: DistanceResult,
    ecc: np.ndarray,
    value: int,
    limit: int = 10,
) -> str:
    """Clubs dont l'excentricité vaut `value` (les plus actifs d'abord)."""
    members = [result.nodes[i] for i in np.nonzero(ecc == value)[0]]
    members.sort(key=lambda v: graph.degree(v, weight="weight"), reverse=True)
    shown = ", ".join(club_label(graph, v) for v in members[:limit])
    return f"{len(members)} clubs : {shown}" + (" …" if len(members) > limit else "")


def plot_histograms(directed: DistanceResult, undirected: DistanceResult) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    width = 0.4
    for offset, result, label in (
        (-width / 2, directed, "orienté (CFC géante)"),
        (width / 2, undirected, "non orienté (CFF géante)"),
    ):
        d = np.arange(1, len(result.histogram))
        share = result.histogram[1:] / result.histogram.sum()
        ax.bar(d + offset, share, width=width * 0.9, label=label)
    ax.set_xlabel("Distance (nombre de transferts successifs)")
    ax.set_ylabel("Part des couples de clubs")
    ax.set_xticks(range(1, max(len(directed.histogram), len(undirected.histogram))))
    ax.grid(axis="x", visible=False)
    ax.legend()
    ax.set_title("Distribution des distances entre clubs")
    save_figure(fig, "distance_distribution")


def summary_row(
    label: str, graph: nx.Graph, result: DistanceResult, ecc: np.ndarray
) -> dict[str, object]:
    return {
        "graphe": label,
        "nœuds": graph.number_of_nodes(),
        "diamètre": int(ecc.max()),
        "rayon": int(ecc.min()),
        "distance moyenne": mean_distance(result.histogram),
        "distance médiane": int(
            np.searchsorted(np.cumsum(result.histogram), result.histogram.sum() / 2)
        ),
    }


def main() -> None:
    graph = main_graph()
    core = graph.subgraph(max(nx.strongly_connected_components(graph), key=len)).copy()
    giant = graph.subgraph(
        max(nx.weakly_connected_components(graph), key=len)
    ).to_undirected()

    directed = all_distances(core, directed=True)
    undirected = all_distances(giant, directed=False)
    plot_histograms(directed, undirected)

    table = pd.DataFrame(
        [
            summary_row(
                "orienté, CFC géante (excentricité sortante)",
                core,
                directed,
                directed.out_ecc,
            ),
            summary_row(
                "orienté, CFC géante (excentricité entrante)",
                core,
                directed,
                directed.in_ecc,
            ),
            summary_row(
                "non orienté, CFF géante", giant, undirected, undirected.out_ecc
            ),
        ]
    )
    # Référence : distance moyenne d'un graphe aléatoire ≈ ln(n) / ln(<k>).
    n, k = (
        giant.number_of_nodes(),
        2 * giant.number_of_edges() / giant.number_of_nodes(),
    )
    random_l = np.log(n) / np.log(k)
    shares = (
        pd.DataFrame(
            {
                "distance": np.arange(1, len(directed.histogram)),
                "orienté (part)": directed.histogram[1:] / directed.histogram.sum(),
            }
        )
        .merge(
            pd.DataFrame(
                {
                    "distance": np.arange(1, len(undirected.histogram)),
                    "non orienté (part)": undirected.histogram[1:]
                    / undirected.histogram.sum(),
                }
            ),
            how="outer",
        )
        .fillna(0.0)
    )
    d_ecc, u_ecc = directed.out_ecc, undirected.out_ecc
    lines = [
        "# A3. Distances",
        "",
        (
            "Généré par `uv run python -m ftna.distances`. Distances en nombre de sauts, calcul exact "
            "(BFS depuis chaque nœud). Orienté : plus grande CFC (toutes distances finies) ; "
            "non orienté : plus grande CFF."
        ),
        "",
        md_table(table, floatfmt=".2f"),
        "",
        (
            f"Référence aléatoire (non orienté, même n = {n:,} et degré moyen {k:.1f}) : "
            f"ln(n)/ln(<k>) ≈ {random_l:.2f}."
        ),
        "",
        "## Distribution des distances",
        "",
        md_table(shares, floatfmt=".4f"),
        "",
        "Figure : `results/figures/distance_distribution.pdf`.",
        "",
        "## Centre et périphérie",
        "",
        f"- Centre orienté (excentricité sortante = rayon {d_ecc.min()}) : "
        + extremal_nodes(core, directed, d_ecc, d_ecc.min()),
        f"- Centre orienté (excentricité entrante = rayon {directed.in_ecc.min()}) : "
        + extremal_nodes(core, directed, directed.in_ecc, directed.in_ecc.min()),
        f"- Périphérie orientée (excentricité sortante = diamètre {d_ecc.max()}) : "
        + extremal_nodes(core, directed, d_ecc, d_ecc.max()),
        f"- Périphérie orientée (excentricité entrante = diamètre {directed.in_ecc.max()}) : "
        + extremal_nodes(core, directed, directed.in_ecc, directed.in_ecc.max()),
        f"- Centre non orienté (rayon {u_ecc.min()}) : "
        + extremal_nodes(giant, undirected, u_ecc, u_ecc.min()),
        f"- Périphérie non orientée (diamètre {u_ecc.max()}) : "
        + extremal_nodes(giant, undirected, u_ecc, u_ecc.max()),
    ]
    write_report("distances", lines)


if __name__ == "__main__":
    main()
