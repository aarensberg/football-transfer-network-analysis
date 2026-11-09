"""A7–A8. Analyses de sensibilité aux choix de modélisation.

Variantes comparées au graphe de référence (2010–2023, sans End of loan, jeunes inclus) :
- sans équipes de jeunes et réserves (A7) ;
- sous-périodes 2010–2016 et 2017–2023 (A8, stabilité temporelle) ;
- sans transferts de type « Unknown » (A8) ;
- avec les retours de prêt « End of loan » (A8, décision 4).

Pour chaque variante : structure (taille, réciprocité, clustering, assortativité,
composantes, diamètre
et rayon exacts), stabilité des centralités (Spearman et recouvrement des tops sur les
clubs communs) et des communautés (NMI avec la référence et avec le pays).
La betweenness est approchée (k = 1000 sources) pour toutes les variantes, référence
comprise, afin de comparer des quantités homogènes.

Usage : `uv run python -m ftna.sensitivity` (~7 min)
Sorties : `results/sensitivity.md`, `results/tables/sensitivity_*.csv`.
"""

from dataclasses import dataclass, field

import networkx as nx
import numpy as np
import pandas as pd

from ftna.common import SEED, main_graph, md_table, save_table, write_report
from ftna.communities import labels_of, nmi, undirected_weighted
from ftna.data import load_raw
from ftna.distances import all_distances
from ftna.graph import GraphConfig, build_graph, club_attributes, filter_transfers

BETWEENNESS_K = 1000
TOP = 50
MEASURES = [
    "out_strength",
    "in_strength",
    "pagerank",
    "reverse_pagerank",
    "out_closeness",
    "betweenness",
]


@dataclass
class VariantResult:
    """Résultats d'une variante."""

    name: str
    structure: dict[str, object]
    centrality: pd.DataFrame
    communities: pd.Series
    extra: dict[str, object] = field(default_factory=dict)


def analyse(name: str, graph: nx.DiGraph) -> VariantResult:
    print(
        f"[{name}] {graph.number_of_nodes():,} nœuds, {graph.number_of_edges():,} arêtes",
        flush=True,
    )
    undirected = undirected_weighted(graph)
    core = graph.subgraph(max(nx.strongly_connected_components(graph), key=len)).copy()
    distances = all_distances(core, directed=True)
    centrality = pd.DataFrame(
        {
            "name": dict(graph.nodes(data="name")),
            "out_strength": dict(graph.out_degree(weight="weight")),
            "in_strength": dict(graph.in_degree(weight="weight")),
            "pagerank": nx.pagerank(graph, weight="weight"),
            "reverse_pagerank": nx.pagerank(graph.reverse(copy=False), weight="weight"),
            "out_closeness": pd.Series(
                distances.closeness("out"), index=distances.nodes
            ),
            "betweenness": nx.betweenness_centrality(graph, k=BETWEENNESS_K, seed=SEED),
        }
    )
    communities = nx.community.louvain_communities(
        undirected, weight="weight", seed=SEED
    )
    nodes = list(undirected)
    labels = pd.Series(labels_of(communities, nodes), index=nodes)
    country = np.array([undirected.nodes[n]["country"] or "?" for n in nodes])
    hist = distances.histogram
    structure = {
        "variante": name,
        "nœuds": graph.number_of_nodes(),
        "arêtes": graph.number_of_edges(),
        "transferts": int(graph.size(weight="weight")),
        "réciprocité": nx.reciprocity(graph),
        "clustering moyen": nx.average_clustering(undirected),
        "assortativité (vendeur→acheteur)": nx.degree_assortativity_coefficient(
            graph, x="out", y="in"
        ),
        "CFF": nx.number_weakly_connected_components(graph),
        "part CFC géante": core.number_of_nodes() / graph.number_of_nodes(),
        "diamètre (CFC)": int(distances.out_ecc.max()),
        "rayon (CFC)": int(distances.out_ecc.min()),
        "distance moyenne": float((np.arange(len(hist)) * hist).sum() / hist.sum()),
        "communautés": len(communities),
        "modularité": nx.community.modularity(undirected, communities),
        "NMI avec le pays": nmi(labels.to_numpy(), country),
    }
    return VariantResult(name, structure, centrality, labels)


