"""A1. Structure du réseau : degrés, forces, réciprocité, clustering, assortativité.

Usage : `uv run python -m ftna.structure`
Sorties : `results/structure.md`, `results/figures/degree_ccdf.{pdf,png}`.
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from ftna.common import (
    SEED,
    main_graph,
    md_table,
    save_figure,
    setup_style,
    write_report,
)


def degree_table(graph: nx.DiGraph) -> pd.DataFrame:
    """Degrés (clubs partenaires distincts) et forces (nombre de transferts) par club."""
    return pd.DataFrame(
        {
            "in_degree": dict(graph.in_degree()),
            "out_degree": dict(graph.out_degree()),
            "in_strength": dict(graph.in_degree(weight="weight")),
            "out_strength": dict(graph.out_degree(weight="weight")),
        }
    )


def describe(series: pd.Series) -> dict[str, float]:
    return {
        "moyenne": series.mean(),
        "médiane": series.median(),
        "q90": series.quantile(0.9),
        "q99": series.quantile(0.99),
        "max": series.max(),
    }


def ccdf(values: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Fonction de survie empirique P(X ≥ x) sur les valeurs strictement positives."""
    x = np.sort(values[values > 0].to_numpy())
    y = 1.0 - np.arange(len(x)) / len(x)
    return x, y


def plot_ccdf(degrees: pd.DataFrame) -> None:
    setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    panels = [
        (axes[0], "in_degree", "out_degree", "Degré (clubs partenaires distincts)"),
        (axes[1], "in_strength", "out_strength", "Force (nombre de transferts)"),
    ]
    for ax, col_in, col_out, xlabel in panels:
        for col, label in (
            (col_in, "entrant (arrivées)"),
            (col_out, "sortant (départs)"),
        ):
            x, y = ccdf(degrees[col])
            ax.loglog(x, y, label=label)
        ax.set_xlabel(xlabel)
    axes[0].set_ylabel("P(X ≥ x)")
    axes[0].legend(loc="lower left")
    fig.suptitle(
        "Distributions cumulées complémentaires des degrés et des forces", y=1.02
    )
    save_figure(fig, "degree_ccdf")


def configuration_graph(undirected: nx.Graph, seed: int = SEED) -> nx.Graph:
    """Modèle de configuration non orienté (mêmes degrés), simplifié : multi-arêtes
    fusionnées et boucles retirées (quelques degrés diminuent légèrement)."""
    config = nx.Graph(
        nx.configuration_model([d for _, d in undirected.degree()], seed=seed)
    )
    config.remove_edges_from(nx.selfloop_edges(config))
    return config


def directed_configuration_graph(graph: nx.DiGraph, seed: int = SEED) -> nx.DiGraph:
    """Modèle de configuration orienté (mêmes degrés entrants et sortants), simplifié."""
    nodes = list(graph)
    config = nx.DiGraph(
        nx.directed_configuration_model(
            [graph.in_degree(n) for n in nodes],
            [graph.out_degree(n) for n in nodes],
            seed=seed,
        )
    )
    config.remove_edges_from(nx.selfloop_edges(config))
    return config


def clustering_baselines(undirected: nx.Graph) -> dict[str, float]:
    """Clustering du graphe et de deux références : G(n, m) (espérance = densité) et un
    modèle de configuration (mêmes degrés, multi-arêtes et boucles retirées)."""
    n, m = undirected.number_of_nodes(), undirected.number_of_edges()
    config = configuration_graph(undirected)
    return {
        "observed_avg": nx.average_clustering(undirected),
        "observed_transitivity": nx.transitivity(undirected),
        "gnm_expected": 2 * m / (n * (n - 1)),
        "config_avg": nx.average_clustering(config),
        "config_transitivity": nx.transitivity(config),
        "config_edges": config.number_of_edges(),
    }


def main() -> None:
    graph = main_graph()
    n, m = graph.number_of_nodes(), graph.number_of_edges()
    degrees = degree_table(graph)
    undirected = graph.to_undirected(as_view=False)

    # Réciprocité : arêtes dont l'inverse existe ; version pondérée = part des transferts
    # portés par des couples réciproques.
    reciprocity = nx.reciprocity(graph)
    reciprocal_weight = sum(
        w for u, v, w in graph.edges(data="weight") if graph.has_edge(v, u)
    )
    total_weight = graph.size(weight="weight")
    expected_reciprocity = m / (n * (n - 1))  # espérance sous G(n, m) orienté

    clustering = clustering_baselines(undirected)
    assortativity = {
        "out→in (vendeur→acheteur)": nx.degree_assortativity_coefficient(
            graph, x="out", y="in"
        ),
        "in→in": nx.degree_assortativity_coefficient(graph, x="in", y="in"),
        "out→out": nx.degree_assortativity_coefficient(graph, x="out", y="out"),
        "non orienté": nx.degree_assortativity_coefficient(undirected),
    }
    rank_corr = degrees.corr(method="spearman")

    plot_ccdf(degrees)

    stats = pd.DataFrame({col: describe(degrees[col]) for col in degrees.columns}).T
    stats.insert(0, "mesure", stats.index)
    sources = int(((degrees.in_degree == 0) & (degrees.out_degree > 0)).sum())
    sinks = int(((degrees.out_degree == 0) & (degrees.in_degree > 0)).sum())
    lines = [
        "# A1. Structure du réseau",
        "",
        "Généré par `uv run python -m ftna.structure`.",
        "",
        (
            f"- Nœuds : {n:,} ; arêtes orientées : {m:,} ; arêtes non orientées : "
            f"{undirected.number_of_edges():,} ; densité orientée : {nx.density(graph):.2e}."
        ),
        (
            f"- Clubs uniquement vendeurs (degré entrant nul) : {sources:,} ; uniquement "
            f"acheteurs (degré sortant nul) : {sinks:,}."
        ),
        "",
        "## Degrés et forces",
        "",
        md_table(stats),
        "",
        (
            "Corrélation de Spearman entre degré entrant et sortant : "
            f"{rank_corr.loc['in_degree', 'out_degree']:.3f} ; entre force entrante et "
            f"sortante : {rank_corr.loc['in_strength', 'out_strength']:.3f}."
        ),
        "",
        "Figure : `results/figures/degree_ccdf.pdf`.",
        "",
        "## Réciprocité",
        "",
        (
            f"- Réciprocité (arêtes) : {reciprocity:.3f}, contre {expected_reciprocity:.2e} "
            "attendu sous G(n, m) orienté."
        ),
        f"- Part des transferts sur des couples réciproques : {reciprocal_weight / total_weight:.3f}.",
        "",
        "## Clustering (graphe non orienté, non pondéré)",
        "",
        (
            f"- Clustering moyen observé : {clustering['observed_avg']:.3f} ; transitivité : "
            f"{clustering['observed_transitivity']:.3f}."
        ),
        f"- G(n, m) de même taille : espérance {clustering['gnm_expected']:.2e}.",
        (
            f"- Modèle de configuration (mêmes degrés, graine {SEED}, "
            f"{clustering['config_edges']:,} arêtes après nettoyage) : clustering moyen "
            f"{clustering['config_avg']:.3f}, transitivité {clustering['config_transitivity']:.3f}."
        ),
        "",
        "## Assortativité de degré",
        "",
        *(f"- {k} : {v:.3f}" for k, v in assortativity.items()),
    ]
    write_report("structure", lines)


if __name__ == "__main__":
    main()
