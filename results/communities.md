# A5. Communautés

Généré par `uv run python -m ftna.communities`. Louvain (NetworkX, résolution 1, graine 42) sur le graphe non orienté pondéré w(u,v) = w(u→v) + w(v→u). Affectations : `results/tables/communities.csv`.

## Partition de référence

- Communautés : 35 ; modularité : 0.836.
- Les 15 plus grandes couvrent 78.9% des clubs ; communautés de moins de 10 clubs : 7.
- Pureté nationale moyenne (part du pays dominant, pondérée par la taille) : 0.683.

| communauté | clubs | pays dominant | part du pays dominant | pays (top 3) | poids interne | clubs les plus actifs |
|---|---|---|---|---|---|---|
| 1 | 1,889 | Germany | 0.99 | Germany 1869, ? 10, Netherlands 3 | 0.93 | Berliner AK 07, Sportfreunde Lotte, Tennis Borussia Berlin, 1.FC Kaiserslautern |
| 2 | 890 | France | 0.56 | France 499, Belgium 165, Netherlands 144 | 0.85 | AS Monaco, Standard Liège, RSC Anderlecht, KAA Gent |
| 3 | 787 | Italy | 0.98 | Italy 769, San Marino 16, Switzerland 1 | 0.94 | Parma Calcio 1913, Genoa CFC, Atalanta BC, Delfino Pescara 1936 |
| 4 | 774 | Russia | 0.28 | Russia 219, Ukraine 140, Belarus 65 | 0.89 | FK Khimki, Dinamo Tbilisi, SKA Khabarovsk, Rubin Kazan |
| 5 | 705 | Austria | 0.98 | Austria 688, Germany 12, Hungary 2 | 0.91 | Red Bull Salzburg, LASK, SV Kapfenberg, SV Horn |
| 6 | 692 | Argentina | 0.20 | Argentina 136, Mexico 98, Peru 68 | 0.93 | Asociación Deportivo Pasto, CD América de Cali, Querétaro FC, Defensa y Justicia |
| 7 | 572 | Japan | 0.57 | Japan 326, Thailand 66, Korea, South 64 | 0.91 | Muangthong United, Police Tero FC, Daejeon Hana Citizen, Gyeongnam FC |
| 8 | 532 | Norway | 0.34 | Norway 179, Denmark 135, Sweden 114 | 0.89 | FC Midtjylland, AFC Eskilstuna, Vejle Boldklub, HB Köge |
| 9 | 503 | England | 0.54 | England 273, Scotland 84, Wales 75 | 0.92 | Blackpool FC, Stevenage FC, Chelsea FC, Fleetwood Town |
| 10 | 476 | Bosnia-Herzegovina | 0.29 | Bosnia-Herzegovina 139, Serbia 78, Slovenia 67 | 0.84 | NK Lokomotiva Zagreb, Red Star Belgrade, FK Novi Pazar, GNK Dinamo Zagreb |
| 11 | 386 | Türkiye | 1.00 | Türkiye 386 | 0.93 | Genclerbirligi Ankara, Adana Demirspor, Trabzonspor, Boluspor |
| 12 | 336 | Switzerland | 0.94 | Switzerland 315, Germany 19, ? 2 | 0.88 | FC Chiasso, FC Sion, Grasshopper Club Zurich, FC Lugano |
| 13 | 314 | Germany | 1.00 | Germany 313, Japan 1 | 0.92 | Concordia Hamburg, Altona 93, Meiendorfer SV, TB Uphusen |
| 14 | 309 | Greece | 0.38 | Greece 118, Bulgaria 92, Romania 52 | 0.77 | Olympiacos Piraeus, Ermis Aradippou, PAOK Thessaloniki, AE Larisa |
| 15 | 306 | Czech Republic | 0.54 | Czech Republic 165, Slovakia 81, Hungary 58 | 0.85 | SK Slavia Prague, DAC Dunajska Streda, Spartak Trnava, FK Viktoria Zizkov |
| 16 | 301 | Spain | 0.88 | Spain 266, Andorra 17, Gibraltar 16 | 0.85 | Granada CF, Real Murcia CF, Cádiz CF, CD Leganés |
| 17 | 301 | Finland | 1.00 | Finland 301 | 0.92 | HJK Klubi 04 Helsinki, Pallokerho-35, IF Gnistan, HJK Helsinki |
| 18 | 300 | Brazil | 0.60 | Brazil 179, Portugal 121 | 0.84 | Tombense Futebol Clube (MG), Cruzeiro Esporte Clube, Mirassol Futebol Clube (SP), Red Bull Bragantino |
| 19 | 267 | Poland | 1.00 | Poland 266, Germany 1 | 0.89 | Jagiellonia Bialystok, Górnik Zabrze, Legia Warszawa, Korona Kielce |
| 20 | 233 | Tunisia | 0.20 | Tunisia 46, Saudi Arabia 46, Algeria 46 | 0.87 | Club Africain Tunis, ES Sétif, Esperance Tunis, Raja Club Athletic |
| 21 | 214 | China | 0.63 | China 134, Hongkong 54, Chinese Taipei 22 | 0.89 | Hong Kong Rangers, Leaper, Orion FC, Tai Po |
| 22 | 184 | United States | 0.74 | United States 136, Jamaica 33, Canada 9 | 0.75 | Vancouver Whitecaps FC, Toronto FC, Colorado Rapids, New York Red Bulls |
| 23 | 184 | Nigeria | 0.23 | Nigeria 43, Ghana 39, South Africa 35 | 0.89 | Mamelodi Sundowns FC, Orlando Pirates, Enyimba Aba, Chippa United |
| 24 | 169 | Australia | 0.32 | Australia 54, India 52, New Zealand 49 | 0.82 | East Bengal FC, Mohun Bagan AC, NorthEast United FC, Western Sydney Wanderers |
| 25 | 140 | Iran | 1.00 | Iran 140 | 0.96 | Mes Kerman, FC Nassaji Mazandaran, Fajr Sepasi Shiraz, Naft Masjed Soleyman FC |

