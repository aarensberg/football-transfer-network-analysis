# A4. Centralités

Généré par `uv run python -m ftna.centrality`. Table complète : `results/tables/centrality.csv`.

- PageRank : α = 0.85, pondéré par le nombre de transferts ; PageRank inverse calculé sur le graphe transposé.
- Closeness : exacte, sur la CFC géante (distances en sauts).
- Betweenness : exacte, non pondérée, normalisée par (n − 1)(n − 2).
- Contrôle de l'approximation (k = 1000 sources, graine 42) : Spearman = 0.964 avec la valeur exacte ; recouvrement du top 100 = 70%.

## Valeurs extrêmes de force sortante

| name | country | out_strength | out_degree |
|---|---|---|---|
| Parma Calcio 1913 | Italy | 926 | 278 |
| Atalanta BC | Italy | 718 | 217 |
| Genoa CFC | Italy | 717 | 259 |

## Top 20 : pagerank

| rang | club | pays | pagerank | jeunes/réserve |
|---|---|---|---|---|
| 1 | Kalev Tallinn | Estonia | 0.0004184 |  |
| 2 | FSV Duisburg | Germany | 0.0003396 |  |
| 3 | Pallokerho-35 | Finland | 0.0003249 |  |
| 4 | FC Kiffen | Finland | 0.0003123 |  |
| 5 | Tampere United | Finland | 0.0003111 |  |
| 6 | SC Ostbahn XI | Austria | 0.0003099 |  |
| 7 | FC Ararat Yerevan | Armenia | 0.0003058 |  |
| 8 | Paide Linnameeskond | Estonia | 0.0003042 |  |
| 9 | FC Kuressaare | Estonia | 0.0002966 |  |
| 10 | Atlantis FC | Finland | 0.0002878 |  |
| 11 | SV Zeilsheim | Germany | 0.0002824 |  |
| 12 | IF Gnistan | Finland | 0.0002761 |  |
| 13 | Ganzhou Ruishi | China | 0.0002731 |  |
| 14 | Reilac Shiga | Japan | 0.0002731 |  |
| 15 | Alashkert Yerevan FC | Armenia | 0.0002719 |  |
| 16 | NK Zvijezda Gradacac | Bosnia-Herzegovina | 0.0002713 |  |
| 17 | NK Jedinstvo Bihac | Bosnia-Herzegovina | 0.0002706 |  |
| 18 | SV Hönnepel-Niedermörmter | Germany | 0.0002694 |  |
| 19 | SV Wörgl | Austria | 0.0002679 |  |
| 20 | Nevsehir Belediye Spor | Türkiye | 0.0002655 |  |

Pays du top 100 : Germany 29, Switzerland 10, Finland 9, Türkiye 8, Estonia 7, Austria 6.

## Top 20 : reverse_pagerank

| rang | club | pays | reverse_pagerank | jeunes/réserve |
|---|---|---|---|---|
| 1 | AKA Red Bull Salzburg U16 | Austria | 0.001728 | oui |
| 2 | Rot-Weiß Erfurt U17 | Germany | 0.001542 | oui |
| 3 | AKA Rapid Wien U16 | Austria | 0.001348 | oui |
| 4 | FK Sarajevo Academy U17 | Bosnia-Herzegovina | 0.001253 | oui |
| 5 | AKA SV Ried U16 | Austria | 0.001099 | oui |
| 6 | FC Carl Zeiss Jena U17 | Germany | 0.001088 | oui |
| 7 | AKA Steiermark - Sturm Graz U16 | Austria | 0.001071 | oui |
| 8 | 1.FC Kaiserslautern U17 | Germany | 0.001012 | oui |
| 9 | Ajax Amsterdam U19 | Netherlands | 0.0009978 | oui |
| 10 | AKA Burgenland U16 | Austria | 0.000987 | oui |
| 11 | Hallescher FC U17 | Germany | 0.0009866 | oui |
| 12 | HJK Helsinki U19 | Finland | 0.0009817 | oui |
| 13 | AKA St. Pölten U16 | Austria | 0.0009142 | oui |
| 14 | Pallokerho-35 U19 | Finland | 0.0008634 | oui |
| 15 | RasenBallsport Leipzig U17 | Germany | 0.000846 | oui |
| 16 | Borussia Dortmund U17 | Germany | 0.0008398 | oui |
| 17 | AKA Tirol U16 | Austria | 0.0008279 | oui |
| 18 | AKA LASK OÖ U16 | Austria | 0.0008158 | oui |
| 19 | FC Erzgebirge Aue U17 | Germany | 0.0008122 | oui |
| 20 | Ajax U18 | Netherlands | 0.0008121 | oui |

