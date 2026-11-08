# Football Transfer Network Analysis

Graph analytics project (2026). We model football player transfers as a directed network of clubs and study which clubs are the most central and which groups of clubs exchange players mainly among themselves.

## Authors

- Alessandro ARENSBERG
- Charles DEFOSSEUX
- Louis ALLIO

Repository: <https://github.com/aarensberg/football-transfer-network-analysis>

## Research question

> Which clubs occupy the most central positions in the football transfer network observed in this dataset, and which communities of clubs mainly exchange players with each other?

## Graph model (preliminary)

- **Nodes**: football clubs.
- **Edges**: player transfers, directed from the selling (departure) club to the buying (arrival) club.
- Attributes, weights, graph type (simple graph or multigraph) and filtering rules are still to be defined and will be documented here once validated.

The results describe the network observed in this dataset, not the entire worldwide transfer market.

## Data

Source: [Soccer Player Transfer Dataset](https://www.kaggle.com/datasets/otaviofbrito/soccer-player-transfer-dataset) (Kaggle, Otavio Brito). The author describes how the dataset was built in [this blog post](https://otaviofbrito.github.io/posts/soccer-player-transfer-dataset/).

According to the author, the data were scraped from [Transfermarkt](https://www.transfermarkt.com) with custom Scrapy spiders (Python) starting from four continental entry points (Europe, Asia, America, Africa). The author reports more than 3 million transfer records, more than 12,000 clubs and 108 countries, covering 1870 to 2024. These figures are the author's; they have not yet been checked against the files used here. Transfer volume is much higher in recent years, so the network observed is the one recorded by Transfermarkt and this scraper, not the entire worldwide transfer market. The author does not document the encoding of `transfer_fee` and `transfer_type`, which we will have to infer from the data.

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

Software: Python and NetworkX. Detailed run instructions will be added as the code is written.

## Repository structure

```text
.
├── data/raw/            # Raw Kaggle CSV files (not versioned)
├── report/              # LaTeX report (template.tex, biblio.bib)
├── src/                 # Analysis code
├── pyproject.toml       # Project metadata and dependencies
└── README.md
```

## Code reuse

No existing code for this dataset has been reused so far. This section will be updated if that changes, with proper citations.

## Use of AI tools

To be completed.
