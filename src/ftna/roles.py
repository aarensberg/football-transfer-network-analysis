"""A10. Rôles des clubs dans les communautés (Guimerà & Amaral, 2005).

Sur le graphe non orienté pondéré et la partition Louvain de A5 :
- coefficient de participation P_i = 1 − Σ_s (k_is / k_i)², où k_is est la force du club i
  vers la communauté s : 0 si tous ses échanges restent dans une communauté ;
- score z_i : force intra-communauté standardisée au sein de la communauté du club.
Rôles : hub si z ≥ 2,5 ; seuils de P de Guimerà & Amaral pour le reste.
Ponts entre communautés : betweenness exacte des arêtes (graphe orienté, cours 3) ;
une arête sur beaucoup de plus courts chemins joue le rôle de pont.

Usage : `uv run python -m ftna.roles` (après `ftna.communities`)
Sorties : `results/roles.md`, `results/tables/roles.csv`,
`results/figures/community_graph.{pdf,png}`.
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from ftna.centrality import exact_edge_betweenness
from ftna.common import (
    NEUTRAL,
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

HUB_Z = 2.5
MIN_STRENGTH = 100  # clubs suffisamment actifs pour interpréter P
SHOWN_COMMUNITIES = 25
TOP_LINKS = 30  # liens les plus forts affichés sur le graphe des communautés
LINKS_PER_COMMUNITY = 2  # liens garantis à chaque communauté (aucune isolée)


def role(p: float, z: float) -> str:
    """Classification de Guimerà & Amaral (2005)."""
    if z >= HUB_Z:
        if p <= 0.30:
            return "R5 hub provincial"
        return "R6 hub connecteur" if p <= 0.75 else "R7 hub sans attache"
    if p <= 0.05:
        return "R1 ultra-périphérique"
    if p <= 0.62:
        return "R2 périphérique"
    return "R3 connecteur" if p <= 0.80 else "R4 sans attache"


def participation(undirected: nx.Graph, community: pd.Series) -> pd.DataFrame:
    rows = []
    for node in undirected:
        flows: dict[int, float] = {}
        for neighbour, data in undirected[node].items():
            c = community[neighbour]
            flows[c] = flows.get(c, 0.0) + data["weight"]
        strength = sum(flows.values())
        share = np.array(list(flows.values())) / strength
        rows.append(
            {
                "club_id": node,
                "strength": strength,
                "internal": flows.get(community[node], 0.0),
                "P": 1 - float((share**2).sum()),
                "partner_communities": len(flows),
            }
        )
    table = pd.DataFrame(rows).set_index("club_id")
    table["community"] = community
    grouped = table.groupby("community").internal
    std = grouped.transform("std").replace(0, np.nan)
    table["z"] = ((table.internal - grouped.transform("mean")) / std).fillna(0.0)
    table["role"] = [role(p, z) for p, z in zip(table.P, table.z)]
    return table


def edge_bridges(
    graph: nx.DiGraph, community: pd.Series
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Betweenness exacte des arêtes et part des arêtes inter-communautés en tête."""
    eb = exact_edge_betweenness(graph).rename("edge_betweenness").reset_index()
    eb["inter"] = eb.u.map(community).to_numpy() != eb.v.map(community).to_numpy()
    eb = eb.sort_values("edge_betweenness", ascending=False, ignore_index=True)
    stats = {
        "base": eb.inter.mean(),
        "top100": eb.inter.head(100).mean(),
        "top1000": eb.inter.head(1000).mean(),
        "ratio": eb.loc[eb.inter, "edge_betweenness"].mean()
        / eb.loc[~eb.inter, "edge_betweenness"].mean(),
    }
    names = dict(graph.nodes(data="name"))
    countries = dict(graph.nodes(data="country"))
    top = eb.head(1000).copy()
    top["from"] = [f"{names[u]} ({countries[u] or '?'})" for u in top.u]
    top["to"] = [f"{names[v]} ({countries[v] or '?'})" for v in top.v]
    top["weight"] = [graph[u][v]["weight"] for u, v in zip(top.u, top.v)]
    top["community_from"] = top.u.map(community)
    top["community_to"] = top.v.map(community)
    return top, stats


def community_names(communities: pd.DataFrame) -> pd.Series:
    """Libellé court : pays principaux (≥ 15 % des clubs) de chaque communauté."""

    def label(group: pd.DataFrame) -> str:
        share = group.country.fillna("?").value_counts(normalize=True)
        main = [c for c, s in share.items() if s >= 0.15][:3] or [share.index[0]]
        return " / ".join(main)

    return communities.groupby("community")[["country"]].apply(label)


