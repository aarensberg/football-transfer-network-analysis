"""A6. Réseau agrégé par pays : transferts domestiques, soldes, corridors internationaux.

Chaque club porte le pays de sa dernière ligue connue (≤ 2023) ; les 68 clubs sans pays
sont ignorés ici. Les volumes ne concernent que les clubs décrits dans `clubs.csv`.
La part « même ligue » utilise la ligue de chaque club **la saison du transfert**
(`club_league`), pour ne pas confondre promotions et relégations avec des échanges
entre ligues ; la version « dernière ligue connue » est donnée pour comparaison.

Usage : `uv run python -m ftna.countries`
Sorties : `results/countries.md`, `results/tables/country_flows.csv`,
`results/figures/country_balance.{pdf,png}`.
"""

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from ftna.common import (
    TABLES_DIR,
    main_graph,
    md_table,
    save_figure,
    save_table,
    setup_style,
    write_report,
)
from ftna.data import load_raw
from ftna.graph import GraphConfig, filter_transfers

DIVERGING = ("#2a78d6", "#e34948")  # exportateur net / importateur net
MIN_CLUBS = 20  # pays retenus pour les classements de part domestique


def edge_frame(graph: nx.DiGraph) -> pd.DataFrame:
    country = dict(graph.nodes(data="country"))
    league = dict(graph.nodes(data="league_id"))
    return pd.DataFrame(
        [
            (country[u], country[v], league[u], league[v], w)
            for u, v, w in graph.edges(data="weight")
        ],
        columns=["from", "to", "league_from", "league_to", "weight"],
    )


def same_league_at_season(config: GraphConfig | None = None) -> tuple[float, float]:
    """Part des transferts entre deux clubs de la même ligue la saison du transfert.

    Une seule ligue par couple (club, saison), choisie comme dans `club_attributes`
    (valeur marchande la plus élevée, puis code de ligue) pour éviter la
    multiplication de lignes. Renvoie (part, couverture parmi les transferts du graphe).
    """
    raw = load_raw(players_columns=["id"])
    transfers, _ = filter_transfers(raw, config or GraphConfig())
    league = (
        raw.club_league.sort_values(
            ["club_id", "season", "market_value", "league_id"],
            ascending=[True, True, False, True],
        )
        .drop_duplicates(["club_id", "season"])
        .set_index(["club_id", "season"])
        .league_id
    )
    from_league = pd.MultiIndex.from_arrays(
        [transfers.left_club_id, transfers.year]
    ).map(league)
    to_league = pd.MultiIndex.from_arrays(
        [transfers.joined_club_id, transfers.year]
    ).map(league)
    known = pd.notna(from_league) & pd.notna(to_league)
    same = (from_league[known] == to_league[known]).mean()
    return float(same), float(known.mean())


def country_table(edges: pd.DataFrame, clubs: pd.Series) -> pd.DataFrame:
    """Volumes domestiques et internationaux par pays."""
    known = edges[(edges["from"] != "") & (edges["to"] != "")]
    domestic = known[known["from"] == known["to"]].groupby("from").weight.sum()
    intl = known[known["from"] != known["to"]]
    exports = intl.groupby("from").weight.sum()
    imports = intl.groupby("to").weight.sum()
    partners = (
        pd.concat(
            [
                intl[["from", "to"]],
                intl[["to", "from"]].set_axis(["from", "to"], axis=1),
            ]
        )
        .groupby("from")
        .to.nunique()
    )
    table = (
        pd.DataFrame(
            {
                "clubs": clubs,
                "domestiques": domestic,
                "exportés": exports,
                "importés": imports,
                "pays partenaires": partners,
            }
        )
        .fillna(0)
        .astype(int)
    )
    table = table[table.index != ""]
    involved = table.domestiques + table.exportés + table.importés
    table["part domestique"] = table.domestiques / involved
    table["solde (exp. − imp.)"] = table.exportés - table.importés
    table.index.name = "pays"
    return table.sort_values("clubs", ascending=False)


