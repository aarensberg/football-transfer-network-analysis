"""A5. Communautés de clubs.

Méthode principale : Louvain (maximisation de la modularité) sur le graphe non orienté
pondéré, où w(u, v) = w(u→v) + w(v→u) (intensité totale d'échange entre deux clubs).
Robustesse : stabilité entre graines, effet de la résolution, Leiden (modularité),
Louvain orienté (modularité orientée).

Usage : `uv run python -m ftna.communities`
Sorties : `results/communities.md`, `results/tables/communities.csv`,
`results/figures/community_countries.{pdf,png}`.
"""

from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from ftna.common import (
    SEED,
    TEXT_PRIMARY,
    main_graph,
    md_table,
    save_figure,
    save_table,
    setup_style,
    write_report,
)

N_SEEDS = 10
RESOLUTIONS = (0.5, 1.0, 2.0, 4.0)
TOP_COMMUNITIES = 15


def undirected_weighted(graph: nx.DiGraph) -> nx.Graph:
    """Version non orientée dont le poids somme les deux sens d'échange."""
    undirected = nx.Graph()
    undirected.add_nodes_from(graph.nodes(data=True))
    for u, v, w in graph.edges(data="weight"):
        if undirected.has_edge(u, v):
            undirected[u][v]["weight"] += w
        else:
            undirected.add_edge(u, v, weight=w)
    return undirected


def labels_of(communities: list[set[int]], nodes: list[int]) -> np.ndarray:
    """Étiquette de communauté par nœud (communautés triées par taille décroissante)."""
    ordered = sorted(communities, key=len, reverse=True)
    lookup = {n: i for i, c in enumerate(ordered) for n in c}
    return np.array([lookup[n] for n in nodes])


def _entropy(counts: np.ndarray) -> float:
    p = counts[counts > 0] / counts.sum()
    return float(-(p * np.log(p)).sum())


def nmi(a: np.ndarray, b: np.ndarray) -> float:
    """Information mutuelle normalisée (moyenne arithmétique des entropies)."""
    table = pd.crosstab(a, b).to_numpy().astype(float)
    n = table.sum()
    pij = table / n
    pi, pj = pij.sum(axis=1, keepdims=True), pij.sum(axis=0, keepdims=True)
    nz = pij > 0
    mi = float((pij[nz] * np.log(pij[nz] / (pi @ pj)[nz])).sum())
    h = (_entropy(table.sum(axis=1)) + _entropy(table.sum(axis=0))) / 2
    return mi / h if h > 0 else 1.0


def ari(a: np.ndarray, b: np.ndarray) -> float:
    """Indice de Rand ajusté."""
    table = pd.crosstab(a, b).to_numpy()

    def comb2(x: np.ndarray) -> float:
        return float((x * (x - 1) / 2).sum())

    index = comb2(table)
    rows, cols = comb2(table.sum(axis=1)), comb2(table.sum(axis=0))
    total = len(a) * (len(a) - 1) / 2
    expected = rows * cols / total
    return (index - expected) / ((rows + cols) / 2 - expected)


def describe_communities(
    graph: nx.DiGraph, undirected: nx.Graph, labels: pd.Series
) -> pd.DataFrame:
    """Profil de chaque communauté : taille, poids interne, pays, clubs les plus actifs."""
    nodes = pd.DataFrame(
        {
            "community": labels,
            "country": pd.Series(dict(graph.nodes(data="country"))).replace("", "?"),
            "name": pd.Series(dict(graph.nodes(data="name"))),
            "strength": pd.Series(dict(undirected.degree(weight="weight"))),
            "youth": pd.Series(dict(graph.nodes(data="youth_or_reserve"))),
        }
    )
    internal = pd.Series(0.0, index=sorted(labels.unique()))
    for u, v, w in undirected.edges(data="weight"):
        if labels[u] == labels[v]:
            internal[labels[u]] += w
    rows = []
    for community, members in nodes.groupby("community"):
        countries = members.country.value_counts()
        total = members.strength.sum()
        top_clubs = members[~members.youth].nlargest(4, "strength").name
        rows.append(
            {
                "communauté": int(community) + 1,
                "clubs": len(members),
                "pays dominant": countries.index[0],
                "part du pays dominant": countries.iloc[0] / len(members),
                "pays (top 3)": ", ".join(
                    f"{c} {k}" for c, k in countries.head(3).items()
                ),
                "poids interne": 2 * internal[community] / total if total else 0.0,
                "clubs les plus actifs": ", ".join(top_clubs),
            }
        )
    return pd.DataFrame(rows)


