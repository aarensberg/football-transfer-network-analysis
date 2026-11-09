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

- **Nodes**: football clubs described in `clubs.csv` that take part in at least one retained transfer. Attributes: `name`, `country` and `league` (league of the most recent season up to 2023 in `club_league.csv`), `current_mv`, `youth_or_reserve` (heuristic flag based on the club and league names, e.g. `U19`, `Under 17`, `Primavera`, a trailing `B`/`II`/`2`; manually checked to exclude first teams such as Boca Juniors or Willem II, see `src/ftna/data.py`).
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

Software: Python 3.14, pandas, NetworkX 3.7, SciPy (sparse shortest paths, required by `nx.pagerank`) and Matplotlib (figures); pytest for the unit tests (`uv run pytest`). Random seed: 42.

## Running the analysis

Run the whole pipeline (about 23 minutes, 7 of which for the sensitivity analysis):

```bash
uv run ftna
```

Or run each step separately, in this order (each step writes a Markdown report in `results/`):

| Step | Command | Output | Content |
|---|---|---|---|
| Inspection | `uv run python -m ftna.inspection` | `data_inspection.md` | Data profiling, key integrity, coding of `transfer_type` and `transfer_fee` |
| Graph | `uv run python -m ftna.graph` | `graph_summary.md`, `data/processed/transfer_network.graphml` | Filtering funnel and graph construction |
| Structure | `uv run python -m ftna.structure` | `structure.md` | Degree/strength distributions, reciprocity, clustering vs random baselines, assortativity, k-core decomposition |
| Connectivity | `uv run python -m ftna.connectivity` | `connectivity.md` | Weakly/strongly connected components, bow-tie decomposition, articulation points, bridges, biconnected components |
| Distances | `uv run python -m ftna.distances` | `distances.md` | Exact diameter, radius, center, periphery, distance distribution, small-world comparison with configuration models |
| Centrality | `uv run python -m ftna.centrality` | `centrality.md`, `tables/centrality.csv` | Degree, strength, PageRank, reverse PageRank, exact closeness (largest SCC and Wasserman–Faust), exact betweenness, eigenvector; validation against market value |
| Communities | `uv run python -m ftna.communities` | `communities.md`, `tables/communities.csv` | Louvain and its hierarchy, significance against a null model, robustness (seeds, resolution, Leiden, directed, label propagation), comparison with countries |
| Countries | `uv run python -m ftna.countries` | `countries.md`, `tables/country_flows.csv` | Country-level flows, net exporters/importers, corridors |
| Hierarchy | `uv run python -m ftna.hierarchy` | `hierarchy.md` | Direction of transfers relative to club market value |
| Roles | `uv run python -m ftna.roles` | `roles.md`, `tables/roles.csv`, `tables/edge_betweenness.csv` | Participation coefficient, within-community z-score, exact edge betweenness of inter-community links |
| Talent flow | `uv run python -m ftna.talent_flow` | `talent_flow.md`, `tables/talent_flow_*.csv` | Product for PSG (see below): academy departures and value realized elsewhere, springboard clubs, competitors, comparables |
| Sensitivity | `uv run python -m ftna.sensitivity` | `sensitivity.md` | Variants without youth teams, by sub-period, by transfer type |

Figures are saved in `results/figures/` as PDF (report) and PNG (preview).

### Conventions

- Distances are counted in hops (edge weights measure exchange intensity, not length). Directed distances are computed exactly on the largest strongly connected component; undirected distances on the largest weakly connected component.
- PageRank uses α = 0.85 and the transfer count as weight; reverse PageRank runs on the transposed graph.
- Betweenness (nodes and edges) is exact (unweighted) on the main graph, computed in parallel by source batches; sensitivity variants use a 1,000-source approximation.
- Closeness is reported on the largest strongly connected component and, for all clubs, with the Wasserman–Faust correction for disconnected graphs (the two rankings agree, Spearman 1.00 on the SCC).
- Eigenvector centrality is computed on the largest weakly connected component (undirected, weighted), because the directed graph is not strongly connected.
- Communities: Louvain on the undirected graph whose weight sums both directions, resolution 1. Significance: Louvain on 3 graphs of the weighted configuration model (club strengths preserved, transfers paired at random).
- Small-world baseline: exact distances in configuration models with the same (in/out) degrees, rather than the Erdős–Rényi formula ln n / ln ⟨k⟩, which assumes homogeneous degrees.
- External validation: Spearman correlation with the mean squad market value over the 2010–2023 seasons (`club_league.csv`); the current market value (`clubs.csv`) is also reported.
- The "without youth teams" variant also drops the clubs left isolated by their removal.

