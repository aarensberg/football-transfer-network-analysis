"""Inspection des données brutes : effectifs, intégrité des clés, codage des variables.

Usage : `uv run python -m ftna.inspection`
Écrit un rapport Markdown dans `results/data_inspection.md` et l'affiche.
"""

import pandas as pd

from ftna.data import (
    PROJECT_ROOT,
    PSEUDO_CLUB_IDS,
    WITHOUT_CLUB_ID,
    YOUTH_RESERVE_PATTERN,
    RawData,
    load_raw,
)

OUTPUT_PATH = PROJECT_ROOT / "results" / "data_inspection.md"


def _fmt(n: float) -> str:
    """Formate un entier avec séparateur de milliers."""
    return f"{n:,.0f}"


def _pct(part: float, total: float) -> str:
    return f"{100 * part / total:.1f} %"


def table_overview(raw: RawData) -> list[str]:
    """Dimensions et valeurs manquantes de chaque table."""
    lines = [
        "## 1. Tables",
        "",
        "| Table | Lignes | Colonnes | Cellules manquantes |",
        "|---|---:|---:|---:|",
    ]
    for name in ("transfers", "clubs", "leagues", "club_league", "players"):
        df: pd.DataFrame = getattr(raw, name)
        lines.append(
            f"| {name} | {_fmt(len(df))} | {df.shape[1]} | {_fmt(df.isna().sum().sum())} |"
        )
    missing = raw.clubs.isna().sum()
    lines += [
        "",
        f"- `clubs.id_current_league` manquant : {_fmt(missing['id_current_league'])} clubs.",
    ]
    return lines


