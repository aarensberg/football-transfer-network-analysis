# Paris Talent Flow : où partent les joueurs formés au PSG ?

Généré par `uv run python -m ftna.talent_flow`. Produit d'aide à la décision pour le directeur sportif du PSG, construit sur le réseau observé dans ce dataset (Transfermarkt), pas sur le marché mondial complet.

## Méthode et conventions

- Carrières reconstituées à partir de `transfers.csv` **brut** (l'entrée au centre passe par des clubs absents de `clubs.csv`), sans « End of loan », dans l'ordre du fichier pour départager une même année.
- Joueur formé : première arrivée dans une équipe de jeunes ou réserve de l'académie entre 2008 et 2019 (équipes associées manuellement, 15 académies).
- Départ : premier mouvement hors prêt de l'organisation (équipe première + jeunes) vers un autre club ou un pseudo-club (joueur libéré). Évalué si l'année est ≤ 2021 (recul d'au moins deux saisons).
- Valeur ultérieure : plus grosse indemnité de transfert hors prêt payée pour le joueur après son départ, hors mouvements impliquant l'académie, jusqu'à l'année d'un éventuel retour dans l'académie (un rachat ouvre un nouveau départ). L'ordre des lignes dans une même année n'étant pas chronologique, les calculs raisonnent à l'année. Sans limite de durée : les cohortes récentes ont eu moins de temps pour être revendues.
- **Ratio de capture** = Σ indemnités de départ / Σ plus grosses indemnités ultérieures ; intervalle à 95 % par bootstrap sur les joueurs (1 000 tirages, graine 42). Un ratio < 1 signifie que la valeur s'est surtout réalisée ailleurs.
- Élite : 20 premiers clubs de la saison par valeur d'effectif (`club_league`) ; sensibilité à 30. « A joué dans l'élite » : départ ou mouvement (prêt compris) vers un club d'élite au plus 3 ans après le départ, même recul pour toutes les cohortes.
- Montant 0 = transfert gratuit **ou** non divulgué ; les clauses de revente et de rachat ne sont pas visibles. On parle donc de « valeur réalisée ailleurs », sans prétendre mesurer un manque à gagner exact.

## 1. Comparatif des académies

| académie | joueurs formés | départs évalués | départs payés | indemnités de départ (M€) | revendus ensuite avec indemnité | dont ≥ 10 M€ | Σ plus grosses indemnités ultérieures (M€) | ratio de capture | IC 95 % bootstrap | ratio sans les 2 plus gros cas | part ayant joué dans l'élite | rachetés ensuite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **PSG** | 239 | 215 | 20 | 118.7 | 35 | 12 | 325.3 | 0.36 | [0.23 ; 0.58] | 0.41 | 0.033 | 9 |
| Rennes | 112 | 103 | 19 | 133.0 | 25 | 8 | 339.3 | 0.39 | [0.21 ; 0.93] | 0.55 | 0.049 | 2 |
| Bayern | 322 | 274 | 21 | 36.5 | 30 | 3 | 91.9 | 0.4 | [0.17 ; 0.74] | 0.33 | 0.007 | 3 |
| Barcelone | 176 | 141 | 40 | 152.2 | 40 | 10 | 274.0 | 0.56 | [0.29 ; 0.97] | 0.67 | 0.071 | 6 |
| Manchester City | 187 | 154 | 36 | 197.9 | 40 | 10 | 314.3 | 0.63 | [0.37 ; 1.35] | 0.89 | 0.039 | 1 |
| Lille | 153 | 134 | 15 | 86.2 | 22 | 4 | 132.0 | 0.65 | [0.33 ; 1.65] | 0.99 | 0.037 | 3 |
| Marseille | 126 | 109 | 8 | 42.1 | 8 | 3 | 61.0 | 0.69 | [0.09 ; 2.19] | 0.82 | 0.028 | 3 |
| Sporting CP | 145 | 108 | 29 | 175.7 | 30 | 7 | 215.1 | 0.82 | [0.46 ; 1.54] | 0.98 | 0.056 | 4 |
| Real Madrid | 178 | 151 | 37 | 316.5 | 27 | 7 | 271.2 | 1.17 | [0.70 ; 2.13] | 1.54 | 0.066 | 8 |
| Chelsea | 156 | 122 | 28 | 222.6 | 17 | 6 | 187.8 | 1.19 | [0.64 ; 2.71] | 1.65 | 0.041 | 0 |
| Ajax | 251 | 223 | 40 | 398.6 | 63 | 7 | 309.7 | 1.29 | [0.71 ; 2.22] | 1.48 | 0.054 | 4 |
| Monaco | 162 | 146 | 23 | 255.1 | 27 | 9 | 196.3 | 1.3 | [0.25 ; 4.27] | 1.75 | 0.027 | 2 |
| Lyon | 164 | 137 | 30 | 223.3 | 21 | 4 | 170.8 | 1.31 | [0.46 ; 4.19] | 2.55 | 0.08 | 4 |
| Benfica | 213 | 170 | 28 | 438.1 | 45 | 7 | 322.9 | 1.36 | [0.61 ; 3.16] | 1.96 | 0.071 | 5 |
| Juventus | 318 | 223 | 76 | 238.1 | 35 | 2 | 99.3 | 2.4 | [1.46 ; 4.65] | 3.06 | 0.013 | 16 |

PSG : 239 joueurs formés, 215 départs évalués, dont 91% sans indemnité connue. Le club a touché 118.7 M€ au départ ; la somme des plus grosses indemnités payées ensuite atteint 325.3 M€, soit un ratio de capture de **0.36** (IC 95 % [0.23 ; 0.58] ; 0.41 sans les deux plus gros cas).

Lecture : les écarts entre académies sont larges et les intervalles se recouvrent souvent (petits effectifs, quelques joueurs dominent la valeur). La colonne « rachetés ensuite » rend visible un levier absent du ratio : le rachat (cas Real Madrid, Juventus, Barcelone).

Figure : `results/figures/academy_value_capture.pdf`.

## 2. Anciens du PSG

### Plus grosses valeurs réalisées après le départ (départs évalués)

| joueur | poste | naissance | départ | vers | indemnité de départ (M€) | plus grosse indemnité ultérieure (M€) | payée par | élite |
|---|---|---|---|---|---|---|---|---|
| Christopher Nkunku | Midfield - Attacking Midfield | 1997 | 2019 | RB Leipzig (Germany) | 19.5 | 60.0 | Chelsea FC (England) | oui |
| Moussa Diaby | Attack - Right Winger | 1999 | 2019 | Bayer 04 Leverkusen (Germany) | 15.0 | 60.0 | Al-Ittihad Club (Saudi Arabia) | non |
| Jean-Kévin Augustin | Attack - Centre-Forward | 1997 | 2017 | RB Leipzig (Germany) | 16.0 | 21.0 | Leeds United (England) | non |
| Kingsley Coman | Attack - Left Winger | 1996 | 2014 | Juventus FC (Italy) | 0.0 | 21.0 | Bayern Munich (Germany) | oui |
| Boubakary Soumaré | Midfield - Defensive Midfield | 1999 | 2017 | LOSC Lille (France) | 0.0 | 20.0 | Leicester City (England) | non |
| Mike Maignan | Goalkeeper | 1995 | 2015 | LOSC Lille (France) | 1.0 | 16.4 | AC Milan (Italy) | non |
| Odsonne Edouard | Attack - Centre-Forward | 1998 | 2018 | Celtic FC (Scotland) | 10.3 | 16.3 | Crystal Palace (England) | non |
| Tanguy Nianzou | Defender - Centre-Back | 2002 | 2020 | Bayern Munich (Germany) | 0.0 | 16.0 | Sevilla FC (Spain) | oui |
| Jonathan Ikoné | Attack - Right Winger | 1998 | 2018 | LOSC Lille (France) | 5.0 | 15.4 | ACF Fiorentina (Italy) | non |
| Stanley Nsoki | Defender - Centre-Back | 1999 | 2019 | OGC Nice (France) | 12.5 | 12.0 | TSG 1899 Hoffenheim (Germany) | non |
| Timothy Weah | Midfield - Right Midfield | 2000 | 2019 | LOSC Lille (France) | 10.0 | 11.0 | Juventus FC (Italy) | non |
| Fodé Ballo-Touré | Defender - Left-Back | 1997 | 2017 | LOSC Lille (France) | 0.0 | 11.0 | AS Monaco (France) | non |
| Yacine Adli | Midfield - Defensive Midfield | 2000 | 2018 | FC Girondins Bordeaux (France) | 5.5 | 8.8 | AC Milan (Italy) | oui |
| Kévin Cabral | Attack - Left Winger | 1999 | 2017 | Valenciennes FC B (France) | 0.0 | 5.4 | Los Angeles Galaxy (United States) | non |
| Wilfried Kanga | Attack - Centre-Forward | 1998 | 2017 | Angers SCO (France) | 0.0 | 5.0 | Hertha BSC (Germany) | non |

### Départs après 2021 (non encore évaluables)

20 départs ; les 10 plus grosses indemnités de départ :

| joueur | poste | naissance | départ | vers | indemnité de départ (M€) |
|---|---|---|---|---|---|
| Arnaud Kalimuendo | Attack - Centre-Forward | 2002 | 2022 | Stade Rennais FC (France) | 20.0 |
| Alphonse Areola | Goalkeeper | 1993 | 2022 | West Ham United (England) | 9.3 |
| Junior Dina Ebimbe | Midfield - Right Midfield | 2000 | 2023 | Eintracht Frankfurt (Germany) | 6.5 |
| Thierno Baldé | Defender - Right-Back | 2002 | 2022 | ESTAC Troyes (France) | 3.0 |
| Timothée Pembélé | Defender - Right-Back | 2002 | 2023 | Sunderland AFC (England) | 1.0 |
| Anfane Ahamada | Midfield - Defensive Midfield | 2002 | 2023 | Sans club | 0.0 |
| Kenny Nagera | Attack - Centre-Forward | 2002 | 2023 | FC Differdange 03 (Luxembourg) | 0.0 |
| Emeryc Mabandza Batantou | Defender - Centre-Back | 1993 | 2023 | US Lusitanos Saint-Maur (France) | 0.0 |
| Mohamed Touré | Defender - Left-Back | 1995 | 2023 | club 93409 | 0.0 |
| Garissone Innocent | Goalkeeper | 2000 | 2022 | KAS Eupen (Belgium) | 0.0 |

Fiche complète : `results/tables/talent_flow_psg_alumni.csv`.

### Clubs captants (premier club d'accueil, pondéré par la valeur ultérieure)

Anciens du PSG :

| premier club d'accueil | joueurs | Σ plus grosses indemnités ultérieures (M€) | académies d'origine |
|---|---|---|---|
| RB Leipzig (Germany) | 2 | 81.0 | PSG |
| LOSC Lille (France) | 5 | 73.8 | PSG |
| Bayer 04 Leverkusen (Germany) | 1 | 60.0 | PSG |
| Juventus FC (Italy) | 2 | 21.0 | PSG |
| Celtic FC (Scotland) | 1 | 16.3 | PSG |
| Bayern Munich (Germany) | 1 | 16.0 | PSG |
| OGC Nice (France) | 1 | 12.0 | PSG |
| R Charleroi SC (Belgium) | 3 | 8.9 | PSG |
| FC Girondins Bordeaux (France) | 2 | 8.8 | PSG |
| Angers SCO (France) | 4 | 6.5 | PSG |

Six académies françaises (PSG, Lyon, Rennes, Monaco, Lille, Marseille) :

| premier club d'accueil | joueurs | Σ plus grosses indemnités ultérieures (M€) | académies d'origine |
|---|---|---|---|
| AS Monaco (France) | 9 | 149.5 | Lille, Lyon, PSG, Rennes |
| Borussia Dortmund (Germany) | 3 | 135.0 | PSG, Rennes |
| OGC Nice (France) | 10 | 107.0 | Lyon, Monaco, PSG, Rennes |
| RB Leipzig (Germany) | 2 | 81.0 | PSG |
| LOSC Lille (France) | 6 | 73.8 | Marseille, PSG |
| Bayer 04 Leverkusen (Germany) | 1 | 60.0 | PSG |
| VfB Stuttgart (Germany) | 3 | 35.0 | Lille, Monaco, PSG |
| TSG 1899 Hoffenheim (Germany) | 1 | 34.0 | Rennes |
| 1.FSV Mainz 05 (Germany) | 1 | 32.0 | Monaco |
| Paris Saint-Germain (France) | 2 | 30.0 | Lille, Monaco |
| Atlético de Madrid (Spain) | 1 | 30.0 | Monaco |
| Galatasaray (Türkiye) | 1 | 30.0 | Rennes |
| Aston Villa (England) | 1 | 30.0 | Lille |
| Stade Brestois 29 (France) | 6 | 27.5 | Lyon, Monaco, Rennes |
| Stade Reims (France) | 3 | 24.5 | Marseille, PSG, Rennes |

## 3. Analyses de graphe

### PageRank personnalisé depuis les équipes du PSG

Marche aléatoire sur le graphe principal (2010–2023, poids = nombre de transferts, α = 0,85) qui repart toujours des équipes du PSG (583, 6326, 8512) : les clubs où se diffusent les flux de joueurs issus du PSG.

| club | PageRank personnalisé |
|---|---|
| RC Lens (France) | 0.0030 |
| US Orléans (France) | 0.0026 |
| Paris FC (France) | 0.0023 |
| AS Poissy (France) | 0.0023 |
| US Créteil-Lusitanos (France) | 0.0022 |
| Angers SCO (France) | 0.0021 |
| LOSC Lille (France) | 0.0021 |
| KAS Eupen (Belgium) | 0.0020 |
| US Avranches (France) | 0.0020 |
| US Boulogne (France) | 0.0019 |
| ESTAC Troyes (France) | 0.0019 |
| Stade Rennais FC (France) | 0.0019 |
| Le Mans FC (France) | 0.0019 |
| Juventus FC (Italy) | 0.0018 |
| Entente Sannois Saint-Gratien (France) | 0.0018 |

### Sortie de la communauté Louvain (A5)

| académie | communauté | départs vers un club du graphe | part hors communauté | part de la valeur ultérieure hors communauté |
|---|---|---|---|---|
| PSG | C2 | 154 | 0.33 | 0.62 |
| Lyon | C2 | 111 | 0.31 | 0.17 |
| Rennes | C2 | 80 | 0.19 | 0.70 |
| Monaco | C2 | 99 | 0.36 | 0.47 |
| Lille | C2 | 106 | 0.24 | 0.55 |
| Marseille | C2 | 65 | 0.25 | 0.40 |

### Clubs passerelles (participation P, A10)

Départs évalués des 15 académies (un joueur passé par deux centres compte une fois) vers un club hors élite, selon le coefficient de participation du premier club d'accueil.

| premier club d'accueil | départs | part atteignant ensuite l'élite | part revendue avec indemnité | médiane plus grosse indemnité si revendu (M€) |
|---|---|---|---|---|
| P < 0.6 | 1,598 | 0.012 | 0.180 | 1.2 |
| passerelle (P ≥ 0.6) | 256 | 0.055 | 0.477 | 5.3 |

Association, pas causalité : les meilleurs jeunes sont peut-être envoyés en priorité vers ces clubs (biais de sélection).

## 4. Clubs tremplins vers l'élite

Sorties définitives (`Not loan` ou `Unknown`) de 2010 à 2020 depuis un club du graphe principal hors élite cette saison-là, hors équipes de jeunes et réserves (heuristique + Barça Atlètic, Valencia Mestalla, Juventus Next Gen, Sevilla Atlético) ; joueurs arrivés en prêt depuis un club d'élite exclus. Atteinte de l'élite directe ou au mouvement suivant (hors prêt) dans les 3 ans. Clubs avec au moins 30 sorties, triés par borne basse de Wilson.

- 687,113 sorties ; 1,182 atteignent l'élite (0.17%, une moyenne tirée vers le bas par les clubs amateurs) ; 7,368 clubs affichables, dont 5% ont envoyé au moins un joueur dans l'élite. Parmi ces derniers, taux médian 1.3%.
- 86% des passages directs vers l'élite ont une indemnité connue.

### Top 20

| club | sorties | directes | en 2 sauts | taux | IC 95 % (Wilson) | 2010–2015 | 2016–2020 |
|---|---|---|---|---|---|---|---|
| Southampton FC (England) | 82 | 16 | 1 | 0.207 | [0.134 ; 0.307] | 8 | 9 |
| Ajax Amsterdam (Netherlands) | 91 | 17 | 1 | 0.198 | [0.129 ; 0.291] | 10 | 8 |
| Olympique Lyon (France) | 80 | 14 | 2 | 0.2 | [0.127 ; 0.300] | 5 | 11 |
| LOSC Lille (France) | 93 | 12 | 5 | 0.183 | [0.117 ; 0.273] | 9 | 8 |
| Sevilla FC (Spain) | 81 | 14 | 1 | 0.185 | [0.116 ; 0.283] | 11 | 4 |
| Villarreal CF (Spain) | 95 | 15 | 2 | 0.179 | [0.115 ; 0.268] | 11 | 6 |
| Borussia Mönchengladbach (Germany) | 66 | 9 | 3 | 0.182 | [0.107 ; 0.291] | 5 | 7 |
| SL Benfica (Portugal) | 99 | 15 | 1 | 0.162 | [0.102 ; 0.247] | 7 | 9 |
| Genoa CFC (Italy) | 258 | 30 | 4 | 0.132 | [0.096 ; 0.179] | 24 | 10 |
| FC Porto (Portugal) | 70 | 11 | 0 | 0.157 | [0.090 ; 0.260] | 4 | 7 |
| Celta de Vigo (Spain) | 62 | 10 | 0 | 0.161 | [0.090 ; 0.272] | 4 | 6 |
| FC Schalke 04 (Germany) | 100 | 11 | 2 | 0.13 | [0.078 ; 0.210] | 6 | 7 |
| Bayer 04 Leverkusen (Germany) | 73 | 10 | 0 | 0.137 | [0.076 ; 0.234] | 5 | 5 |
| Olympique Marseille (France) | 83 | 8 | 3 | 0.133 | [0.076 ; 0.222] | 4 | 7 |
| Udinese Calcio (Italy) | 195 | 19 | 2 | 0.108 | [0.072 ; 0.159] | 18 | 3 |
| UC Sampdoria (Italy) | 173 | 17 | 2 | 0.11 | [0.071 ; 0.165] | 12 | 7 |
| Newcastle United (England) | 80 | 10 | 0 | 0.125 | [0.069 ; 0.215] | 7 | 3 |
| Red Bull Salzburg (Austria) | 102 | 8 | 4 | 0.118 | [0.069 ; 0.194] | 4 | 8 |
| PSV Eindhoven (Netherlands) | 83 | 8 | 2 | 0.12 | [0.067 ; 0.208] | 6 | 4 |
| AS Roma (Italy) | 52 | 6 | 1 | 0.135 | [0.067 ; 0.253] | 2 | 5 |

### Tremplins français

| club | sorties | directes | en 2 sauts | taux | IC 95 % (Wilson) | 2010–2015 | 2016–2020 |
|---|---|---|---|---|---|---|---|
| Olympique Lyon (France) | 80 | 14 | 2 | 0.2 | [0.127 ; 0.300] | 5 | 11 |
| LOSC Lille (France) | 93 | 12 | 5 | 0.183 | [0.117 ; 0.273] | 9 | 8 |
| Olympique Marseille (France) | 83 | 8 | 3 | 0.133 | [0.076 ; 0.222] | 4 | 7 |
| AS Monaco (France) | 94 | 10 | 0 | 0.106 | [0.059 ; 0.185] | 7 | 3 |
| FC Girondins Bordeaux (France) | 75 | 5 | 2 | 0.093 | [0.046 ; 0.180] | 3 | 4 |
| FC Toulouse (France) | 77 | 5 | 2 | 0.091 | [0.045 ; 0.176] | 3 | 4 |
| Stade Rennais FC (France) | 109 | 5 | 4 | 0.083 | [0.044 ; 0.150] | 5 | 4 |
| AS Saint-Étienne (France) | 78 | 5 | 1 | 0.077 | [0.036 ; 0.158] | 4 | 2 |
| Montpellier HSC (France) | 69 | 4 | 1 | 0.072 | [0.031 ; 0.159] | 4 | 1 |
| FC Lorient (France) | 100 | 5 | 0 | 0.05 | [0.022 ; 0.112] | 3 | 2 |

### Tremplins émergents (2016–2020 contre 2010–2015)

Clubs avec au moins 15 sorties dans chaque période, classés par hausse du taux d'atteinte de l'élite (et non du nombre brut).

| club | sorties 2010–2015 | taux 2010–2015 | sorties 2016–2020 | taux 2016–2020 | hausse |
|---|---|---|---|---|---|
| Southampton FC (England) | 53 | 0.151 | 29 | 0.31 | 0.159 |
| Borussia Mönchengladbach (Germany) | 41 | 0.122 | 25 | 0.28 | 0.158 |
| Leicester City (England) | 51 | 0 | 22 | 0.136 | 0.136 |
| Real Betis Balompié (Spain) | 49 | 0 | 49 | 0.122 | 0.122 |
| CR Flamengo (Brazil) | 73 | 0 | 54 | 0.111 | 0.111 |
| Red Bull Salzburg (Austria) | 56 | 0.071 | 46 | 0.174 | 0.102 |
| Crystal Palace (England) | 48 | 0.021 | 25 | 0.12 | 0.099 |
| Olympique Marseille (France) | 45 | 0.089 | 38 | 0.184 | 0.095 |
| AS Roma (Italy) | 24 | 0.083 | 28 | 0.179 | 0.095 |
| Olympique Lyon (France) | 34 | 0.147 | 46 | 0.239 | 0.092 |

### Sensibilité : élite à 30 clubs

| clubs communs | Spearman des taux | recouvrement top 20 |
|---|---|---|
| 7,361 | 0.827 | 0.600 |

Le ratio de capture (section 1) ne dépend pas de la définition de l'élite.

Figure : `results/figures/springboards.pdf`.

## 5. Concurrents : recrutement étranger dans les équipes de jeunes françaises

Transferts hors prêt retenus dans le graphe principal depuis une équipe de jeunes ou réserve française vers un club étranger.

| pays | 2010–2016 | 2017–2023 | total |
|---|---|---|---|
| Belgium | 65 | 100 | 165 |
| Italy | 29 | 94 | 123 |
| Switzerland | 28 | 53 | 81 |
| England | 34 | 38 | 72 |
| Luxembourg | 18 | 52 | 70 |
| Germany | 24 | 41 | 65 |
| Spain | 23 | 22 | 45 |
| Portugal | 12 | 31 | 43 |
| Bulgaria | 12 | 11 | 23 |
| Czech Republic | 6 | 14 | 20 |

| club | 2010–2016 | 2017–2023 | total |
|---|---|---|---|
| FC Sion U21 (Switzerland) | 5 | 6 | 11 |
| Olympic Charleroi (Belgium) | 0 | 10 | 10 |
| UR La Louvière Centre (Belgium) | 4 | 6 | 10 |
| Royal Excel Mouscron (-2022) (Belgium) | 3 | 6 | 9 |
| Cercle Brugge (Belgium) | 1 | 7 | 8 |
| Francs Borains (Belgium) | 3 | 5 | 8 |
| Royal Excelsior Virton (Belgium) | 4 | 4 | 8 |
| MFK Vyskov (Czech Republic) | 0 | 7 | 7 |
| Swift Hesperange (Luxembourg) | 1 | 6 | 7 |
| FC Luxembourg City (Luxembourg) | 1 | 6 | 7 |
| Stade Tunisien (Tunisia) | 0 | 6 | 6 |
| Racing FC Union Luxembourg (Luxembourg) | 1 | 5 | 6 |
| Standard de Liège 16 FC (Belgium) | 1 | 5 | 6 |
| FC Wiltz 71 (Luxembourg) | 2 | 4 | 6 |
| Zébra Élites (Belgium) | 3 | 3 | 6 |

## 6. Comparables pour les clauses

Départs évalués des 15 académies (un joueur passé par deux centres compte une fois), par poste et âge au départ (année de départ − année de naissance). Valeur = plus grosse indemnité ultérieure : moyenne sur tous les départs (0 compris, espérance utile pour un pourcentage de revente), quantiles parmi les joueurs revendus avec indemnité. Cellules de moins de 10 départs masquées ; quantiles vides si moins de 5 joueurs revendus.

| poste | âge au départ | départs | part revendue avec indemnité | valeur moyenne (M€) | médiane si revendu (M€) | Q75 si revendu (M€) | Q90 si revendu (M€) | part ayant joué dans l'élite |
|---|---|---|---|---|---|---|---|---|
| Gardien | ≤ 19 | 82 | 0.05 | 0.09 |  |  |  | 0.01 |
| Gardien | 20–21 | 72 | 0.10 | 0.31 | 0.75 | 1.75 | 7.76 | 0.01 |
| Gardien | 22–23 | 44 | 0.18 | 0.53 | 1.25 | 3.11 | 7.24 | 0.00 |
| Gardien | ≥ 24 | 23 | 0.04 | 1.04 |  |  |  | 0.00 |
| Défenseur | ≤ 19 | 208 | 0.12 | 0.56 | 1.75 | 4.67 | 10.50 | 0.03 |
| Défenseur | 20–21 | 331 | 0.20 | 1.81 | 2.65 | 9.38 | 30.00 | 0.06 |
| Défenseur | 22–23 | 146 | 0.20 | 1.40 | 1.53 | 4.50 | 14.60 | 0.05 |
| Défenseur | ≥ 24 | 75 | 0.19 | 1.20 | 2.50 | 6.75 | 17.15 | 0.08 |
| Milieu | ≤ 19 | 207 | 0.17 | 0.92 | 2.00 | 8.94 | 16.45 | 0.04 |
| Milieu | 20–21 | 290 | 0.18 | 1.27 | 3.20 | 7.00 | 16.58 | 0.02 |
| Milieu | 22–23 | 141 | 0.23 | 1.43 | 1.20 | 4.10 | 17.60 | 0.06 |
| Milieu | ≥ 24 | 60 | 0.20 | 1.44 | 4.00 | 8.78 | 17.55 | 0.08 |
| Attaquant | ≤ 19 | 213 | 0.21 | 2.76 | 2.50 | 14.25 | 32.80 | 0.05 |
| Attaquant | 20–21 | 240 | 0.24 | 1.67 | 2.50 | 8.50 | 21.44 | 0.03 |
| Attaquant | 22–23 | 131 | 0.32 | 2.00 | 4.08 | 8.00 | 17.18 | 0.05 |
| Attaquant | ≥ 24 | 90 | 0.29 | 1.34 | 1.50 | 5.97 | 14.50 | 0.07 |

## Limites

- Aucune donnée de performance (minutes, statistiques) : le succès est mesuré par les indemnités et l'accès à l'élite.
- Montant 0 ambigu (gratuit ou non divulgué) ; clauses de revente et de rachat invisibles.
- Seules les cohortes parties jusqu'en 2021 sont évaluables ; 2024 est incomplet.
- Petits effectifs : une douzaine de joueurs concentre l'essentiel de la valeur d'une académie (voir le ratio sans les deux plus gros cas).
- Association manuelle des équipes de jeunes à leur club ; heuristique jeunes/réserves imparfaite.
- Pas de lieu de naissance : impossible de localiser les viviers régionaux.