Pays du top 100 : Germany 37, Austria 14, Italy 10, France 6, Russia 6, Bosnia-Herzegovina 5.

## Top 20 : betweenness

| rang | club | pays | betweenness | jeunes/réserve |
|---|---|---|---|---|
| 1 | BSV Schwarz-Weiß Rehden | Germany | 0.0049 |  |
| 2 | KFC Uerdingen 05 | Germany | 0.003625 |  |
| 3 | SV 1910 Neuhof | Germany | 0.003612 |  |
| 4 | Mosta FC | Malta | 0.003541 |  |
| 5 | FK Spartaks Jurmala | Latvia | 0.003454 |  |
| 6 | FC International Leipzig | Germany | 0.00326 |  |
| 7 | SV Kapfenberg | Austria | 0.003141 |  |
| 8 | Kalju FC | Estonia | 0.003123 |  |
| 9 | FC Mauerwerk | Austria | 0.003078 |  |
| 10 | TSG Neustrelitz | Germany | 0.003054 |  |
| 11 | SV Horn | Austria | 0.002986 |  |
| 12 | FCI Levadia | Estonia | 0.002974 |  |
| 13 | Kalev Tallinn | Estonia | 0.002935 |  |
| 14 | Parma Calcio 1913 | Italy | 0.002928 |  |
| 15 | FC Wacker Innsbruck | Austria | 0.002858 |  |
| 16 | Germania Halberstadt | Germany | 0.002834 |  |
| 17 | VfB Oldenburg | Germany | 0.002805 |  |
| 18 | FC Lahti | Finland | 0.002735 |  |
| 19 | Berliner AK 07 | Germany | 0.002715 |  |
| 20 | NK Hrvatski Dragovoljac | Croatia | 0.002696 |  |

Pays du top 100 : Germany 35, Finland 15, Austria 8, Estonia 5, Türkiye 4, Croatia 3.

## Top 20 : in_closeness

| rang | club | pays | in_closeness | jeunes/réserve |
|---|---|---|---|---|
| 1 | Mosta FC | Malta | 0.3561 |  |
| 2 | FC Sheriff Tiraspol | Moldova | 0.356 |  |
| 3 | NK Istra 1961 | Croatia | 0.356 |  |
| 4 | FC Botosani | Romania | 0.3558 |  |
| 5 | Ermis Aradippou | Cyprus | 0.3537 |  |
| 6 | ACSM Politehnica Iasi | Romania | 0.3531 |  |
| 7 | FK Novi Pazar | Serbia | 0.3531 |  |
| 8 | FK Kukësi | Albania | 0.353 |  |
| 9 | Ethnikos Achnas | Cyprus | 0.3517 |  |
| 10 | AEL Limassol | Cyprus | 0.3516 |  |
| 11 | Doxa Katokopias | Cyprus | 0.3513 |  |
| 12 | FK Radnicki Nis | Serbia | 0.3512 |  |
| 13 | Lokomotiv Plovdiv | Bulgaria | 0.351 |  |
| 14 | FK Sarajevo | Bosnia-Herzegovina | 0.3509 |  |
| 15 | FC Dinamo Bucharest | Romania | 0.3508 |  |
| 16 | Slaven Belupo Koprivnica | Croatia | 0.3503 |  |
| 17 | Nea Salamina Famagusta | Cyprus | 0.3502 |  |
| 18 | Enosis Neon Paralimniou | Cyprus | 0.3498 |  |
| 19 | Petrolul Ploiesti | Romania | 0.3498 |  |
| 20 | Rabotnicki Skopje | North Macedonia | 0.3497 |  |

Pays du top 100 : Cyprus 11, Türkiye 9, Romania 8, Greece 8, Croatia 6, Albania 6.

## Top 20 : out_closeness

| rang | club | pays | out_closeness | jeunes/réserve |
|---|---|---|---|---|
| 1 | HNK Hajduk Split | Croatia | 0.3663 |  |
| 2 | HNK Rijeka | Croatia | 0.3645 |  |
| 3 | Udinese Calcio | Italy | 0.3636 |  |
| 4 | NK Istra 1961 | Croatia | 0.3626 |  |
| 5 | GNK Dinamo Zagreb | Croatia | 0.3606 |  |
| 6 | Red Star Belgrade | Serbia | 0.3605 |  |
| 7 | Olympiacos Piraeus | Greece | 0.36 |  |
| 8 | FK Partizan Belgrade | Serbia | 0.3593 |  |
| 9 | FC Sion | Switzerland | 0.3588 |  |
| 10 | CSKA-Sofia | Bulgaria | 0.3588 |  |
| 11 | Parma Calcio 1913 | Italy | 0.3586 |  |
| 12 | FK Sarajevo | Bosnia-Herzegovina | 0.3586 |  |
| 13 | Genoa CFC | Italy | 0.3585 |  |
| 14 | AE Larisa | Greece | 0.3583 |  |
| 15 | DAC Dunajska Streda | Slovakia | 0.3578 |  |
| 16 | AEL Limassol | Cyprus | 0.3576 |  |
| 17 | HSK Zrinjski Mostar | Bosnia-Herzegovina | 0.3574 |  |
| 18 | FC Sheriff Tiraspol | Moldova | 0.3572 |  |
| 19 | NK Lokomotiva Zagreb | Croatia | 0.3569 |  |
| 20 | Enosis Neon Paralimniou | Cyprus | 0.3566 |  |

