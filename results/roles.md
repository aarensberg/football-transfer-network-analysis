# A10. Rôles des clubs dans les communautés

Généré par `uv run python -m ftna.roles`. Partition Louvain de A5 ; graphe non orienté pondéré. Hubs : z ≥ 2.5. Table complète : `results/tables/roles.csv`.

- P médian : 0.076 ; P médian des clubs actifs (force ≥ 100) : 0.114 ; clubs actifs : 6,506.

## Répartition des rôles

| rôle | clubs |
|---|---|
| R1 ultra-périphérique | 4,705 |
| R2 périphérique | 6,954 |
| R3 connecteur | 183 |
| R4 sans attache | 7 |
| R5 hub provincial | 148 |
| R6 hub connecteur | 12 |

## Clubs passerelles : P le plus élevé parmi les clubs actifs (force ≥ 100)

| name | country | bloc | strength | P | z | role |
|---|---|---|---|---|---|---|
| FC Sheriff Tiraspol | Moldova | C4 Russia / Ukraine | 445.00 | 0.82 | 0.35 | R4 sans attache |
| Sporting CP | Portugal | C18 Brazil / Portugal | 569.00 | 0.81 | -0.06 | R4 sans attache |
| SL Benfica | Portugal | C18 Brazil / Portugal | 645.00 | 0.81 | 0.11 | R4 sans attache |
| Red Bull Salzburg | Austria | C5 Austria | 462.00 | 0.81 | 0.83 | R4 sans attache |
| Manchester City | England | C9 England / Scotland | 458.00 | 0.79 | -0.33 | R3 connecteur |
| Olympiacos Piraeus | Greece | C14 Greece / Bulgaria / Romania | 798.00 | 0.79 | 1.76 | R3 connecteur |
| Chelsea FC | England | C9 England / Scotland | 541.00 | 0.78 | -0.02 | R3 connecteur |
| Dynamo Kyiv | Ukraine | C4 Russia / Ukraine | 351.00 | 0.78 | 0.25 | R3 connecteur |
| FC Basel 1893 | Switzerland | C12 Switzerland | 387.00 | 0.78 | 0.58 | R3 connecteur |
| Panathinaikos FC | Greece | C14 Greece / Bulgaria / Romania | 432.00 | 0.78 | 0.33 | R3 connecteur |
| Vitesse Arnhem | Netherlands | C2 France / Belgium / Netherlands | 307.00 | 0.77 | 0.21 | R3 connecteur |
| FC Copenhagen | Denmark | C8 Norway / Denmark / Sweden | 325.00 | 0.77 | 0.32 | R3 connecteur |
| Olympique Marseille | France | C2 France / Belgium / Netherlands | 360.00 | 0.77 | 0.51 | R3 connecteur |
| York United FC | Canada | C22 United States / Jamaica | 109.00 | 0.77 | -0.44 | R3 connecteur |
| CFR Cluj | Romania | C14 Greece / Bulgaria / Romania | 501.00 | 0.77 | 0.70 | R3 connecteur |
| Sevilla FC | Spain | C16 Spain | 428.00 | 0.76 | 0.21 | R3 connecteur |
| Ludogorets Razgrad | Bulgaria | C14 Greece / Bulgaria / Romania | 302.00 | 0.76 | -0.20 | R3 connecteur |
| Atlético de Madrid | Spain | C16 Spain | 384.00 | 0.76 | 0.00 | R3 connecteur |
| FC Barcelona | Spain | C16 Spain | 303.00 | 0.76 | -0.37 | R3 connecteur |
| Udinese Calcio | Italy | C3 Italy | 794.00 | 0.75 | 1.01 | R3 connecteur |

## Hubs (z ≥ 2.5) : 160 clubs

