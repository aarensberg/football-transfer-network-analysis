# Football Transfer Network Analysis

Graph analytics project (2026). We model football player transfers as a directed network of clubs and study which clubs are the most central and which groups of clubs exchange players mainly among themselves.

## Authors

- Alessandro ARENSBERG
- Charles DEFOSSEUX
- Louis ALLIO

Repository: <https://github.com/aarensberg/football-transfer-network-analysis>

## Research question

> Which clubs occupy the most central positions in the football transfer network observed in this dataset, and which communities of clubs mainly exchange players with each other?

## Graph model

- **Nodes**: football clubs described in `clubs.csv` that take part in at least one retained transfer. Attributes: `name`, `country` and `league` (league of the most recent season up to 2023 in `club_league.csv`), `current_mv`, `youth_or_reserve` (name-based heuristic flag).
- **Edges**: an edge u → v exists if at least one player moved from club u (departure) to club v (arrival). Attributes: `weight` (number of transfers), `total_fee` (EUR, mostly 0), `n_permanent`, `n_loan`, `n_unknown`.
- **Graph type**: directed, simple, weighted, without self-loops (`networkx.DiGraph`). Transfer fees are not used as weights because 98% of them are 0 (free transfer or undisclosed fee).
- **Filters**: seasons 2010–2023; `End of loan` rows excluded (mechanical return of a loan); placeholder clubs excluded (`-5` retired, `75` unknown, `515` without club); both clubs must be described in `clubs.csv`; self-loops removed.
- **Result**: 12,009 nodes and 450,217 edges built from 920,304 transfers (see `results/graph_summary.md`).

The results describe the network observed in this dataset, not the entire worldwide transfer market.

## Data

