"""A5. Communautés de clubs.

Méthode principale : Louvain (maximisation de la modularité) sur le graphe non orienté
pondéré, où w(u, v) = w(u→v) + w(v→u) (intensité totale d'échange entre deux clubs).
Robustesse : stabilité entre graines, effet de la résolution, Leiden (modularité),
Louvain orienté (modularité orientée), propagation de labels asynchrone (algorithme
sans fonction objectif, cours 4). Hiérarchie : niveaux du dendrogramme de Louvain.
Significativité : Louvain sur des graphes
aléatoires du modèle de configuration pondéré (forces des clubs préservées).

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
N_NULL = 3  # réalisations du modèle nul
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


def strength_null_model(undirected: nx.Graph, seed: int) -> nx.Graph:
    """Modèle de configuration pondéré : chaque club reçoit autant de demi-transferts que
    sa force, appariés au hasard ; multiplicités = poids, boucles retirées.

    C'est le modèle nul de la modularité (poids attendu k_i k_j / 2m) : il conserve
    exactement les forces (aux boucles près) mais détruit toute structure de groupe.
    """
    rng = np.random.default_rng(seed)
    nodes = np.array(list(undirected))
    strength = np.array([undirected.degree(n, weight="weight") for n in nodes])
    stubs = np.repeat(nodes, strength.astype(np.int64))
    rng.shuffle(stubs)
    u, v = stubs[0::2], stubs[1::2]  # la somme des forces est paire (= 2 × poids total)
    keep = u != v
    pairs = pd.DataFrame(
        {"u": np.minimum(u[keep], v[keep]), "v": np.maximum(u[keep], v[keep])}
    ).value_counts()
    null = nx.Graph()
    null.add_nodes_from(int(n) for n in nodes)
    null.add_weighted_edges_from(
        (int(a), int(b), int(w)) for (a, b), w in pairs.items()
    )
    return null


def null_model_test(undirected: nx.Graph, observed: float) -> pd.DataFrame:
    """Modularité de Louvain sur `N_NULL` graphes du modèle nul, comparée à l'observée."""
    rows = []
    for seed in range(N_NULL):
        null = strength_null_model(undirected, seed=SEED + seed)
        comms = nx.community.louvain_communities(null, weight="weight", seed=SEED)
        rows.append(
            {
                "réalisation": seed + 1,
                "arêtes distinctes": null.number_of_edges(),
                "communautés": len(comms),
                "modularité": nx.community.modularity(null, comms),
            }
        )
    table = pd.DataFrame(rows)
    std = table.modularité.std()
    table.attrs["z"] = (observed - table.modularité.mean()) / std if std else np.inf
    return table


def louvain_hierarchy(
    undirected: nx.Graph, nodes: list[int], country: np.ndarray
) -> pd.DataFrame:
    """Niveaux du dendrogramme de Louvain (graine `SEED`) : du plus fin au plus agrégé ;
    le dernier niveau est la partition de référence."""
    rows = []
    for level, comms in enumerate(
        nx.community.louvain_partitions(undirected, weight="weight", seed=SEED), 1
    ):
        labels = labels_of(comms, nodes)
        purity = pd.crosstab(labels, country).max(axis=1).sum() / len(
            nodes
        )  # part des clubs appartenant au pays dominant de leur communauté
        rows.append(
            {
                "niveau": level,
                "communautés": len(comms),
                "communautés ≥ 50 clubs": sum(len(c) >= 50 for c in comms),
                "modularité": nx.community.modularity(undirected, comms),
                "pureté nationale": purity,
                "NMI avec le pays": nmi(labels, country),
            }
        )
    return pd.DataFrame(rows)


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
        image, ax=ax, fraction=0.03, pad=0.02, label="share of the community's clubs"
    )
    ax.set_title(
        f"Country composition of the {TOP_COMMUNITIES} largest communities (Louvain)"
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
    lpa = list(
        nx.community.asyn_lpa_communities(undirected, weight="weight", seed=SEED)
    )
    country_partition = [set(np.array(nodes)[country == c]) for c in np.unique(country)]

    def compare_row(name: str, partition: list[set[int]], ref_nmi: float) -> dict:
        """Modularités non orientée et orientée d'une partition, NMI."""
        partition_labels = labels_of(partition, nodes)
        return {
            "partition": name,
            "communautés": len(partition),
            "modularité (non orientée)": nx.community.modularity(undirected, partition),
            "modularité orientée": nx.community.modularity(graph, partition),
            "NMI avec référence": ref_nmi,
            "NMI avec le pays": nmi(partition_labels, country),
        }

    comparisons = pd.DataFrame(
        [
            compare_row("Louvain non orienté (référence)", communities, 1.0),
            compare_row(
                "Leiden (modularité)",
                leiden,
                nmi(labels_of(leiden, nodes), labels.to_numpy()),
            ),
            compare_row(
                "Louvain orienté (optimise la modularité orientée)",
                directed,
                nmi(labels_of(directed, nodes), labels.to_numpy()),
            ),
            compare_row(
                "Propagation de labels asynchrone (pondérée)",
                lpa,
                nmi(labels_of(lpa, nodes), labels.to_numpy()),
            ),
            compare_row(
                "Pays (partition de référence externe)",
                country_partition,
                nmi(country, labels.to_numpy()),
            ),
        ]
    )
    null = null_model_test(undirected, modularity)
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
        (
            "Modularité non orientée : graphe w(u,v) = w(u→v) + w(v→u) ; modularité "
            "orientée : formule de Leicht et Newman sur le graphe orienté pondéré."
        ),
        "",
        (
            "La propagation de labels n'optimise aucune fonction objectif : sa "
            "concordance avec Louvain (NMI) indique si la structure trouvée dépend de "
            "la modularité."
        ),
        "",
        "## Hiérarchie : niveaux du dendrogramme de Louvain",
        "",
        md_table(louvain_hierarchy(undirected, nodes, country), floatfmt=".3f"),
        "",
        (
            "Chaque niveau agrège les communautés du niveau précédent (passes de "
            "Louvain) ; le dernier niveau est la partition de référence."
        ),
        "",
        "## Significativité : modèle nul",
        "",
        (
            f"Louvain (graine {SEED}) sur {N_NULL} graphes du modèle de configuration "
            "pondéré (forces des clubs préservées, appariement aléatoire des "
            "transferts, boucles retirées)."
        ),
        "",
        md_table(null, floatfmt=".3f"),
        "",
        (
            f"- Modularité observée {modularity:.3f} contre "
            f"{null.modularité.mean():.3f} ± {null.modularité.std():.3f} sous le "
            f"modèle nul (score z ≈ {null.attrs['z']:.0f})."
        ),
        "",
        f"## Stabilité de Louvain ({N_SEEDS} graines)",
        "",
        md_table(stability(undirected, nodes), floatfmt=".3f"),
        "",
        "## Effet de la résolution",
        "",
        md_table(resolution_scan(undirected, nodes, country), floatfmt=".3f"),
        "",
        (
            "Lecture : la colonne « modularité (γ = 1) » évalue chaque partition avec la "
            "modularité standard, que Louvain à γ = 1 optimise directement ; son maximum "
            "à γ = 1 est donc attendu et ne justifie pas à lui seul ce choix. La NMI "
            "croît mécaniquement avec le nombre de communautés : sa hausse avec γ ne "
            "prouve pas que les communautés fines sont « plus nationales »."
        ),
    ]
    write_report("communities", lines)


if __name__ == "__main__":
    main()
