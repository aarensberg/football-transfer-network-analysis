"""Analyse du réseau des transferts de football (Graph analytics 2026)."""

import importlib
import time

# Étapes dans l'ordre de dépendance (communities avant roles, centrality avant roles).
STEPS = (
    "inspection",
    "graph",
    "structure",
    "connectivity",
    "distances",
    "centrality",
    "communities",
    "countries",
    "hierarchy",
    "roles",
    "sensitivity",
)


def main() -> None:
    """Exécute tout le pipeline : `uv run ftna` (~18 min, dont ~7 pour la sensibilité)."""
    for step in STEPS:
        start = time.perf_counter()
        print(f"=== ftna.{step}", flush=True)
        importlib.import_module(f"ftna.{step}").main()
        print(f"=== ftna.{step} : {time.perf_counter() - start:.0f} s", flush=True)
