"""A2. Connectivité : composantes faiblement et fortement connexes, décomposition bow-tie,
sommets d'articulation, ponts et composante biconnexe (robustesse, cours 1).

Usage : `uv run python -m ftna.connectivity`
Sortie : `results/connectivity.md`.
"""

import networkx as nx
import pandas as pd

from ftna.common import club_label, main_graph, md_table, write_report


def bow_tie(graph: nx.DiGraph, core: set[int]) -> dict[str, set[int]]:
    """Décomposition de Broder et al. (2000) autour de la plus grande CFC.

    IN : nœuds qui atteignent le cœur sans en être atteignables ; OUT : l'inverse ;
    AUTRES : tendrils, tubes et composantes déconnectées.
    """
    seed = next(iter(core))
    reachable = nx.descendants(graph, seed) | {seed}
    reaching = nx.ancestors(graph, seed) | {seed}
    in_set = reaching - core
    out_set = reachable - core
    others = set(graph) - core - in_set - out_set
    return {"CFC géante": core, "IN": in_set, "OUT": out_set, "Autres": others}


def describe_nodes(graph: nx.DiGraph, nodes: set[int]) -> dict[str, object]:
    """Profil d'un groupe de nœuds : effectif, degré moyen, part de jeunes, pays principaux."""
    if not nodes:
        return {
            "clubs": 0,
            "degré total moyen": 0.0,
            "part jeunes/réserves": 0.0,
            "pays principaux": "",
        }
    data = pd.DataFrame.from_dict({n: graph.nodes[n] for n in nodes}, orient="index")
    countries = data.country.replace("", "?").value_counts().head(3)
    return {
        "clubs": len(nodes),
        "degré total moyen": sum(graph.degree(n) for n in nodes) / len(nodes),
        "part jeunes/réserves": float(data.youth_or_reserve.mean()),
        "pays principaux": ", ".join(f"{c} ({k})" for c, k in countries.items()),
    }


def cut_structure(graph: nx.DiGraph, giant: set[int]) -> dict[str, object]:
    """Sommets d'articulation, ponts et 2-connexité de la CFF géante (non orientée).

    Pour chaque sommet d'articulation, on compte les clubs qu'il détacherait de la
    composante principale s'il était retiré.
    """
    undirected = graph.subgraph(giant).to_undirected(as_view=False)
    points = list(nx.articulation_points(undirected))
    bridges = list(nx.bridges(undirected))
    blocks = sorted(nx.biconnected_components(undirected), key=len, reverse=True)
    detached = {}
    for a in points:
        rest = nx.restricted_view(undirected, [a], [])
        sizes = sorted((len(c) for c in nx.connected_components(rest)), reverse=True)
        detached[a] = sum(sizes[1:])
    return {
        "nodes": undirected.number_of_nodes(),
        "points": points,
        "bridges": bridges,
        "largest_block": len(blocks[0]),
        "detached": pd.Series(detached, dtype=int).sort_values(ascending=False),
    }


def component_sizes(components: list[set[int]]) -> pd.DataFrame:
    sizes = (
        pd.Series([len(c) for c in components])
        .value_counts()
        .sort_index(ascending=False)
    )
    return pd.DataFrame(
        {
            "taille": sizes.index.astype(int),
            "nombre de composantes": sizes.to_numpy().astype(int),
        }
    )


def main() -> None:
    graph = main_graph()
    n = graph.number_of_nodes()
    weak = sorted(nx.weakly_connected_components(graph), key=len, reverse=True)
    strong = sorted(nx.strongly_connected_components(graph), key=len, reverse=True)
    core = strong[0]
    parts = bow_tie(graph, core)
    core_weight = graph.subgraph(core).size(weight="weight")

    small_weak = [", ".join(club_label(graph, v) for v in sorted(c)) for c in weak[1:]]
    bow = pd.DataFrame(
        [{"partie": k, **describe_nodes(graph, v)} for k, v in parts.items()]
    )
    bow.insert(2, "part des nœuds", bow.clubs / n)
    cuts = cut_structure(graph, weak[0])
    top_cuts = cuts["detached"].head(10)
    cut_table = pd.DataFrame(
        {
            "club": [club_label(graph, a) for a in top_cuts.index],
            "degré": [graph.degree(a) for a in top_cuts.index],
            "clubs détachés": top_cuts.to_numpy(),
        }
    )
    lines = [
        "# A2. Connectivité",
        "",
        "Généré par `uv run python -m ftna.connectivity`.",
        "",
        (
            f"- Graphe faiblement connexe : {nx.is_weakly_connected(graph)} ; "
            f"fortement connexe : {nx.is_strongly_connected(graph)}."
        ),
        "",
        "## Composantes faiblement connexes (CFF)",
        "",
        f"- Nombre : {len(weak)} ; plus grande : {len(weak[0]):,} nœuds ({len(weak[0]) / n:.2%}).",
        "- Petites CFF :",
        *(f"  - {s}" for s in small_weak),
        "",
        "## Composantes fortement connexes (CFC)",
        "",
        (
            f"- Nombre : {len(strong)} ; plus grande : {len(core):,} nœuds ({len(core) / n:.2%}), "
            f"{graph.subgraph(core).number_of_edges():,} arêtes, "
            f"{core_weight / graph.size(weight='weight'):.2%} des transferts."
        ),
        (
            f"- CFC de taille 1 : {sum(len(c) == 1 for c in strong)} ; "
            f"deuxième plus grande : {len(strong[1])} nœuds."
        ),
        "",
        md_table(component_sizes(strong)),
        "",
        "## Décomposition bow-tie autour de la CFC géante",
        "",
        md_table(bow, floatfmt=".3g"),
        "",
        "## Robustesse : sommets d'articulation et ponts (CFF géante, non orientée)",
        "",
        (
            f"- Sommets d'articulation (cutvertices) : {len(cuts['points'])} ; ponts : "
            f"{len(cuts['bridges'])}. La CFF géante est donc 1-connexe (κ = λ = 1)."
        ),
        (
            f"- Plus grande composante biconnexe (2-connexe) : {cuts['largest_block']:,} "
            f"clubs ({cuts['largest_block'] / cuts['nodes']:.2%} de la CFF géante) ; "
            f"retirer un sommet d'articulation détache au total "
            f"{int(cuts['detached'].sum()):,} clubs (au plus {int(cuts['detached'].max())} "
            "pour un même club)."
        ),
        "",
        md_table(cut_table),
    ]
    write_report("connectivity", lines)


if __name__ == "__main__":
    main()
