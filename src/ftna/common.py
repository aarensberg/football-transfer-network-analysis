"""Outils partagés par les analyses : chemins de sortie, tableaux Markdown, style des figures."""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # rendu sans affichage (scripts en ligne de commande)

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from ftna.data import PROJECT_ROOT
from ftna.graph import load_graph

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"

SEED = 42

# Palette catégorielle validée (trois premiers emplacements, sûrs pour les daltoniens
# en toutes paires) et encres de texte ; voir le skill dataviz, palette de référence.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a")
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
NEUTRAL = "#a3a29c"


def main_graph(exclude_youth: bool = False) -> nx.DiGraph:
    """Graphe principal, éventuellement sans équipes de jeunes et réserves."""
    graph = load_graph()
    if exclude_youth:
        keep = [n for n, y in graph.nodes(data="youth_or_reserve") if not y]
        graph = graph.subgraph(keep).copy()
    return graph


def club_label(graph: nx.DiGraph, node: int) -> str:
    """Nom du club suivi de son pays, pour les tableaux."""
    data = graph.nodes[node]
    return f"{data['name']} ({data['country'] or '?'})"


def md_table(df: pd.DataFrame, floatfmt: str = ".3g") -> str:
    """Tableau Markdown simple (évite une dépendance à `tabulate`)."""

    def fmt(value: object) -> str:
        if isinstance(value, float):
            return "" if math.isnan(value) else format(value, floatfmt)  # NaN → vide
        if isinstance(value, int) and not isinstance(value, bool):
            return f"{value:,}"
        return str(value)

    header = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    rows = [
        "| " + " | ".join(fmt(v) for v in row) + " |"
        for row in df.itertuples(index=False)
    ]
    return "\n".join([header, sep, *rows])


def write_report(name: str, lines: list[str]) -> Path:
    """Écrit `results/<name>.md` et l'affiche."""
    path = RESULTS_DIR / f"{name}.md"
    text = "\n".join(lines).rstrip() + "\n"
    path.write_text(text, encoding="utf-8")
    print(text)
    return path


def save_table(df: pd.DataFrame, name: str) -> Path:
    """Sauvegarde un tableau complet en CSV dans `results/tables/`."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = TABLES_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def setup_style() -> None:
    """Style sobre : marques fines, grille et axes discrets, texte en encre neutre."""
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.edgecolor": NEUTRAL,
            "axes.labelcolor": TEXT_SECONDARY,
            "axes.titlecolor": TEXT_PRIMARY,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": TEXT_SECONDARY,
            "ytick.color": TEXT_SECONDARY,
            "legend.frameon": False,
            "lines.linewidth": 2,
            "axes.prop_cycle": plt.cycler(color=list(SERIES)),
        }
    )


def save_figure(fig: plt.Figure, name: str) -> Path:
    """Sauvegarde en PDF (rapport LaTeX) et PNG (aperçu) dans `results/figures/`."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.pdf")
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    return path
