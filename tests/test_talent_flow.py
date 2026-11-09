"""Tests des tableaux du rapport `ftna.talent_flow` sur données synthétiques."""

import networkx as nx
import pandas as pd
from conftest import frame

from ftna.talent_flow import Clubs, competitors


def test_competitors_count_permanent_moves_only():
    graph = nx.DiGraph()
    graph.add_node(1, country="France", youth_or_reserve=True)
    graph.add_node(2, country="Belgium", youth_or_reserve=False)
    transfers = frame(
        [
            (5, 2012, 1, 2, 0, "Not loan"),
            (6, 2012, 1, 2, 0, "Loan"),  # un prêt n'est pas un recrutement
            (7, 2018, 1, 2, 0, "Unknown"),
        ]
    )
    clubs = Clubs(pd.DataFrame({"id": [1, 2], "club_name": ["A U19", "B"]}), graph)
    by_country, _ = competitors(transfers, graph, clubs)
    row = by_country.set_index("pays").loc["Belgium"]
    assert (row["2010–2016"], row["2017–2023"], row["total"]) == (1, 1, 2)