## Key results

All figures below come from the reports in `results/` (main graph: 2010–2023, 12,009 clubs, 450,217 directed edges, 920,304 transfers).

- **Structure**: no scale-free hubs (activity is capped by squad size), strong reciprocity (41% of edges vs 0.3% at random), very high clustering (0.34 vs 0.015 for a degree-preserving random graph) and positive degree assortativity (0.49). The densest k-core (k = 76) is the Turkish professional pyramid (139 clubs); the 60-core is mostly Italian, Turkish, English and Brazilian.
- **Connectivity**: not connected; 6 weakly connected components (the largest holds 99.9% of clubs) and 404 strongly connected components (the largest holds 96.6% of clubs and 99.7% of transfers). The largest weakly connected component has 180 articulation points and 181 bridges, but 98.5% of it is biconnected and no club disconnects more than 4 others: no single club is critical.
- **Distances** (hops, exact): diameter 12 and radius 6 on the largest strongly connected component (directed); diameter 10 and radius 5 on the largest weakly connected component (undirected); mean distance 3.65 (directed) and 3.28 (undirected), close to a degree-preserving random graph (2.95 and 2.74) while clustering is 22 times higher: a small world (σ ≈ 19).
- **Centrality** is multidimensional: Italian and Brazilian clubs lead by volume (Parma: 926 outgoing transfers); Balkan and Eastern Mediterranean clubs lead closeness (Hajduk Split, Dinamo Zagreb, Red Star, Olympiacos); mid-tier clubs bridging sub-markets lead betweenness; PageRank points to end-of-career destinations, not prestige (Spearman 0.08 with the 2010–2023 market value, against 0.72 for out-closeness); eigenvector centrality localizes on the Brazilian and Italian loan systems (all of its top 100).
- **Hierarchy**: 85% of loans go to a less valuable club, 65% of paid transfers go to a more valuable club: players are loaned down and bought up.
- **Communities**: 35 Louvain communities, modularity 0.836 (0.063 ± 0.001 for the weighted configuration model), robust to seeds, Leiden, edge direction and resolution; label propagation, which optimizes no objective, finds a finer but consistent partition (NMI 0.78). The Louvain hierarchy shows the nesting: 389 almost purely national groups at the first level (national purity 0.98), merged into transnational blocs from the second level (purity 0.72). They are national markets merged into regional blocs that follow language and history (Brazil–Portugal, France–Belgium–Netherlands, post-Soviet, former Yugoslavia, Scandinavia, British Isles…). 85% of transfers are domestic.
- **Bridges between blocs**: Benfica, Sporting CP, Red Bull Salzburg, Manchester City, Chelsea, Olympiacos, Dynamo Kyiv, FC Basel (highest participation coefficients). 75.5% of the 1,000 edges with the highest edge betweenness link two communities, against 19.7% of all edges.
- **Robustness**: removing youth/reserve teams, splitting the period, dropping `Unknown` transfers or adding `End of loan` rows keeps communities (NMI ≥ 0.92), centrality rankings (Spearman ≥ 0.78) and degree assortativity (0.48–0.52) stable; only the exact top ranks of PageRank and betweenness move.

Limitations: only clubs described in `clubs.csv` are kept (Transfermarkt coverage, very deep for German-speaking amateur leagues); 98% of transfer fees are zero or undisclosed; youth/reserve teams are detected with a name-based heuristic (manually checked, but imperfect).

## Product: Paris Talent Flow

