# Inspection des données brutes

Généré par `uv run python -m ftna.inspection` à partir de `data/raw/`.

## 1. Tables

| Table | Lignes | Colonnes | Cellules manquantes |
|---|---:|---:|---:|
| transfers | 3,469,314 | 6 | 0 |
| clubs | 12,963 | 5 | 6,405 |
| leagues | 475 | 5 | 0 |
| club_league | 127,980 | 5 | 0 |
| players | 858,947 | 3 | 308,333 |

- `clubs.id_current_league` manquant : 6,405 clubs.

## 2. Période

- Années : 1870 à 2027.
- 1992 : 19,975 transferts ; 2023 : 202,275.
- 2024 (année incomplète) : 64,753 ; années > 2024 : 186 lignes.
- Part des transferts depuis 2000 : 83.4 %.

| Décennie | Transferts |
|---|---:|
| 1870 | 19 |
| 1880 | 86 |
| 1890 | 185 |
| 1900 | 1,097 |
| 1910 | 2,382 |
| 1920 | 7,664 |
| 1930 | 17,317 |
| 1940 | 20,012 |
| 1950 | 33,791 |
| 1960 | 55,944 |
| 1970 | 77,311 |
| 1980 | 118,510 |
| 1990 | 240,220 |
| 2000 | 592,426 |
| 2010 | 1,457,448 |
| 2020 | 844,902 |

## 3. Clubs et intégrité des clés

- Clubs dans `clubs.csv` : 12,963 (identifiants uniques : True).
- Identifiants de clubs distincts dans `transfers.csv` : 75,177.
- Dont présents dans `clubs.csv` : 12,726 ; clubs de `clubs.csv` jamais impliqués : 237.
- Clubs réels (hors pseudo-clubs) sans fiche dans `clubs.csv` : 62,450, degré médian 6 contre 281 pour les clubs décrits ; ils représentent 18.9 % des extrémités de transferts réels.
- Noms de clubs non uniques : 11 doublons (clubs homonymes distincts, ex. Arsenal FC anglais et argentin) : il faut identifier les clubs par `id`.
- Noms de clubs signalant un club disparu, « (-AAAA) » : 250.

### Pseudo-clubs

| id | Nom dans `clubs.csv` | Départs | Arrivées |
|---:|---|---:|---:|
| -5 | Retired | 14,636 | 201,836 |
| 75 | Unknown | 110,580 | 116,116 |
| 515 | (absent) | 82,710 | 166,479 |

- `515` : absent de `clubs.csv`, club actuel de 91,412 joueurs, type « Unknown » dans 98.0 % des cas : interprété comme « sans club » (joueur libre).
- Lignes impliquant au moins un pseudo-club : 692,357 (20.0 %).

## 4. Types de transfert et montants

| transfer_type | Lignes | Part | Montant = 0 | Montant > 0 | Médiane (> 0, €) |
|---|---:|---:|---:|---:|---:|
| Unknown | 1,755,475 | 50.6 % | 1,755,475 | 0 |  |
| Not loan | 1,370,051 | 39.5 % | 1,316,351 | 53,700 | 500,000 |
| Loan | 228,756 | 6.6 % | 223,701 | 5,055 | 225,000 |
| End of loan | 115,032 | 3.3 % | 115,032 | 0 |  |

Part de chaque type par décennie (depuis 1950) :

| Décennie | End of loan | Loan | Not loan | Unknown |
|---|---:|---:|---:|---:|
| 1950 | 0.2 % | 0.9 % | 8.9 % | 89.9 % |
| 1960 | 0.3 % | 0.9 % | 10.5 % | 88.3 % |
| 1970 | 0.6 % | 1.4 % | 8.7 % | 89.2 % |
| 1980 | 0.8 % | 2.1 % | 12.0 % | 85.0 % |
| 1990 | 1.7 % | 4.3 % | 19.5 % | 74.4 % |
| 2000 | 3.1 % | 6.9 % | 36.0 % | 53.9 % |
| 2010 | 3.7 % | 7.6 % | 45.9 % | 42.7 % |
| 2020 | 4.2 % | 7.2 % | 48.3 % | 40.2 % |

- Montants strictement positifs : 58,755 lignes (1.7 %).
- Montant maximal : 222,000,000 ; les plus gros montants correspondent aux records connus en euros (tableau ci-dessous) : unité = euro.
- Montant 0 : transfert libre **ou** montant inconnu, indiscernables.

Trois plus gros montants :

| Joueur | Année | Départ | Arrivée | Montant (€) |
|---|---:|---|---|---:|
| Neymar | 2017 | FC Barcelona | Paris Saint-Germain | 222,000,000 |
| Kylian Mbappé | 2018 | AS Monaco | Paris Saint-Germain | 180,000,000 |
| Philippe Coutinho | 2017 | Liverpool FC | FC Barcelona | 135,000,000 |

## 5. Cohérence

- Lignes strictement dupliquées : 0 ; doublons (joueur, année, départ, arrivée) : 0.
- Boucles (départ = arrivée) : 8.
- Fichier trié par joueur puis année : True.
- Chaîne de carrière cohérente (club de départ = club d'arrivée précédent) : 74.0 % (écarts dus aux prêts, à l'ordre intra-annuel et aux lacunes).
- Joueurs distincts dans les transferts : 793,947 ; absents de `players.csv` : 9,079 ; `players.csv` : 858,947 lignes.
- Clubs au nom de jeune/réserve (heuristique) : 1,684 ; transferts réels les impliquant : 393,571 (14.2 % des transferts entre clubs réels).
- `club_league` : 3,215 couples (club, saison) en double (Apertura/Clausura, deux divisions la même saison) → une jointure sur (club, saison) multiplie les lignes.
- `club_league` : 323 clubs absents de `clubs.csv`.
- `leagues` : 475 ligues, 111 pays.