def plot_community_graph(
    undirected: nx.Graph, community: pd.Series, names: pd.Series
) -> None:
    """Graphe des communautés : taille ∝ nombre de clubs, épaisseur ∝ transferts entre blocs."""
    sizes = community.value_counts()
    shown = list(sizes.index[:SHOWN_COMMUNITIES])
    flows: dict[tuple[int, int], float] = {}
    for u, v, w in undirected.edges(data="weight"):
        a, b = community[u], community[v]
        if a != b and a in shown and b in shown:
            key = (min(a, b), max(a, b))
            flows[key] = flows.get(key, 0.0) + w
    # Liens affichés : les plus forts au total et les plus forts de chaque communauté,
    # pour qu'aucune communauté ne soit isolée sur la figure.
    ranked = sorted(flows.items(), key=lambda kv: -kv[1])
    kept = dict(ranked[:TOP_LINKS])
    for c in shown:
        for key, w in [kv for kv in ranked if c in kv[0]][:LINKS_PER_COMMUNITY]:
            kept[key] = w
    meta = nx.Graph()
    meta.add_nodes_from(shown)
    meta.add_weighted_edges_from((a, b, w) for (a, b), w in kept.items())
    strongest = list(kept.items())
    # Disposition topologique (non pondérée) : stable et sans effondrement des gros nœuds.
    layout = nx.kamada_kawai_layout(meta, weight=None)
    setup_style()
    fig, ax = plt.subplots(figsize=(7.4, 6.0))
    ax.axis("off")
    max_w = max(w for _, w in strongest)
    nx.draw_networkx_edges(
        meta,
        layout,
        ax=ax,
        edge_color=NEUTRAL,
        alpha=0.7,
        width=[0.4 + 5 * meta[a][b]["weight"] / max_w for a, b in meta.edges],
    )
    nx.draw_networkx_nodes(
        meta,
        layout,
        ax=ax,
        node_color=SERIES[0],
        alpha=0.85,
        node_size=[12 * np.sqrt(sizes[c]) for c in meta.nodes],
        linewidths=0,
    )
    for c, (x, y) in layout.items():
        ax.annotate(
            f"C{c} " + " / ".join(names[c].split(" / ")[:2]),
            (x, y),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=6.3,
            color=TEXT_PRIMARY,
        )
    ax.set_title(
        f"Flux entre les {SHOWN_COMMUNITIES} plus grandes communautés\n"
        f"({TOP_LINKS} liens les plus forts + les {LINKS_PER_COMMUNITY} plus forts "
        "de chaque communauté)"
    )
    save_figure(fig, "community_graph")


def main() -> None:
    graph = main_graph()
    undirected = undirected_weighted(graph)
    communities = pd.read_csv(TABLES_DIR / "communities.csv")
    community = communities.set_index("club_id").community
    names = community_names(communities)

    table = participation(undirected, community)
    table["name"] = pd.Series(dict(graph.nodes(data="name")))
    table["country"] = pd.Series(dict(graph.nodes(data="country")))
    table["bloc"] = table.community.map(lambda c: f"C{c} {names[c]}")
    save_table(table.reset_index(), "roles")
    plot_community_graph(undirected, community, names)

    bridges, bridge_stats = edge_bridges(graph, community)
    save_table(bridges, "edge_betweenness")
    shown_bridges = bridges.head(15).assign(
        **{"inter-communautés": bridges.inter.head(15).map({True: "oui", False: ""})}
    )[["from", "to", "weight", "edge_betweenness", "inter-communautés"]]
    active = table[table.strength >= MIN_STRENGTH]
    roles = table.role.value_counts().sort_index()
    columns = ["name", "country", "bloc", "strength", "P", "z", "role"]
    connectors = active.nlargest(20, "P")[columns]
    hubs = table[table.z >= HUB_Z].sort_values("z", ascending=False)
    leaders = (
        table[table.community.isin(community.value_counts().index[:15])]
        .sort_values("z", ascending=False)
        .groupby("community")
        .head(2)
        .sort_values(["community", "z"], ascending=[True, False])[columns]
    )
    corr = (
        table[["P", "z"]]
        .join(
            pd.read_csv(TABLES_DIR / "centrality.csv").set_index("club_id")[
                ["betweenness", "out_closeness", "pagerank", "reverse_pagerank"]
            ]
        )
        .corr(method="spearman")
        .loc[
            ["P", "z"], ["betweenness", "out_closeness", "pagerank", "reverse_pagerank"]
        ]
    )
    corr.insert(0, "indicateur", corr.index)
    lines = [
        "# A10. Rôles des clubs dans les communautés",
        "",
        (
            "Généré par `uv run python -m ftna.roles`. Partition Louvain de A5 ; graphe non orienté "
            f"pondéré. Hubs : z ≥ {HUB_Z}. Table complète : `results/tables/roles.csv`."
        ),
        "",
        (
            f"- P médian : {table.P.median():.3f} ; P médian des clubs actifs (force ≥ {MIN_STRENGTH}) : "
            f"{active.P.median():.3f} ; clubs actifs : {len(active):,}."
        ),
        "",
        "## Répartition des rôles",
        "",
        md_table(pd.DataFrame({"rôle": roles.index, "clubs": roles.to_numpy()})),
        "",
        f"## Clubs passerelles : P le plus élevé parmi les clubs actifs (force ≥ {MIN_STRENGTH})",
        "",
        md_table(connectors, floatfmt=".2f"),
        "",
        f"## Hubs (z ≥ {HUB_Z}) : {len(hubs)} clubs",
        "",
        md_table(hubs[columns].head(25), floatfmt=".2f"),
        "",
        "## Leaders des 15 plus grandes communautés (2 plus forts z)",
        "",
        md_table(leaders, floatfmt=".2f"),
        "",
        "## Lien avec les centralités (Spearman)",
        "",
        md_table(corr, floatfmt=".2f"),
        "",
        "Figure : `results/figures/community_graph.pdf`.",
        "",
        "## Ponts : betweenness des arêtes",
        "",
        (
            "Betweenness exacte des arêtes (graphe orienté, non pondéré, normalisée par "
            "n(n − 1)). Top 1 000 : `results/tables/edge_betweenness.csv`."
        ),
        "",
        (
            f"- Part des arêtes reliant deux communautés : {bridge_stats['base']:.1%} de "
            f"toutes les arêtes, {bridge_stats['top1000']:.1%} des 1 000 arêtes de plus "
            f"forte betweenness, {bridge_stats['top100']:.1%} des 100 premières."
        ),
        (
            "- Betweenness moyenne d'une arête inter-communautés : "
            f"{bridge_stats['ratio']:.1f} fois celle d'une arête interne."
        ),
        "",
        md_table(shown_bridges, floatfmt=".2e"),
    ]
    write_report("roles", lines)


if __name__ == "__main__":
    main()
