# A3. Distances

Généré par `uv run python -m ftna.distances`. Distances en nombre de sauts, calcul exact (BFS depuis chaque nœud). Orienté : plus grande CFC (toutes distances finies) ; non orienté : plus grande CFF.

| graphe | nœuds | diamètre | rayon | distance moyenne | distance médiane |
|---|---|---|---|---|---|
| orienté, CFC géante (excentricité sortante) | 11,598 | 12 | 6 | 3.65 | 4 |
| orienté, CFC géante (excentricité entrante) | 11,598 | 12 | 6 | 3.65 | 4 |
| non orienté, CFF géante | 11,999 | 10 | 5 | 3.28 | 3 |

Référence aléatoire (non orienté, même n = 11,999 et degré moyen 59.6) : ln(n)/ln(<k>) ≈ 2.30.

## Distribution des distances

| distance | orienté (part) | non orienté (part) |
|---|---|---|
| 1 | 0.0033 | 0.0050 |
| 2 | 0.0633 | 0.1138 |
| 3 | 0.3675 | 0.5204 |
| 4 | 0.4305 | 0.3205 |
| 5 | 0.1184 | 0.0372 |
| 6 | 0.0143 | 0.0025 |
| 7 | 0.0022 | 0.0004 |
| 8 | 0.0005 | 0.0001 |
| 9 | 0.0001 | 0.0000 |
| 10 | 0.0000 | 0.0000 |
| 11 | 0.0000 | 0.0000 |
| 12 | 0.0000 | 0.0000 |

Figure : `results/figures/distance_distribution.pdf`.

## Centre et périphérie

- Centre orienté (excentricité sortante = rayon 6) : 7 clubs : FK Spartaks Jurmala (Latvia), LOSC Lille B (France), Paris Saint-Germain B (France), FC Flora Tallinn (Estonia), Egersunds IK (Norway), UMF Víkingur Ólafsvík (Iceland), Nybergsund (Norway)
- Centre orienté (excentricité entrante = rayon 6) : 418 clubs : Tombense Futebol Clube (MG) (Brazil), ABC Futebol Clube (RN) (Brazil), NK Lokomotiva Zagreb (Croatia), Club Athletico Paranaense (Brazil), Asociación Deportivo Pasto (Colombia), HNK Hajduk Split (Croatia), FK Rad (Serbia), HSK Zrinjski Mostar (Bosnia-Herzegovina), Jagiellonia Bialystok (Poland), EC Santo André (Brazil) …
- Périphérie orientée (excentricité sortante = diamètre 12) : 2 clubs : Eveil FC (Kobe) (Japan), Nakaniida SC (Japan)
- Périphérie orientée (excentricité entrante = diamètre 12) : 1 clubs : Le Puy Foot 43 Auvergne U19 (France)
- Centre non orienté (rayon 5) : 14 clubs : FC Gifu (Japan), SC Sagamihara (Japan), V-Varen Nagasaki (Japan), Machida Zelvia (Japan), Fujieda MYFC (Japan), Ventforet Kofu (Japan), Sanfrecce Hiroshima (Japan), FC Osaka (Japan), FK Auda (Latvia), Tochigi City (Japan) …
- Périphérie non orientée (diamètre 10) : 3 clubs : Parafrente Yonezawa (Japan), Nagai Club (Japan), Viimsi JK U17 (Estonia)