Pays du top 100 : Croatia 13, Greece 11, Italy 9, Cyprus 9, Serbia 8, Bulgaria 5.

## Top 20 : in_strength

| rang | club | pays | in_strength | jeunes/réserve |
|---|---|---|---|---|
| 1 | Parma Calcio 1913 | Italy | 442 |  |
| 2 | Associação Atlética Ponte Preta | Brazil | 389 |  |
| 3 | Red Bull Bragantino | Brazil | 389 |  |
| 4 | Guarani Futebol Clube (SP) | Brazil | 374 |  |
| 5 | ABC Futebol Clube (RN) | Brazil | 374 |  |
| 6 | Genoa CFC | Italy | 371 |  |
| 7 | Delfino Pescara 1936 | Italy | 364 |  |
| 8 | Clube de Regatas Brasil (AL) | Brazil | 361 |  |
| 9 | Associação Chapecoense de Futebol | Brazil | 359 |  |
| 10 | Mirassol Futebol Clube (SP) | Brazil | 358 |  |
| 11 | Boa EC | Brazil | 357 |  |
| 12 | América FC | Brazil | 356 |  |
| 13 | Atlético Clube Goianiense | Brazil | 356 |  |
| 14 | Fidelis Andria 2018 | Italy | 353 |  |
| 15 | Oeste FC | Brazil | 353 |  |
| 16 | Adana Demirspor | Türkiye | 350 |  |
| 17 | Fortaleza Esporte Clube | Brazil | 350 |  |
| 18 | AC Carpi | Italy | 349 |  |
| 19 | Clube Náutico Capibaribe | Brazil | 348 |  |
| 20 | Siena FC | Italy | 347 |  |

Pays du top 100 : Italy 43, Brazil 31, Türkiye 16, Greece 3, England 3, Serbia 1.

## Top 20 : out_strength

| rang | club | pays | out_strength | jeunes/réserve |
|---|---|---|---|---|
| 1 | Parma Calcio 1913 | Italy | 926 |  |
| 2 | Atalanta BC | Italy | 718 |  |
| 3 | Genoa CFC | Italy | 717 |  |
| 4 | Tombense Futebol Clube (MG) | Brazil | 650 |  |
| 5 | Inter Milan | Italy | 582 |  |
| 6 | Udinese Calcio | Italy | 571 |  |
| 7 | Juventus FC | Italy | 565 |  |
| 8 | Chievo Verona | Italy | 546 |  |
| 9 | UC Sampdoria | Italy | 529 |  |
| 10 | AS Roma | Italy | 489 |  |
| 11 | Olympiacos Piraeus | Greece | 482 |  |
| 12 | ACF Fiorentina | Italy | 467 |  |
| 13 | Sociedade Esportiva Palmeiras | Brazil | 458 |  |
| 14 | SL Benfica | Portugal | 452 |  |
| 15 | Cruzeiro Esporte Clube | Brazil | 451 |  |
| 16 | Sport Club Internacional | Brazil | 448 |  |
| 17 | Sport Club Corinthians Paulista | Brazil | 447 |  |
| 18 | AC Milan | Italy | 442 |  |
| 19 | Delfino Pescara 1936 | Italy | 439 |  |
| 20 | SSC Napoli | Italy | 436 |  |

Pays du top 100 : Italy 34, Brazil 21, Türkiye 10, England 8, Portugal 4, Croatia 4.

## Top 20 : in_degree

