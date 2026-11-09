"""A3. Distances : diamètre, rayon, centre, périphérie et distribution des distances.

Conventions :
- distances en nombre de sauts (arêtes non pondérées) : le poids mesure une intensité
  d'échange, pas une longueur ;
- orienté : calcul exact sur la plus grande composante fortement connexe (CFC), où
  toutes les distances sont finies ;
- non orienté : calcul exact sur la plus grande composante faiblement connexe (CFF) ;
- référence « petit monde » : mêmes calculs sur des modèles de configuration (mêmes
  degrés, graine fixe), plus juste que ln(n)/ln(<k>) pour des degrés hétérogènes.

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
    SEED,
    club_label,
    main_graph,
    md_table,
    save_figure,
    setup_style,
    write_report,
)
from ftna.structure import configuration_graph, directed_configuration_graph

CHUNK = 500  # lignes de la matrice des distances calculées à la fois


@dataclass(frozen=True)
class DistanceResult:
    """Excentricités, sommes des distances (sortantes et entrantes) et histogramme."""

    nodes: list[int]
    out_ecc: np.ndarray  # distance maximale depuis le nœud
    in_ecc: np.ndarray  # distance maximale vers le nœud
    out_sum: np.ndarray  # somme des distances depuis le nœud
    in_sum: np.ndarray  # somme des distances vers le nœud
    histogram: np.ndarray  # histogram[d] = nombre de couples ordonnés à distance d

    def closeness(self, direction: str) -> np.ndarray:
        """Closeness classique (n - 1) / somme des distances ; `out` ou `in`."""
        sums = self.out_sum if direction == "out" else self.in_sum
        return (len(self.nodes) - 1) / sums


def all_distances(graph: nx.Graph, directed: bool) -> DistanceResult:
    """BFS depuis chaque nœud (scipy, en C), par blocs pour limiter la mémoire."""
    nodes = list(graph)
    matrix = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight=None, format="csr")
    n = len(nodes)
    out_ecc = np.zeros(n, dtype=int)
    in_ecc = np.zeros(n, dtype=int)
    out_sum = np.zeros(n, dtype=np.int64)
    in_sum = np.zeros(n, dtype=np.int64)
    histogram = np.zeros(n, dtype=np.int64)
    for start in range(0, n, CHUNK):
        rows = np.arange(start, min(start + CHUNK, n))
        dist = shortest_path(matrix, directed=directed, unweighted=True, indices=rows)
        if np.isinf(dist).any():
            raise ValueError("Composante non connexe : distances infinies.")
        dist = dist.astype(int)
        out_ecc[rows] = dist.max(axis=1)
        in_ecc = np.maximum(in_ecc, dist.max(axis=0))
        out_sum[rows] = dist.sum(axis=1)
        in_sum += dist.sum(axis=0)
        histogram += np.bincount(dist.ravel(), minlength=n)[:n]
    histogram[0] = 0  # distance d'un nœud à lui-même
    last = int(np.nonzero(histogram)[0].max())
    return DistanceResult(
        nodes, out_ecc, in_ecc, out_sum, in_sum, histogram[: last + 1]
    )


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
        (-width / 2, directed, "directed (largest SCC)"),
        (width / 2, undirected, "undirected (largest WCC)"),
    ):
        d = np.arange(1, len(result.histogram))
        share = result.histogram[1:] / result.histogram.sum()
        ax.bar(d + offset, share, width=width * 0.9, label=label)
    ax.set_xlabel("Distance (number of successive transfers)")
    ax.set_ylabel("Share of club pairs")
    ax.set_xticks(range(1, max(len(directed.histogram), len(undirected.histogram))))
    ax.grid(axis="x", visible=False)
    ax.legend()
    ax.set_title("Distribution of distances between clubs")
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


def configuration_baseline(
    core: nx.DiGraph,
    giant: nx.Graph,
    directed: DistanceResult,
    undirected: DistanceResult,
) -> pd.DataFrame:
    """Distances exactes et clustering dans des modèles de configuration de mêmes
    degrés que la CFC géante (orienté) et la CFF géante (non orienté)."""
    d_config = directed_configuration_graph(core)
    d_core = d_config.subgraph(max(nx.strongly_connected_components(d_config), key=len))
    u_config = configuration_graph(giant)
    u_giant = u_config.subgraph(max(nx.connected_components(u_config), key=len))
    d_null = all_distances(d_core, directed=True)
    u_null = all_distances(u_giant, directed=False)
    rows = []
    for label, graph, result in (
        ("orienté, CFC géante observée", core, directed),
        ("orienté, modèle de configuration (CFC géante)", d_core, d_null),
        ("non orienté, CFF géante observée", giant, undirected),
        ("non orienté, modèle de configuration (composante géante)", u_giant, u_null),
    ):
        rows.append(
            {
                "graphe": label,
                "nœuds": graph.number_of_nodes(),
                "arêtes": graph.number_of_edges(),
                "distance moyenne": mean_distance(result.histogram),
                "diamètre": int(result.out_ecc.max()),
                "rayon": int(result.out_ecc.min()),
                "clustering moyen": nx.average_clustering(graph)
                if not graph.is_directed()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


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
    baseline = configuration_baseline(core, giant, directed, undirected)
    obs, rnd = baseline.iloc[2], baseline.iloc[3]
    sigma = (obs["clustering moyen"] / rnd["clustering moyen"]) / (
        obs["distance moyenne"] / rnd["distance moyenne"]
    )
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
            f"ln(n)/ln(<k>) ≈ {random_l:.2f} (formule d'Erdős–Rényi, degrés homogènes)."
        ),
        "",
        "## Référence petit monde : modèles de configuration",
        "",
        (
            f"Mêmes degrés (entrants et sortants en orienté) que le graphe observé, graine {SEED}, "
            "multi-arêtes fusionnées et boucles retirées ; distances exactes sur la composante "
            "géante (fortement connexe en orienté)."
        ),
        "",
        md_table(baseline, floatfmt=".3f"),
        "",
        (
            f"Coefficient petit monde σ = (C / C_config) / (L / L_config) = {sigma:.1f} "
            "(non orienté ; σ > 1 : petit monde)."
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