Source: [Soccer Player Transfer Dataset](https://www.kaggle.com/datasets/otaviofbrito/soccer-player-transfer-dataset) (Kaggle, Otavio Brito). The author describes how the dataset was built in [this blog post](https://otaviofbrito.github.io/posts/soccer-player-transfer-dataset/).

According to the author, the data were scraped from [Transfermarkt](https://www.transfermarkt.com) with custom Scrapy spiders (Python) starting from four continental entry points (Europe, Asia, America, Africa). The author reports more than 3 million transfer records, more than 12,000 clubs and 108 countries, covering 1870 to 2024. These figures are the author's. Our own inspection (`results/data_inspection.md`) confirms the orders of magnitude: 3,469,314 transfer rows, 12,963 described clubs, 475 leagues in 111 countries. It also shows that the transfers reference 75,177 club identifiers, of which only 12,726 are described in `clubs.csv`, that about 20% of rows involve placeholder clubs (retired, unknown, without club), and that `transfer_fee` is in euros but zero for 98% of rows (free transfer or undisclosed fee). Transfer volume is much higher in recent years, so the network observed is the one recorded by Transfermarkt and this scraper, not the entire worldwide transfer market. The author does not document the encoding of `transfer_fee` and `transfer_type`; our interpretation, inferred from the data, is given in `results/data_inspection.md`.

The files are too large to be stored on GitHub (`data/` is git-ignored). To reproduce the analysis, download the dataset from the Kaggle link above and place the following files, unmodified, in `data/raw/`:

```text
data/raw
├── club_league.csv
├── clubs.csv
├── leagues.csv
├── players.csv
└── transfers.csv
```

## Setup

The project uses [uv](https://docs.astral.sh/uv/) and requires Python 3.14 or later.

```bash
git clone https://github.com/aarensberg/football-transfer-network-analysis.git
cd football-transfer-network-analysis
uv sync
```

Software: Python 3.14, pandas, NetworkX 3.7, SciPy (sparse shortest paths, required by `nx.pagerank`) and Matplotlib (figures). Random seed: 42.

## Running the analysis

Run the whole pipeline (about 30 minutes, 20 of which for the sensitivity analysis):

```bash
uv run ftna
```

Or run each step separately, in this order (each step writes a Markdown report in `results/`):

| Step | Command | Output | Content |
|---|---|---|---|
| Inspection | `uv run python -m ftna.inspection` | `data_inspection.md` | Data profiling, key integrity, coding of `transfer_type` and `transfer_fee` |
| Graph | `uv run python -m ftna.graph` | `graph_summary.md`, `data/processed/transfer_network.graphml` | Filtering funnel and graph construction |
| Structure | `uv run python -m ftna.structure` | `structure.md` | Degree/strength distributions, reciprocity, clustering vs random baselines, assortativity |
| Connectivity | `uv run python -m ftna.connectivity` | `connectivity.md` | Weakly/strongly connected components, bow-tie decomposition |
| Distances | `uv run python -m ftna.distances` | `distances.md` | Exact diameter, radius, center, periphery and distance distribution |
| Centrality | `uv run python -m ftna.centrality` | `centrality.md`, `tables/centrality.csv` | Degree, strength, PageRank, reverse PageRank, exact closeness and betweenness |
| Communities | `uv run python -m ftna.communities` | `communities.md`, `tables/communities.csv` | Louvain, robustness (seeds, resolution, Leiden, directed), comparison with countries |
| Countries | `uv run python -m ftna.countries` | `countries.md`, `tables/country_flows.csv` | Country-level flows, net exporters/importers, corridors |
| Hierarchy | `uv run python -m ftna.hierarchy` | `hierarchy.md` | Direction of transfers relative to club market value |
| Roles | `uv run python -m ftna.roles` | `roles.md`, `tables/roles.csv` | Participation coefficient and within-community z-score |
| Sensitivity | `uv run python -m ftna.sensitivity` | `sensitivity.md` | Variants without youth teams, by sub-period, by transfer type |

Figures are saved in `results/figures/` as PDF (report) and PNG (preview).

### Conventions

- Distances are counted in hops (edge weights measure exchange intensity, not length). Directed distances are computed exactly on the largest strongly connected component; undirected distances on the largest weakly connected component.
- PageRank uses α = 0.85 and the transfer count as weight; reverse PageRank runs on the transposed graph.
- Betweenness is exact (unweighted) on the main graph, computed in parallel by source batches; sensitivity variants use a 1,000-source approximation.
- Communities: Louvain on the undirected graph whose weight sums both directions, resolution 1.

## Key results

All figures below come from the reports in `results/` (main graph: 2010–2023, 12,009 clubs, 450,217 directed edges, 920,304 transfers).

- **Structure**: no scale-free hubs (activity is capped by squad size), strong reciprocity (41% of edges vs 0.3% at random), very high clustering (0.34 vs 0.015 for a degree-preserving random graph) and positive degree assortativity (0.49).
- **Connectivity**: not connected; 6 weakly connected components (the largest holds 99.9% of clubs) and 404 strongly connected components (the largest holds 96.6% of clubs and 99.7% of transfers).
- **Distances** (hops, exact): diameter 12 and radius 6 on the largest strongly connected component (directed); diameter 10 and radius 5 on the largest weakly connected component (undirected); mean distance 3.65 (directed), i.e. a small world.
- **Centrality** is multidimensional: Italian and Brazilian clubs lead by volume (Parma: 926 outgoing transfers); Balkan and Eastern Mediterranean clubs lead closeness (Hajduk Split, Dinamo Zagreb, Red Star, Olympiacos); mid-tier clubs bridging sub-markets lead betweenness; PageRank points to end-of-career destinations, not prestige (Spearman 0.03 with market value).
- **Hierarchy**: 85% of loans go to a less valuable club, 65% of paid transfers go to a more valuable club: players are loaned down and bought up.
- **Communities**: 35 Louvain communities, modularity 0.836, robust to seeds, Leiden, edge direction and resolution. They are national markets merged into regional blocs that follow language and history (Brazil–Portugal, France–Belgium–Netherlands, post-Soviet, former Yugoslavia, Scandinavia, British Isles…). 85% of transfers are domestic.
- **Bridges between blocs**: Benfica, Sporting CP, Red Bull Salzburg, Manchester City, Chelsea, Olympiacos, Dynamo Kyiv, FC Basel (highest participation coefficients).
- **Robustness**: removing youth/reserve teams, splitting the period, dropping `Unknown` transfers or adding `End of loan` rows keeps communities (NMI ≥ 0.92) and centrality rankings (Spearman ≥ 0.78) stable; only the exact top ranks of PageRank and betweenness move.

Limitations: only clubs described in `clubs.csv` are kept (Transfermarkt coverage, very deep for German-speaking amateur leagues); 98% of transfer fees are zero or undisclosed; youth/reserve teams are detected with a name-based heuristic.

## Repository structure

```text
.
├── data/raw/            # Raw Kaggle CSV files (not versioned)
├── data/processed/      # Generated graph (not versioned)
├── report/              # LaTeX report (template.tex, biblio.bib)
├── results/             # Generated reports, tables (tables/) and figures (figures/)
├── src/ftna/            # Analysis code (one module per step, see table above)
├── pyproject.toml       # Project metadata and dependencies
└── README.md
```

## Code reuse

No existing code for this dataset has been reused so far. This section will be updated if that changes, with proper citations.

## Use of AI tools

To be completed.
