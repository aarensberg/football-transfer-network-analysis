"""A9. Hiérarchie des flux : les joueurs « descendent »-ils vers des clubs moins valorisés ?

Pour chaque transfert retenu dans le graphe, on compare la valeur marchande du club
vendeur et du club acheteur **la saison du transfert** (`club_league.market_value`,
maximum en cas de doublon (club, saison) pour éviter la multiplication de lignes).
Convention : saison = année du transfert ; robustesse avec la saison précédente.

Usage : `uv run python -m ftna.hierarchy`
Sorties : `results/hierarchy.md`, `results/figures/value_ratio.{pdf,png}`.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ftna.common import (
    NEUTRAL,
    SERIES,
    md_table,
    save_figure,
    setup_style,
    write_report,
)
from ftna.data import load_raw
from ftna.graph import GraphConfig, filter_transfers


def categorize(transfers: pd.DataFrame) -> pd.Series:
    """Catégorie lisible : prêt, définitif payé, définitif sans montant, type inconnu."""
    category = transfers.transfer_type.map({"Loan": "prêt", "Unknown": "type inconnu"})
    permanent = transfers.transfer_type == "Not loan"
    category[permanent & (transfers.transfer_fee > 0)] = "définitif payé"
    category[permanent & (transfers.transfer_fee == 0)] = "définitif sans montant"
    return category


def with_values(transfers: pd.DataFrame, values: pd.Series, lag: int) -> pd.DataFrame:
    """Ajoute la valeur des deux clubs pour la saison `year - lag` ; garde les couples > 0."""
    season = transfers.year - lag
    out = transfers.assign(
        mv_from=pd.MultiIndex.from_arrays([transfers.left_club_id, season]).map(values),
        mv_to=pd.MultiIndex.from_arrays([transfers.joined_club_id, season]).map(values),
    )
    out = out[(out.mv_from > 0) & (out.mv_to > 0)].copy()
    out["log_ratio"] = np.log10(out.mv_to / out.mv_from)
    return out


def summary(frame: pd.DataFrame, total: int) -> pd.DataFrame:
    rows = []
    for category, group in [("tous", frame), *frame.groupby("category")]:
        rows.append(
            {
                "catégorie": category,
                "transferts valorisés": len(group),
                "couverture": len(group) / total if category == "tous" else np.nan,
                "vers moins valorisé": (group.log_ratio < 0).mean(),
                "vers plus valorisé": (group.log_ratio > 0).mean(),
                "médiane log10(acheteur/vendeur)": group.log_ratio.median(),
            }
        )
    return pd.DataFrame(rows)


# Libellés anglais des catégories, pour la figure du rapport uniquement.
CATEGORY_EN = {
    "prêt": "loan",
    "définitif payé": "permanent, paid",
    "définitif sans montant": "permanent, no fee",
}


def plot_ratio(frame: pd.DataFrame) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    bins = np.linspace(-3, 3, 61)
    for color, category in zip(
        SERIES, ("prêt", "définitif payé", "définitif sans montant")
    ):
        values = frame.log_ratio[frame.category == category].clip(-3, 3)
        ax.hist(
            values,
            bins=bins,
            density=True,
            histtype="step",
            linewidth=2,
            color=color,
            label=f"{CATEGORY_EN[category]} (n = {len(values):,})",
        )
    ax.axvline(0, color=NEUTRAL, linewidth=1, linestyle="--")
    ax.set_xlabel(
        "log10(buying club value / selling club value), season of the transfer"
    )
    ax.set_ylabel("density")
    ax.set_title("Direction of transfers in the economic hierarchy of clubs")
    ax.legend(loc="upper left", fontsize=7)
    save_figure(fig, "value_ratio")


def main() -> None:
    raw = load_raw(players_columns=["id"])
    transfers, _ = filter_transfers(raw, GraphConfig())
    transfers = transfers.assign(category=categorize(transfers))
    values = raw.club_league.groupby(["club_id", "season"]).market_value.max()

    same = with_values(transfers, values, lag=0)
    previous = with_values(transfers, values, lag=1)
    plot_ratio(same)
    lines = [
        "# A9. Hiérarchie des flux",
        "",
        (
            "Généré par `uv run python -m ftna.hierarchy`. Valeur marchande des clubs dans "
            "`club_league` (saison du transfert), transferts du graphe 2010–2023 ; seuls les "
            "transferts dont les deux clubs ont une valeur > 0 sont comparés."
        ),
        "",
        "## Saison = année du transfert",
        "",
        md_table(summary(same, len(transfers)), floatfmt=".3f"),
        "",
        "## Robustesse : saison précédente",
        "",
        md_table(summary(previous, len(transfers)), floatfmt=".3f"),
        "",
        "Figure : `results/figures/value_ratio.pdf`.",
    ]
    write_report("hierarchy", lines)


if __name__ == "__main__":
    main()