def stability(undirected: nx.Graph, nodes: list[int]) -> pd.DataFrame:
    runs = []
    for seed in range(N_SEEDS):
        comms = nx.community.louvain_communities(undirected, weight="weight", seed=seed)
        runs.append((comms, labels_of(comms, nodes)))
    pairs = list(combinations(range(N_SEEDS), 2))
    return pd.DataFrame(
        {
            "indicateur": [
                "modularité (moyenne)",
                "modularité (écart-type)",
                "nombre de communautés (min)",
                "nombre de communautés (max)",
                "NMI entre graines (moyenne)",
                "ARI entre graines (moyenne)",
            ],
            "valeur": [
                np.mean([nx.community.modularity(undirected, c) for c, _ in runs]),
                np.std([nx.community.modularity(undirected, c) for c, _ in runs]),
                min(len(c) for c, _ in runs),
                max(len(c) for c, _ in runs),
                np.mean([nmi(runs[i][1], runs[j][1]) for i, j in pairs]),
                np.mean([ari(runs[i][1], runs[j][1]) for i, j in pairs]),
            ],
        }
    )


def resolution_scan(
    undirected: nx.Graph, nodes: list[int], country: np.ndarray
) -> pd.DataFrame:
    rows = []
    for gamma in RESOLUTIONS:
        comms = nx.community.louvain_communities(
            undirected, weight="weight", resolution=gamma, seed=SEED
        )
        sizes = sorted((len(c) for c in comms), reverse=True)
        rows.append(
            {
                "résolution γ": gamma,
                "communautés": len(comms),
                "communautés ≥ 50 clubs": sum(s >= 50 for s in sizes),
                "plus grande": sizes[0],
                "modularité (γ = 1)": nx.community.modularity(undirected, comms),
                "NMI avec le pays": nmi(labels_of(comms, nodes), country),
            }
        )
    return pd.DataFrame(rows)


def plot_composition(
    profile: pd.DataFrame, graph: nx.DiGraph, labels: pd.Series
) -> None:
    """Carte de chaleur : part de chaque pays dans les plus grandes communautés."""
    top = profile.nsmallest(TOP_COMMUNITIES, "communauté").communauté - 1
    country = pd.Series(dict(graph.nodes(data="country"))).replace("", "?")
    frame = pd.DataFrame({"community": labels, "country": country})
    frame = frame[frame.community.isin(top)]
    share = pd.crosstab(frame.community, frame.country, normalize="index")
    # Colonnes ordonnées communauté par communauté (pays ≥ 10 %) : structure en blocs.
    columns: list[str] = []
    for community in share.index:
        row = share.loc[community].sort_values(ascending=False)
        columns += [c for c in row[row >= 0.1].index[:3] if c not in columns]
    share = share[columns]
    setup_style()
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    image = ax.imshow(share.to_numpy(), cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(columns)), columns, rotation=60, ha="right", fontsize=7)
    sizes = frame.community.value_counts()
    ax.set_yticks(
        range(len(share.index)),
        [f"C{c + 1} ({sizes[c]:,} clubs)" for c in share.index],
        fontsize=7,
    )
    ax.grid(False)
    for (i, j), value in np.ndenumerate(share.to_numpy()):
        if value >= 0.15:
            ax.text(
                j,
                i,
                f"{value:.0%}",
                ha="center",
                va="center",
                fontsize=5.5,
                color="white" if value > 0.55 else TEXT_PRIMARY,
            )
    fig.colorbar(
        image, ax=ax, fraction=0.03, pad=0.02, label="part des clubs de la communauté"
    )
    ax.set_title(
        f"Composition par pays des {TOP_COMMUNITIES} plus grandes communautés (Louvain)"
    )
    save_figure(fig, "community_countries")