| name | country | bloc | strength | P | z | role |
|---|---|---|---|---|---|---|
| Parma Calcio 1913 | Italy | C3 Italy | 1368.00 | 0.32 | 5.77 | R6 hub connecteur |
| East Bengal FC | India | C24 Australia / India / New Zealand | 448.00 | 0.17 | 5.15 | R5 hub provincial |
| Karlsruher SC U19 | Germany | C1 Germany | 476.00 | 0.08 | 3.82 | R5 hub provincial |
| AC Sparta Prague B | Czech Republic | C15 Czech Republic / Slovakia / Hungary | 534.00 | 0.11 | 3.81 | R5 hub provincial |
| HJK Klubi 04 Helsinki | Finland | C17 Finland | 396.00 | 0.12 | 3.79 | R5 hub provincial |
| TSV 1860 München U19 | Germany | C1 Germany | 460.00 | 0.04 | 3.76 | R5 hub provincial |
| Genoa CFC | Italy | C3 Italy | 1088.00 | 0.45 | 3.75 | R6 hub connecteur |
| AKA Steiermark - Sturm Graz U18 | Austria | C5 Austria | 425.00 | 0.01 | 3.73 | R5 hub provincial |
| Hong Kong Rangers | Hongkong | C21 China / Hongkong | 424.00 | 0.20 | 3.73 | R5 hub provincial |
| Leaper | Hongkong | C21 China / Hongkong | 392.00 | 0.06 | 3.73 | R5 hub provincial |
| AKA Tirol U18 | Austria | C5 Austria | 427.00 | 0.05 | 3.66 | R5 hub provincial |
| AKA Burgenland U18 | Austria | C5 Austria | 417.00 | 0.00 | 3.65 | R5 hub provincial |
| Mohun Bagan AC | India | C24 Australia / India / New Zealand | 333.00 | 0.12 | 3.65 | R5 hub provincial |
| Atalanta BC | Italy | C3 Italy | 926.00 | 0.28 | 3.64 | R5 hub provincial |
| Pallokerho-35 | Finland | C17 Finland | 387.00 | 0.13 | 3.63 | R5 hub provincial |
| FC Bayern Munich U19 | Germany | C1 Germany | 459.00 | 0.09 | 3.61 | R5 hub provincial |
| SK Slavia Prague B | Czech Republic | C15 Czech Republic / Slovakia / Hungary | 529.00 | 0.17 | 3.57 | R5 hub provincial |
| Concordia Hamburg | Germany | C13 Germany | 379.00 | 0.12 | 3.55 | R5 hub provincial |
| Berliner AK 07 | Germany | C1 Germany | 492.00 | 0.23 | 3.55 | R5 hub provincial |
| Orlando Pirates | South Africa | C23 Nigeria / Ghana / South Africa | 364.00 | 0.10 | 3.53 | R5 hub provincial |
| Muangthong United | Thailand | C7 Japan | 538.00 | 0.22 | 3.50 | R5 hub provincial |
| Kalev Tallinn | Estonia | C26 Estonia | 314.00 | 0.27 | 3.49 | R5 hub provincial |
| FC Augsburg U19 | Germany | C1 Germany | 435.00 | 0.06 | 3.45 | R5 hub provincial |
| IF Gnistan | Finland | C17 Finland | 366.00 | 0.11 | 3.44 | R5 hub provincial |
| AKA St. Pölten U18 | Austria | C5 Austria | 415.00 | 0.09 | 3.42 | R5 hub provincial |

## Leaders des 15 plus grandes communautés (2 plus forts z)

| name | country | bloc | strength | P | z | role |
|---|---|---|---|---|---|---|
| Karlsruher SC U19 | Germany | C1 Germany | 476.00 | 0.08 | 3.82 | R5 hub provincial |
| TSV 1860 München U19 | Germany | C1 Germany | 460.00 | 0.04 | 3.76 | R5 hub provincial |
| Paris FC | France | C2 France / Belgium / Netherlands | 416.00 | 0.25 | 3.01 | R5 hub provincial |
| Ajax Amsterdam U21 | Netherlands | C2 France / Belgium / Netherlands | 402.00 | 0.24 | 2.90 | R5 hub provincial |
| Parma Calcio 1913 | Italy | C3 Italy | 1368.00 | 0.32 | 5.77 | R6 hub connecteur |
| Genoa CFC | Italy | C3 Italy | 1088.00 | 0.45 | 3.75 | R6 hub connecteur |
| Zenit St. Petersburg II | Russia | C4 Russia / Ukraine | 465.00 | 0.08 | 2.97 | R5 hub provincial |
| FK Khimki | Russia | C4 Russia / Ukraine | 484.00 | 0.20 | 2.85 | R5 hub provincial |
| AKA Steiermark - Sturm Graz U18 | Austria | C5 Austria | 425.00 | 0.01 | 3.73 | R5 hub provincial |
| AKA Tirol U18 | Austria | C5 Austria | 427.00 | 0.05 | 3.66 | R5 hub provincial |
| Asociación Deportivo Pasto | Colombia | C6 Argentina | 558.00 | 0.12 | 2.64 | R5 hub provincial |
| CD Atlético Huila | Colombia | C6 Argentina | 511.00 | 0.13 | 2.28 | R2 périphérique |
| Muangthong United | Thailand | C7 Japan | 538.00 | 0.22 | 3.50 | R5 hub provincial |
| Police Tero FC | Thailand | C7 Japan | 492.00 | 0.21 | 3.14 | R5 hub provincial |
| Brönshöj Boldklub | Denmark | C8 Norway / Denmark / Sweden | 343.00 | 0.03 | 2.93 | R5 hub provincial |
| Hellerup IK | Denmark | C8 Norway / Denmark / Sweden | 325.00 | 0.03 | 2.70 | R5 hub provincial |
| Stevenage FC | England | C9 England / Scotland | 547.00 | 0.04 | 2.39 | R1 ultra-périphérique |
| Blackpool FC | England | C9 England / Scotland | 587.00 | 0.19 | 2.33 | R2 périphérique |
| NK Lokomotiva Zagreb | Croatia | C10 Bosnia-Herzegovina / Serbia | 634.00 | 0.28 | 3.34 | R5 hub provincial |
| FK Novi Pazar | Serbia | C10 Bosnia-Herzegovina / Serbia | 600.00 | 0.39 | 2.67 | R6 hub connecteur |
| Eyüpspor | Türkiye | C11 Türkiye | 617.00 | 0.11 | 2.29 | R2 périphérique |
| Fethiyespor | Türkiye | C11 Türkiye | 575.00 | 0.06 | 2.15 | R2 périphérique |
| SC YF Juventus Zürich | Switzerland | C12 Switzerland | 393.00 | 0.15 | 2.78 | R5 hub provincial |
| FC Fribourg | Switzerland | C12 Switzerland | 358.00 | 0.10 | 2.52 | R5 hub provincial |
| Concordia Hamburg | Germany | C13 Germany | 379.00 | 0.12 | 3.55 | R5 hub provincial |
| Meiendorfer SV | Germany | C13 Germany | 345.00 | 0.12 | 3.11 | R5 hub provincial |
| Apollon Smyrnis | Greece | C14 Greece / Bulgaria / Romania | 525.00 | 0.42 | 2.39 | R2 périphérique |
| Panachaiki GE | Greece | C14 Greece / Bulgaria / Romania | 437.00 | 0.24 | 2.19 | R2 périphérique |
| AC Sparta Prague B | Czech Republic | C15 Czech Republic / Slovakia / Hungary | 534.00 | 0.11 | 3.81 | R5 hub provincial |
| SK Slavia Prague B | Czech Republic | C15 Czech Republic / Slovakia / Hungary | 529.00 | 0.17 | 3.57 | R5 hub provincial |

