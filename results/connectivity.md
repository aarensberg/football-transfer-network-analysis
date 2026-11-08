# A2. Connectivité

Généré par `uv run python -m ftna.connectivity`.

- Graphe faiblement connexe : False ; fortement connexe : False.

## Composantes faiblement connexes (CFF)

- Nombre : 6 ; plus grande : 11,999 nœuds (99.92%).
- Petites CFF :
  - Ryutsu Keizai Dragons Ryugasaki (Japan), Ryutsu Keizai University FC (Japan)
  - Jogeva SK Noorus 96 U19 (Estonia), FC Helios Tartu/Jogeva SK Noorus 96 U19 (Estonia)
  - Niigata Univ. of Management FC (Japan), Niigata Univ. of Management '09 Keidai (Japan)
  - Hokuriku University FC (Japan), Hokuriku University FC Futures (-2020) (Japan)
  - Chukyo University FC (I) (Japan), Chukyo univ.FC (II) (Japan)

## Composantes fortement connexes (CFC)

- Nombre : 404 ; plus grande : 11,598 nœuds (96.58%), 448,881 arêtes, 99.65% des transferts.
- CFC de taille 1 : 396 ; deuxième plus grande : 3 nœuds.

| taille | nombre de composantes |
|---|---|
| 11,598 | 1 |
| 3 | 1 |
| 2 | 6 |
| 1 | 396 |

## Décomposition bow-tie autour de la CFC géante

| partie | clubs | part des nœuds | degré total moyen | part jeunes/réserves | pays principaux |
|---|---|---|---|---|---|
| CFC géante | 11,598 | 0.966 | 77.5 | 0.123 | Germany (2206), Italy (764), Austria (674) |
| IN | 259 | 0.0216 | 3.96 | 0.432 | Japan (76), Estonia (20), Germany (17) |
| OUT | 138 | 0.0115 | 2.51 | 0.145 | Japan (24), Germany (15), Türkiye (12) |
| Autres | 14 | 0.00117 | 1.71 | 0.286 | Japan (11), Estonia (2), France (1) |