def plot_balance(table: pd.DataFrame, n: int = 10) -> None:
    """Barres divergentes : principaux exportateurs et importateurs nets."""
    balance = table["solde (exp. − imp.)"]
    selected = pd.concat([balance.nlargest(n), balance.nsmallest(n)]).sort_values()
    setup_style()
    fig, ax = plt.subplots(figsize=(6.0, 4.8))
    colors = [DIVERGING[0] if v > 0 else DIVERGING[1] for v in selected]
    ax.barh(selected.index, selected.to_numpy(), color=colors, height=0.75)
    ax.axvline(0, color="#52514e", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Transferts internationaux sortants − entrants (2010–2023)")
    ax.set_title("Exportateurs (bleu) et importateurs (rouge) nets de joueurs")
    ax.tick_params(axis="y", labelsize=7)
    save_figure(fig, "country_balance")


def main() -> None:
    graph = main_graph()
    edges = edge_frame(graph)
    clubs = pd.Series(dict(graph.nodes(data="country"))).value_counts()
    table = country_table(edges, clubs)
    save_table(table.reset_index(), "country_flows")
    plot_balance(table)

    known = edges[(edges["from"] != "") & (edges["to"] != "")]
    total = known.weight.sum()
    domestic_share = known[known["from"] == known["to"]].weight.sum() / total
    same_league = edges[
        (edges.league_from != "") & (edges.league_from == edges.league_to)
    ]
    same_league_share = same_league.weight.sum() / edges.weight.sum()
    season_league_share, season_league_coverage = same_league_at_season()

    # Bloc de chaque pays = communauté Louvain qui contient le plus de ses clubs (A5).
    communities = pd.read_csv(TABLES_DIR / "communities.csv")
    bloc = communities.groupby("country").community.agg(
        lambda s: s.value_counts().index[0]
    )
    intl = known[known["from"] != known["to"]]
    corridors = (
        intl.groupby(["from", "to"])
        .weight.sum()
        .sort_values(ascending=False)
        .head(25)
        .reset_index()
    )
    corridors["même bloc (A5)"] = [
        "oui" if bloc.get(a) == bloc.get(b) else ""
        for a, b in zip(corridors["from"], corridors.to)
    ]
    intl_same_bloc = (
        sum(
            w
            for a, b, w in intl[["from", "to", "weight"]].itertuples(index=False)
            if bloc.get(a) == bloc.get(b)
        )
        / intl.weight.sum()
    )

    big = table[table.clubs >= MIN_CLUBS]
    lines = [
        "# A6. Réseau agrégé par pays",
        "",
        "Généré par `uv run python -m ftna.countries`. Table complète : `results/tables/country_flows.csv`.",
        "",
        f"- Transferts entre clubs de pays connus : {total:,} ; part **domestique** : {domestic_share:.1%}.",
        (
            f"- Part des transferts entre deux clubs de la **même ligue la saison du transfert** : "
            f"{season_league_share:.1%} (ligue connue pour les deux clubs dans "
            f"{season_league_coverage:.1%} des transferts) ; avec la dernière ligue connue : "
            f"{same_league_share:.1%}."
        ),
        (
            f"- Transferts internationaux : {intl.weight.sum():,} ; dont entre pays du même bloc de "
            f"communautés (A5) : {intl_same_bloc:.1%}."
        ),
        f"- Pays : {len(table)} ; couples de pays reliés : {intl.groupby(['from', 'to']).ngroups:,}.",
        "",
        f"## Pays les plus fermés et les plus ouverts (≥ {MIN_CLUBS} clubs)",
        "",
        md_table(
            big.nlargest(10, "part domestique").reset_index()[
                ["pays", "clubs", "part domestique", "pays partenaires"]
            ],
            floatfmt=".3f",
        ),
        "",
        md_table(
            big.nsmallest(10, "part domestique").reset_index()[
                ["pays", "clubs", "part domestique", "pays partenaires"]
            ],
            floatfmt=".3f",
        ),
        "",
        "## Soldes internationaux",
        "",
        md_table(
            table.nlargest(10, "solde (exp. − imp.)").reset_index()[
                ["pays", "exportés", "importés", "solde (exp. − imp.)"]
            ]
        ),
        "",
        md_table(
            table.nsmallest(10, "solde (exp. − imp.)").reset_index()[
                ["pays", "exportés", "importés", "solde (exp. − imp.)"]
            ]
        ),
        "",
        "Figure : `results/figures/country_balance.pdf`.",
        "",
        "## Pays les plus connectés (nombre de pays partenaires)",
        "",
        md_table(
            table.nlargest(10, "pays partenaires").reset_index()[
                ["pays", "pays partenaires", "exportés", "importés"]
            ]
        ),
        "",
        "## Principaux corridors internationaux",
        "",
        md_table(
            corridors.rename(
                columns={"from": "de", "to": "vers", "weight": "transferts"}
            )
        ),
    ]
    write_report("countries", lines)


if __name__ == "__main__":
    main()