Beyond the course analysis, we built a decision-support tool for the sporting director of Paris Saint-Germain. It answers: *where do the players trained at PSG go, who captures the value they create afterwards, and through which springboard clubs should they be sent (loan, sale with sell-on or buy-back clause) to recover part of it?* The idea was selected from ten recruitment pain points, scored on added value and feasibility with our data. Code: `src/ftna/careers.py`, `src/ftna/springboards.py`, `src/ftna/talent_flow.py`; report: `results/talent_flow.md`.

Method:

- Careers are rebuilt from the raw `transfers.csv`, not from the filtered graph: players enter academies through club identifiers missing from `clubs.csv`.
- A trained player is one whose first move into a youth or reserve team of the academy happened between 2008 and 2019. 15 academies are compared, with their youth teams matched manually.
- A departure is the first non-loan move out of the club (first team and youth teams). Departures up to 2021 are evaluated.
- The value realized afterwards is the highest non-loan fee later paid for the player, excluding moves involving the academy itself, from the departure year up to the year of a first return to the academy (after a buy-back, the career belongs to a new departure). The order of rows within a year is not chronological in the file, so all computations work at the year level.
- Capture ratio = Σ departure fees / Σ highest later fees, with a 95% bootstrap interval.
- The elite is the 20 clubs with the highest squad value each season; "played in the elite" means joining an elite club (loans included) within three years of the departure. A player trained in two academies counts once in pooled analyses.

Key results:

- **Value realized elsewhere**: 239 players trained at PSG, 215 evaluated departures, 91% without a known fee. PSG received €118.7M when they left; the highest fees paid for them afterwards add up to €325.3M. The capture ratio is **0.36** (95% CI [0.23; 0.58], 0.41 without the two largest cases), the lowest of the 15 academies, close to Rennes and Bayern (0.39; the confidence intervals overlap). Ajax, Monaco, Lyon and Benfica are at 1.29–1.36, Real Madrid at 1.17, Juventus at 2.40. Examples: Nkunku (€19.5M to Leipzig, then €60M to Chelsea), Diaby (€15M to Leverkusen, then €60M), Coman (free to Juventus, then €21M to Bayern).
- **Who captures**: RB Leipzig, Lille and Leverkusen as first destinations of PSG alumni. For the six French academies: Monaco, Dortmund and Nice.
- **Bridge clubs**: academy players first sent to a non-elite club with a high participation coefficient (P ≥ 0.6, analysis A10) reach the elite within three years in 5.5% of cases, against 1.2% otherwise, and are later sold for a fee in 48% of cases, against 18%. This is an association, not a causal effect.
- **Springboards**: Southampton, Ajax, Lyon, Lille, Sevilla and Villarreal send about 18–21% of their outgoing players to the elite within two moves and three years. Only 5% of the 7,368 clubs with at least 30 exits sent any player to the elite, with a median rate of 1.3% among them.
- **Competitors**: foreign clubs signing players from French youth teams (loans excluded) are mainly Belgian, then Italian. Italian clubs went from 29 signings (2010–2016) to 94 (2017–2023). Emerging springboards (rise in rate between 2010–2015 and 2016–2020): Southampton, Mönchengladbach, Leicester, Betis, Flamengo, Salzburg.
- **Comparables**: for each position × age at departure, the share later sold for a fee and the distribution of the highest later fee, to set sell-on percentages and buy-back prices.

Limitations: no performance data (minutes, statistics); a zero fee means free or undisclosed; clauses are invisible; only cohorts that left up to 2021 can be evaluated; small numbers, where a dozen players carry most of an academy's value; youth teams are matched manually; there is no birthplace, so regional talent pools cannot be located.

## Repository structure

```text
.
├── data/raw/            # Raw Kaggle CSV files (not versioned)
├── data/processed/      # Generated graph (not versioned)
├── report/              # LaTeX report (template.tex, biblio.bib)
├── results/             # Generated reports, tables (tables/) and figures (figures/)
├── src/ftna/            # Analysis code (one module per step, see table above)
├── tests/               # Unit tests on synthetic data (uv run pytest)
├── pyproject.toml       # Project metadata and dependencies
└── README.md
```

## Code reuse

No existing code for this dataset has been reused so far. This section will be updated if that changes, with proper citations.

## Use of AI tools

To be completed.