def country_spread(
    graph: nx.DiGraph, labels: pd.Series, countries: list[str]
) -> pd.DataFrame:
    """Nombre de communautés nécessaires pour couvrir 90 % des clubs d'un pays."""
    country = pd.Series(dict(graph.nodes(data="country")))
    rows = []
    for c in countries:
        counts = labels[country == c].value_counts()
        cover = int((counts.cumsum() / counts.sum() < 0.9).sum() + 1)
        rows.append(
            {
                "pays": c,
                "clubs": int(counts.sum()),
                "communautés (90 %)": cover,
                "part dans la 1ʳᵉ": counts.iloc[0] / counts.sum(),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    graph = main_graph()
    undirected = undirected_weighted(graph)
    nodes = list(undirected)
    country = np.array([undirected.nodes[n]["country"] or "?" for n in nodes])

    communities = nx.community.louvain_communities(
        undirected, weight="weight", seed=SEED
    )
    labels = pd.Series(labels_of(communities, nodes), index=nodes)
    modularity = nx.community.modularity(undirected, communities)
    profile = describe_communities(graph, undirected, labels)
    save_table(
        pd.DataFrame(
            {
                "club_id": nodes,
                "community": labels.to_numpy() + 1,
                "name": [undirected.nodes[n]["name"] for n in nodes],
                "country": country,
            }
        ),
        "communities",
    )
    plot_composition(profile, graph, labels)

    leiden = nx.community.leiden_communities(
        undirected, weight="weight", metric="modularity", seed=SEED
    )
    directed = nx.community.louvain_communities(graph, weight="weight", seed=SEED)
    country_partition = [set(np.array(nodes)[country == c]) for c in np.unique(country)]
    comparisons = pd.DataFrame(
        [
            {
                "partition": "Louvain non orienté (référence)",
                "communautés": len(communities),
                "modularité": modularity,
                "NMI avec référence": 1.0,
                "NMI avec le pays": nmi(labels.to_numpy(), country),
            },
            {
                "partition": "Leiden (modularité)",
                "communautés": len(leiden),
                "modularité": nx.community.modularity(undirected, leiden),
                "NMI avec référence": nmi(labels_of(leiden, nodes), labels.to_numpy()),
                "NMI avec le pays": nmi(labels_of(leiden, nodes), country),
            },
            {
                "partition": "Louvain orienté (modularité orientée)",
                "communautés": len(directed),
                "modularité": nx.community.modularity(undirected, directed),
                "NMI avec référence": nmi(
                    labels_of(directed, nodes), labels.to_numpy()
                ),
                "NMI avec le pays": nmi(labels_of(directed, nodes), country),
            },
            {
                "partition": "Pays (partition de référence externe)",
                "communautés": len(country_partition),
                "modularité": nx.community.modularity(undirected, country_partition),
                "NMI avec référence": nmi(country, labels.to_numpy()),
                "NMI avec le pays": 1.0,
            },
        ]
    )
    sizes = profile.clubs.sort_values(ascending=False)
    purity = (
        profile["part du pays dominant"] * profile.clubs
    ).sum() / profile.clubs.sum()
    top_countries = pd.Series(country).value_counts().head(12).index.tolist()
    lines = [
        "# A5. Communautés",
        "",
        (
            "Généré par `uv run python -m ftna.communities`. Louvain (NetworkX, résolution 1, "
            f"graine {SEED}) sur le graphe non orienté pondéré w(u,v) = w(u→v) + w(v→u). "
            "Affectations : `results/tables/communities.csv`."
        ),
        "",
        "## Partition de référence",
        "",
        f"- Communautés : {len(communities)} ; modularité : {modularity:.3f}.",
        (
            f"- Les {TOP_COMMUNITIES} plus grandes couvrent {sizes.head(TOP_COMMUNITIES).sum() / sizes.sum():.1%} "
            f"des clubs ; communautés de moins de 10 clubs : {(sizes < 10).sum()}."
        ),
        f"- Pureté nationale moyenne (part du pays dominant, pondérée par la taille) : {purity:.3f}.",
        "",
        md_table(profile.nsmallest(TOP_COMMUNITIES + 10, "communauté"), floatfmt=".2f"),
        "",
        "`poids interne` : part de la force des membres réalisée à l'intérieur de la communauté.",
        "",
        "Figure : `results/figures/community_countries.pdf`.",
        "",
        "## Dispersion des grands pays entre communautés",
        "",
        md_table(country_spread(graph, labels, top_countries), floatfmt=".2f"),
        "",
        "## Comparaisons",
        "",
        md_table(comparisons, floatfmt=".3f"),
        "",
        f"## Stabilité de Louvain ({N_SEEDS} graines)",
        "",
        md_table(stability(undirected, nodes), floatfmt=".3f"),
        "",
        "## Effet de la résolution",
        "",
        md_table(resolution_scan(undirected, nodes, country), floatfmt=".3f"),
    ]
    write_report("communities", lines)


if __name__ == "__main__":
    main()