| rang | club | pays | in_degree | jeunes/réserve |
|---|---|---|---|---|
| 1 | Taranto FC 1927 | Italy | 202 |  |
| 2 | Parma Calcio 1913 | Italy | 200 |  |
| 3 | ACR Messina | Italy | 187 |  |
| 4 | SS Arezzo | Italy | 180 |  |
| 5 | US Sambenedettese | Italy | 180 |  |
| 6 | FC Pistoiese | Italy | 178 |  |
| 7 | Nocerina Calcio | Italy | 177 |  |
| 8 | Siena FC | Italy | 176 |  |
| 9 | Rimini FC | Italy | 174 |  |
| 10 | Fidelis Andria 2018 | Italy | 173 |  |
| 11 | AC Carpi | Italy | 172 |  |
| 12 | US Grosseto 1912 | Italy | 171 |  |
| 13 | Cavese 1919 | Italy | 167 |  |
| 14 | US Vibonese | Italy | 166 |  |
| 15 | US Triestina | Italy | 165 |  |
| 16 | Fatih Karagümrük | Türkiye | 163 |  |
| 17 | FC Sheriff Tiraspol | Moldova | 162 |  |
| 18 | Paganese Calcio 1926 | Italy | 162 |  |
| 19 | Calcio Lecco 1912 | Italy | 161 |  |
| 20 | Latina Calcio 1932 | Italy | 161 |  |

Pays du top 100 : Italy 49, Türkiye 24, Cyprus 5, Greece 4, Brazil 4, England 3.

## Top 20 : out_degree

| rang | club | pays | out_degree | jeunes/réserve |
|---|---|---|---|---|
| 1 | Parma Calcio 1913 | Italy | 278 |  |
| 2 | Udinese Calcio | Italy | 260 |  |
| 3 | Genoa CFC | Italy | 259 |  |
| 4 | SL Benfica | Portugal | 229 |  |
| 5 | Inter Milan | Italy | 226 |  |
| 6 | UC Sampdoria | Italy | 223 |  |
| 7 | AS Roma | Italy | 222 |  |
| 8 | Olympiacos Piraeus | Greece | 222 |  |
| 9 | Juventus FC | Italy | 218 |  |
| 10 | Atalanta BC | Italy | 217 |  |
| 11 | AC Milan | Italy | 214 |  |
| 12 | Manchester City U21 | England | 209 | oui |
| 13 | ACF Fiorentina | Italy | 206 |  |
| 14 | Chievo Verona | Italy | 206 |  |
| 15 | Sporting CP | Portugal | 205 |  |
| 16 | SS Lazio | Italy | 198 |  |
| 17 | Torino Primavera | Italy | 198 | oui |
| 18 | SSC Napoli | Italy | 197 |  |
| 19 | Tombense Futebol Clube (MG) | Brazil | 193 |  |
| 20 | Red Star Belgrade | Serbia | 192 |  |

Pays du top 100 : Italy 44, England 11, Brazil 11, Türkiye 6, Portugal 4, Greece 4.

## Corrélations de Spearman entre mesures

| mesure | in_degree | out_degree | in_strength | out_strength | pagerank | reverse_pagerank | in_closeness | out_closeness | betweenness |
|---|---|---|---|---|---|---|---|---|---|
| in_degree | 1.00 | 0.91 | 0.94 | 0.81 | 0.79 | 0.63 | 0.91 | 0.79 | 0.82 |
| out_degree | 0.91 | 1.00 | 0.90 | 0.94 | 0.62 | 0.81 | 0.82 | 0.90 | 0.84 |
| in_strength | 0.94 | 0.90 | 1.00 | 0.85 | 0.80 | 0.67 | 0.84 | 0.78 | 0.81 |
| out_strength | 0.81 | 0.94 | 0.85 | 1.00 | 0.57 | 0.90 | 0.72 | 0.86 | 0.80 |
| pagerank | 0.79 | 0.62 | 0.80 | 0.57 | 1.00 | 0.45 | 0.67 | 0.43 | 0.72 |
| reverse_pagerank | 0.63 | 0.81 | 0.67 | 0.90 | 0.45 | 1.00 | 0.54 | 0.74 | 0.76 |
| in_closeness | 0.91 | 0.82 | 0.84 | 0.72 | 0.67 | 0.54 | 1.00 | 0.84 | 0.80 |
| out_closeness | 0.79 | 0.90 | 0.78 | 0.86 | 0.43 | 0.74 | 0.84 | 1.00 | 0.79 |
| betweenness | 0.82 | 0.84 | 0.81 | 0.80 | 0.72 | 0.76 | 0.80 | 0.79 | 1.00 |

## Validation externe

Clubs avec valeur marchande actuelle > 0 : 4,410.

| mesure | Spearman avec current_mv | Spearman avec montants payés |
|---|---|---|
| in_degree | 0.53 | 0.49 |
| out_degree | 0.56 | 0.55 |
| in_strength | 0.48 | 0.49 |
| out_strength | 0.54 | 0.54 |
| pagerank | 0.03 | 0.18 |
| reverse_pagerank | 0.47 | 0.47 |
| in_closeness | 0.53 | 0.50 |
| out_closeness | 0.59 | 0.56 |
| betweenness | 0.36 | 0.44 |

Figure : `results/figures/pagerank_map.pdf`.