def period(t: pd.DataFrame) -> list[str]:
    """Couverture temporelle des transferts."""
    by_year = t.year.value_counts().sort_index()
    by_decade = t.groupby(t.year // 10 * 10).size()
    lines = [
        "## 2. Période",
        "",
        f"- Années : {t.year.min()} à {t.year.max()}.",
        f"- 1992 : {_fmt(by_year.get(1992, 0))} transferts ; 2023 : {_fmt(by_year.get(2023, 0))}.",
        (
            f"- 2024 (année incomplète) : {_fmt(by_year.get(2024, 0))} ; "
            f"années > 2024 : {_fmt(by_year[by_year.index > 2024].sum())} lignes."
        ),
        f"- Part des transferts depuis 2000 : {_pct(by_year[by_year.index >= 2000].sum(), len(t))}.",
        "",
        "| Décennie | Transferts |",
        "|---|---:|",
    ]
    lines += [f"| {d} | {_fmt(n)} |" for d, n in by_decade.items()]
    return lines


def key_integrity(raw: RawData) -> list[str]:
    """Correspondance entre identifiants de clubs des transferts et `clubs.csv`."""
    t, clubs = raw.transfers, raw.clubs
    known = set(clubs.id)
    endpoints = pd.concat([t.left_club_id, t.joined_club_id])
    involvement = endpoints.value_counts()
    real = involvement[~involvement.index.isin(list(PSEUDO_CLUB_IDS))]
    named = real.index.isin(list(known))

    lines = [
        "## 3. Clubs et intégrité des clés",
        "",
        f"- Clubs dans `clubs.csv` : {_fmt(len(clubs))} (identifiants uniques : {clubs.id.is_unique}).",
        f"- Identifiants de clubs distincts dans `transfers.csv` : {_fmt(endpoints.nunique())}.",
        (
            f"- Dont présents dans `clubs.csv` : {_fmt(len(set(endpoints) & known))} ; "
            f"clubs de `clubs.csv` jamais impliqués : {_fmt(len(known - set(endpoints)))}."
        ),
        (
            f"- Clubs réels (hors pseudo-clubs) sans fiche dans `clubs.csv` : {_fmt((~named).sum())}, "
            f"degré médian {real[~named].median():.0f} contre {real[named].median():.0f} pour les clubs décrits ; "
            f"ils représentent {_pct(real[~named].sum(), real.sum())} des extrémités de transferts réels."
        ),
        (
            f"- Noms de clubs non uniques : {_fmt(clubs.club_name.duplicated().sum())} doublons "
            "(clubs homonymes distincts, ex. Arsenal FC anglais et argentin) : il faut identifier les clubs par `id`."
        ),
        f"- Noms de clubs signalant un club disparu, « (-AAAA) » : {_fmt(clubs.club_name.str.contains(r'\(-\d{4}\)').sum())}.",
        "",
        "### Pseudo-clubs",
        "",
        "| id | Nom dans `clubs.csv` | Départs | Arrivées |",
        "|---:|---|---:|---:|",
    ]
    names = clubs.set_index("id").club_name
    for cid in sorted(PSEUDO_CLUB_IDS):
        lines.append(
            f"| {cid} | {names.get(cid, '(absent)')} | {_fmt((t.left_club_id == cid).sum())} "
            f"| {_fmt((t.joined_club_id == cid).sum())} |"
        )
    current_515 = (raw.players.current_club_id == WITHOUT_CLUB_ID).sum()
    rows_515 = (t.left_club_id == WITHOUT_CLUB_ID) | (
        t.joined_club_id == WITHOUT_CLUB_ID
    )
    unknown_515 = (t.transfer_type[rows_515] == "Unknown").sum()
    lines += [
        "",
        (
            f"- `{WITHOUT_CLUB_ID}` : absent de `clubs.csv`, club actuel de {_fmt(current_515)} joueurs, "
            f"type « Unknown » dans {_pct(unknown_515, rows_515.sum())} des cas : "
            "interprété comme « sans club » (joueur libre)."
        ),
    ]
    pseudo_rows = t.left_club_id.isin(PSEUDO_CLUB_IDS) | t.joined_club_id.isin(
        PSEUDO_CLUB_IDS
    )
    lines.append(
        f"- Lignes impliquant au moins un pseudo-club : {_fmt(pseudo_rows.sum())} ({_pct(pseudo_rows.sum(), len(t))})."
    )
    return lines


def transfer_coding(raw: RawData) -> list[str]:
    """Codage de `transfer_type` et `transfer_fee`."""
    t = raw.transfers
    club_names = raw.clubs.set_index("id").club_name
    player_names = raw.players.set_index("id").name
    stats = t.groupby("transfer_type").transfer_fee.agg(
        n="size",
        zero=lambda x: (x == 0).sum(),
        positive=lambda x: (x > 0).sum(),
        median_positive=lambda x: x[x > 0].median(),
    )
    lines = [
        "## 4. Types de transfert et montants",
        "",
        "| transfer_type | Lignes | Part | Montant = 0 | Montant > 0 | Médiane (> 0, €) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for ttype, row in stats.sort_values("n", ascending=False).iterrows():
        median = "" if pd.isna(row.median_positive) else _fmt(row.median_positive)
        lines.append(
            f"| {ttype} | {_fmt(row.n)} | {_pct(row.n, len(t))} | {_fmt(row.zero)} | {_fmt(row.positive)} | {median} |"
        )
    share = (
        t.groupby(t.year // 10 * 10)
        .transfer_type.value_counts(normalize=True)
        .unstack(fill_value=0)
    )
    lines += [
        "",
        "Part de chaque type par décennie (depuis 1950) :",
        "",
        "| Décennie | " + " | ".join(share.columns) + " |",
    ]
    lines.append("|---|" + "---:|" * len(share.columns))
    for decade, row in share.loc[1950:].iterrows():
        lines.append(
            f"| {decade} | " + " | ".join(f"{100 * v:.1f} %" for v in row) + " |"
        )
    top = t.nlargest(3, "transfer_fee")
    lines += [
        "",
        f"- Montants strictement positifs : {_fmt((t.transfer_fee > 0).sum())} lignes ({_pct((t.transfer_fee > 0).sum(), len(t))}).",
        (
            f"- Montant maximal : {_fmt(t.transfer_fee.max())} ; les plus gros montants correspondent aux records "
            "connus en euros (tableau ci-dessous) : unité = euro."
        ),
        "- Montant 0 : transfert libre **ou** montant inconnu, indiscernables.",
        "",
        "Trois plus gros montants :",
        "",
        "| Joueur | Année | Départ | Arrivée | Montant (€) |",
        "|---|---:|---|---|---:|",
    ]
    lines += [
        f"| {player_names.get(r.player_id)} | {r.year} | {club_names.get(r.left_club_id)} "
        f"| {club_names.get(r.joined_club_id)} | {_fmt(r.transfer_fee)} |"
        for r in top.itertuples()
    ]
    return lines


def consistency(raw: RawData) -> list[str]:
    """Doublons, boucles, chronologie et jointures à risque."""
    t, clubs, cl = raw.transfers, raw.clubs, raw.club_league
    prev_joined = t.groupby("player_id").joined_club_id.shift()
    chained = prev_joined.notna()
    youth_ids = set(
        clubs.id[clubs.club_name.str.contains(YOUTH_RESERVE_PATTERN, regex=True)]
    )
    real = ~t.left_club_id.isin(PSEUDO_CLUB_IDS) & ~t.joined_club_id.isin(
        PSEUDO_CLUB_IDS
    )
    youth_rows = real & (
        t.left_club_id.isin(youth_ids) | t.joined_club_id.isin(youth_ids)
    )
    players_known = t.player_id.drop_duplicates().isin(set(raw.players.id))
    return [
        "## 5. Cohérence",
        "",
        (
            f"- Lignes strictement dupliquées : {_fmt(t.duplicated().sum())} ; "
            f"doublons (joueur, année, départ, arrivée) : {_fmt(t.duplicated(['player_id', 'year', 'left_club_id', 'joined_club_id']).sum())}."
        ),
        f"- Boucles (départ = arrivée) : {_fmt((t.left_club_id == t.joined_club_id).sum())}.",
        f"- Fichier trié par joueur puis année : {t.player_id.is_monotonic_increasing and (t.groupby('player_id').year.diff().dropna() >= 0).all()}.",
        (
            f"- Chaîne de carrière cohérente (club de départ = club d'arrivée précédent) : "
            f"{_pct((t.left_club_id[chained] == prev_joined[chained]).sum(), chained.sum())} "
            "(écarts dus aux prêts, à l'ordre intra-annuel et aux lacunes)."
        ),
        (
            f"- Joueurs distincts dans les transferts : {_fmt(t.player_id.nunique())} ; "
            f"absents de `players.csv` : {_fmt((~players_known).sum())} ; `players.csv` : {_fmt(len(raw.players))} lignes."
        ),
        (
            f"- Clubs au nom de jeune/réserve (heuristique) : {_fmt(len(youth_ids))} ; transferts réels les impliquant : "
            f"{_fmt(youth_rows.sum())} ({_pct(youth_rows.sum(), real.sum())} des transferts entre clubs réels)."
        ),
        (
            f"- `club_league` : {_fmt(cl.duplicated(['club_id', 'season']).sum())} couples (club, saison) en double "
            "(Apertura/Clausura, deux divisions la même saison) → une jointure sur (club, saison) multiplie les lignes."
        ),
        f"- `club_league` : {_fmt(len(set(cl.club_id) - set(clubs.id)))} clubs absents de `clubs.csv`.",
        f"- `leagues` : {_fmt(len(raw.leagues))} ligues, {_fmt(raw.leagues.country.nunique())} pays.",
    ]


def build_report(raw: RawData) -> str:
    sections = [
        [
            "# Inspection des données brutes",
            "",
            "Généré par `uv run python -m ftna.inspection` à partir de `data/raw/`.",
        ],
        table_overview(raw),
        period(raw.transfers),
        key_integrity(raw),
        transfer_coding(raw),
        consistency(raw),
    ]
    return "\n\n".join("\n".join(s) for s in sections) + "\n"


def main() -> None:
    raw = load_raw(players_columns=["id", "name", "current_club_id"])
    report = build_report(raw)
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