## Lien avec les centralités (Spearman)

| indicateur | betweenness | out_closeness | pagerank | reverse_pagerank |
|---|---|---|---|---|
| P | 0.60 | 0.65 | 0.27 | 0.41 |
| z | 0.81 | 0.73 | 0.71 | 0.82 |

Figure : `results/figures/community_graph.pdf`.

## Ponts : betweenness des arêtes

Betweenness exacte des arêtes (graphe orienté, non pondéré, normalisée par n(n − 1)). Top 1 000 : `results/tables/edge_betweenness.csv`.

- Part des arêtes reliant deux communautés : 19.7% de toutes les arêtes, 75.5% des 1 000 arêtes de plus forte betweenness, 65.0% des 100 premières.
- Betweenness moyenne d'une arête inter-communautés : 2.8 fois celle d'une arête interne.

| from | to | weight | edge_betweenness | inter-communautés |
|---|---|---|---|---|
| FK Leotar Trebinje (Bosnia-Herzegovina) | FK Sarajevo Academy U17 (Bosnia-Herzegovina) | 1 | 9.95e-04 |  |
| Omonia Nicosia (Cyprus) | Eintracht Frankfurt U17 (Germany) | 1 | 8.27e-04 | oui |
| Shichigahama SC (Japan) | TSV Eintracht Stadtallendorf (Germany) | 1 | 5.58e-04 | oui |
| Merry (Fukushima) (Japan) | Iwaki Furukawa FC (Japan) | 1 | 5.04e-04 |  |
| Iwaki Furukawa FC (Japan) | Zuvor: Thespakusatsu Gunma Challengers (Reserves) (Japan) | 1 | 4.79e-04 |  |
| Warta Poznan (Poland) | MSV Duisburg U17 (Germany) | 1 | 4.71e-04 | oui |
| FK Borac 1926 Cacak (Serbia) | Racing Strasbourg U19 (France) | 1 | 4.65e-04 | oui |
| Cefn Druids (Wales) | FC Sheriff Tiraspol (Moldova) | 1 | 4.63e-04 | oui |
| Tallinn JK Legion (Estonia) | Tallinn JK Legion U19 (Estonia) | 1 | 4.31e-04 |  |
| SC Westfalia Herne (Germany) | ACR Messina (Italy) | 1 | 4.25e-04 | oui |
| JK Merkuur-Juunior (Estonia) | FC Flora Tallinn U17 (Estonia) | 3 | 4.08e-04 |  |
| VfR Neumünster (Germany) | FK Spartaks Jurmala (Latvia) | 1 | 4.04e-04 | oui |
| HJK Helsinki U19 (Finland) | FC Zürich U17 (Switzerland) | 1 | 3.92e-04 | oui |
| Kalju FC (Estonia) | Kalju FC U19 (Estonia) | 1 | 3.92e-04 |  |
| SV Stegersbach (Austria) | AKA Red Bull Salzburg U16 (Austria) | 1 | 3.85e-04 |  |
