# Réseau des transferts : construction

Généré par `uv run python -m ftna.graph` à partir de `data/raw/`.

## Filtrage

| Étape | Lignes restantes |
|---|---:|
| Lignes brutes | 3,469,314 |
| Années 2010–2023 | 2,237,411 |
| Types exclus : End of loan | 2,150,643 |
| Sans pseudo-clubs (-5, 75, 515) | 1,722,261 |
| Deux clubs décrits dans clubs.csv | 920,310 |
| Sans boucles | 920,304 |

## Graphe

- Type : orienté, simple (une arête par couple ordonné de clubs), pondéré (`weight` = nombre de transferts), sans boucle.
- Nœuds (clubs) : 12,009
- Arêtes (couples orientés distincts) : 450,217
- Somme des poids (= transferts retenus) : 920,304
- Densité : 3.12e-03
- Part des arêtes réciproques (u→v et v→u) : 41.2%
- Poids : médiane 1, moyenne 2.04, max 225 ; arêtes de poids 1 : 64.0%
- Clubs sans pays identifié : 68
- Pays représentés : 110
- Équipes de jeunes/réserves (heuristique, attribut `youth_or_reserve`) : 1,567 nœuds, 17.3% du poids total (arêtes touchant au moins une de ces équipes)

## Arêtes les plus lourdes

| Départ | Arrivée | Transferts | dont prêts |
|---|---|---:|---:|
| Hertha BSC U17 | Hertha BSC U19 | 225 | 0 |
| TSV 1860 München U17 | TSV 1860 München U19 | 221 | 0 |
| AKA Tirol U16 | AKA Tirol U18 | 219 | 0 |
| AKA Burgenland U16 | AKA Burgenland U18 | 215 | 0 |
| FC Bayern Munich U17 | FC Bayern Munich U19 | 208 | 0 |
| Akademia FK Krasnodar | FK Krasnodar II | 208 | 0 |
| Borussia Mönchengladbach U17 | Borussia Mönchengladbach U19 | 207 | 0 |
| Karlsruher SC U17 | Karlsruher SC U19 | 200 | 0 |
| AKA Steiermark - Sturm Graz U16 | AKA Steiermark - Sturm Graz U18 | 199 | 0 |
| 1.FSV Mainz 05 U17 | 1.FSV Mainz 05 U19 | 197 | 0 |

## Clubs par pays (15 premiers)

| Pays | Clubs |
|---|---:|
| Germany | 2,238 |
| Italy | 769 |
| Austria | 688 |
| France | 499 |
| Türkiye | 387 |
| Japan | 342 |
| Switzerland | 318 |
| Finland | 301 |
| England | 273 |
| Spain | 268 |
| Poland | 266 |
| Russia | 219 |
| Norway | 179 |
| Brazil | 179 |
| Belgium | 167 |

Paramètres : GraphConfig(start_year=2010, end_year=2023, excluded_types=('End of loan',)).