`poids interne` : part de la force des membres réalisée à l'intérieur de la communauté.

Figure : `results/figures/community_countries.pdf`.

## Dispersion des grands pays entre communautés

| pays | clubs | communautés (90 %) | part dans la 1ʳᵉ |
|---|---|---|---|
| Germany | 2,238 | 2 | 0.84 |
| Italy | 769 | 1 | 1.00 |
| Austria | 688 | 1 | 1.00 |
| France | 499 | 1 | 1.00 |
| Türkiye | 387 | 1 | 1.00 |
| Japan | 342 | 1 | 0.95 |
| Switzerland | 318 | 1 | 0.99 |
| Finland | 301 | 1 | 1.00 |
| England | 273 | 1 | 1.00 |
| Spain | 268 | 1 | 0.99 |
| Poland | 266 | 1 | 1.00 |
| Russia | 219 | 1 | 1.00 |

## Comparaisons

| partition | communautés | modularité (non orientée) | modularité orientée | NMI avec référence | NMI avec le pays |
|---|---|---|---|---|---|
| Louvain non orienté (référence) | 35 | 0.836 | 0.836 | 1.000 | 0.849 |
| Leiden (modularité) | 34 | 0.836 | 0.836 | 0.992 | 0.852 |
| Louvain orienté (optimise la modularité orientée) | 35 | 0.836 | 0.836 | 0.987 | 0.853 |
| Pays (partition de référence externe) | 111 | 0.806 | 0.806 | 0.849 | 1.000 |

Modularité non orientée : graphe w(u,v) = w(u→v) + w(v→u) ; modularité orientée : formule de Leicht et Newman sur le graphe orienté pondéré.

## Significativité : modèle nul

Louvain (graine 42) sur 3 graphes du modèle de configuration pondéré (forces des clubs préservées, appariement aléatoire des transferts, boucles retirées).

| réalisation | arêtes distinctes | communautés | modularité |
|---|---|---|---|
| 1 | 902,514 | 8 | 0.063 |
| 2 | 902,311 | 9 | 0.063 |
| 3 | 902,302 | 6 | 0.064 |

- Modularité observée 0.836 contre 0.063 ± 0.001 sous le modèle nul (score z ≈ 975).

## Stabilité de Louvain (10 graines)

| indicateur | valeur |
|---|---|
| modularité (moyenne) | 0.836 |
| modularité (écart-type) | 0.000 |
| nombre de communautés (min) | 34.000 |
| nombre de communautés (max) | 37.000 |
| NMI entre graines (moyenne) | 0.976 |
| ARI entre graines (moyenne) | 0.933 |

## Effet de la résolution

| résolution γ | communautés | communautés ≥ 50 clubs | plus grande | modularité (γ = 1) | NMI avec le pays |
|---|---|---|---|---|---|
| 0.500 | 25 | 19 | 2,210 | 0.828 | 0.809 |
| 1.000 | 35 | 26 | 1,889 | 0.836 | 0.849 |
| 2.000 | 58 | 48 | 787 | 0.827 | 0.874 |
| 4.000 | 88 | 68 | 769 | 0.816 | 0.897 |

Lecture : la colonne « modularité (γ = 1) » évalue chaque partition avec la modularité standard, que Louvain à γ = 1 optimise directement ; son maximum à γ = 1 est donc attendu et ne justifie pas à lui seul ce choix. La NMI croît mécaniquement avec le nombre de communautés : sa hausse avec γ ne prouve pas que les communautés fines sont « plus nationales ».