def compare(reference: VariantResult, variant: VariantResult) -> dict[str, object]:
    """Stabilité des centralités et des communautés sur les clubs communs."""
    common = reference.centrality.index.intersection(variant.centrality.index)
    row: dict[str, object] = {"variante": variant.name, "clubs communs": len(common)}
    for measure in MEASURES:
        a = reference.centrality.loc[common, measure]
        b = variant.centrality.loc[common, measure]
        both = a.notna() & b.notna()
        row[f"ρ {measure}"] = a[both].corr(b[both], method="spearman")
        top_a, top_b = set(a.nlargest(TOP).index), set(b.nlargest(TOP).index)
        row[f"top{TOP} {measure}"] = len(top_a & top_b) / TOP
    row["NMI communautés"] = nmi(
        reference.communities.loc[common].to_numpy(),
        variant.communities.loc[common].to_numpy(),
    )
    return row


def top_lists(result: VariantResult, measures: list[str], n: int = 10) -> pd.DataFrame:
    return pd.DataFrame(
        {m: result.centrality.nlargest(n, m).name.to_numpy() for m in measures}
    )


def build_variant(config: GraphConfig) -> nx.DiGraph:
    raw = load_raw(players_columns=["id"])
    transfers, _ = filter_transfers(raw, config)
    return build_graph(transfers, club_attributes(raw, config.end_year))


def main() -> None:
    variants = {
        "référence": main_graph(),
        "sans jeunes/réserves": main_graph(exclude_youth=True),
        "2010–2016": build_variant(GraphConfig(start_year=2010, end_year=2016)),
        "2017–2023": build_variant(GraphConfig(start_year=2017, end_year=2023)),
        "sans type Unknown": build_variant(
            GraphConfig(excluded_types=("End of loan", "Unknown"))
        ),
        "avec End of loan": build_variant(GraphConfig(excluded_types=())),
    }
    results = {name: analyse(name, graph) for name, graph in variants.items()}
    reference = results["référence"]

    structure = pd.DataFrame([r.structure for r in results.values()])
    stability = pd.DataFrame(
        [compare(reference, r) for name, r in results.items() if name != "référence"]
    )
    save_table(structure, "sensitivity_structure")
    save_table(stability, "sensitivity_stability")

    rho_cols = [
        "variante",
        "clubs communs",
        *(f"ρ {m}" for m in MEASURES),
        "NMI communautés",
    ]
    top_cols = ["variante", *(f"top{TOP} {m}" for m in MEASURES)]
    focus = ["reverse_pagerank", "pagerank", "betweenness", "out_closeness"]
    lines = [
        "# A7–A8. Analyses de sensibilité",
        "",
        (
            "Généré par `uv run python -m ftna.sensitivity`. Betweenness approchée "
            f"(k = {BETWEENNESS_K}, graine {SEED}) pour toutes les variantes ; Louvain graine {SEED}."
        ),
        "",
        "## Structure",
        "",
        md_table(structure, floatfmt=".3f"),
        "",
        "## Stabilité des centralités (Spearman sur les clubs communs)",
        "",
        md_table(stability[rho_cols], floatfmt=".3f"),
        "",
        f"## Recouvrement des top {TOP}",
        "",
        md_table(stability[top_cols], floatfmt=".2f"),
        "",
    ]
    for name in ("sans jeunes/réserves", "2010–2016", "2017–2023"):
        lines += [
            f"## Top 10 : {name}",
            "",
            md_table(top_lists(results[name], focus)),
            "",
        ]
    write_report("sensitivity", lines)


if __name__ == "__main__":
    main()
