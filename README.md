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

According to the author, the data were scraped from [Transfermarkt](https://www.transfermarkt.com) with custom Scrapy spiders (Python) starting from four continental entry points (Europe, Asia, America, Africa). The author reports more than 3 million transfer records, more than 12,000 clubs and 108 countries, covering 1870 to 2024. These figures are the author's. Our own inspection (`results/data_inspection.md`) confirms the orders of magnitude: 3,469,314 transfer rows, 12,963 described clubs, 475 leagues in 111 countries. It also shows that the transfers reference 75,177 club identifiers, of which only 12,726 are described in `clubs.csv`, that about 20% of rows involve placeholder clubs (retired, unknown, without club), and that `transfer_fee` is in euros but zero for 98% of rows (free transfer or undisclosed fee). Transfer volume is much higher in recent years, so the network observed is the one recorded by Transfermarkt and this scraper, not the entire worldwide transfer market. The author does not document the encoding of `transfer_fee` and `transfer_type`, which we will have to infer from the data.

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

Software: Python, pandas and NetworkX.

## Running the analysis

```bash
uv run python -m ftna.inspection   # data inspection report -> results/data_inspection.md
uv run python -m ftna.graph        # build the graph -> data/processed/transfer_network.graphml, results/graph_summary.md
```

Further steps will be added as the code is written.

## Repository structure

```text
.
├── data/raw/            # Raw Kaggle CSV files (not versioned)
├── data/processed/      # Generated graph (not versioned)
├── report/              # LaTeX report (template.tex, biblio.bib)
├── results/             # Generated reports and figures
├── src/ftna/            # Analysis code (data loading, inspection, graph construction)
├── pyproject.toml       # Project metadata and dependencies
└── README.md
```

## Code reuse

No existing code for this dataset has been reused so far. This section will be updated if that changes, with proper citations.

## Use of AI tools

To be completed.
