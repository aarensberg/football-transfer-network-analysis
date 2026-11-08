# A7–A8. Analyses de sensibilité

Généré par `uv run python -m ftna.sensitivity`. Betweenness approchée (k = 1000, graine 42) pour toutes les variantes ; Louvain graine 42.

## Structure

| variante | nœuds | arêtes | transferts | réciprocité | clustering moyen | CFF | part CFC géante | diamètre (CFC) | rayon (CFC) | distance moyenne | communautés | modularité | NMI avec le pays |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| référence | 12,009 | 450,217 | 920,304 | 0.412 | 0.336 | 6 | 0.966 | 12 | 6 | 3.652 | 35 | 0.836 | 0.849 |
| sans jeunes/réserves | 10,442 | 389,038 | 761,345 | 0.442 | 0.349 | 16 | 0.971 | 10 | 5 | 3.610 | 45 | 0.830 | 0.835 |
| 2010–2016 | 10,973 | 232,181 | 404,390 | 0.364 | 0.312 | 2 | 0.913 | 15 | 10 | 4.158 | 29 | 0.835 | 0.759 |
| 2017–2023 | 11,380 | 290,215 | 515,914 | 0.362 | 0.310 | 7 | 0.945 | 13 | 7 | 4.062 | 39 | 0.837 | 0.859 |
| sans type Unknown | 11,784 | 377,886 | 674,911 | 0.378 | 0.308 | 8 | 0.945 | 13 | 7 | 3.772 | 32 | 0.817 | 0.821 |
| avec End of loan | 12,009 | 471,085 | 980,174 | 0.480 | 0.336 | 6 | 0.967 | 12 | 6 | 3.620 | 34 | 0.837 | 0.845 |

## Stabilité des centralités (Spearman sur les clubs communs)

| variante | clubs communs | ρ out_strength | ρ in_strength | ρ pagerank | ρ reverse_pagerank | ρ out_closeness | ρ betweenness | NMI communautés |
|---|---|---|---|---|---|---|---|---|
| sans jeunes/réserves | 10,442 | 0.993 | 0.989 | 0.986 | 0.966 | 0.997 | 0.927 | 0.973 |
| 2010–2016 | 10,973 | 0.868 | 0.882 | 0.821 | 0.853 | 0.908 | 0.781 | 0.920 |
| 2017–2023 | 11,380 | 0.925 | 0.920 | 0.910 | 0.906 | 0.940 | 0.830 | 0.965 |
| sans type Unknown | 11,784 | 0.892 | 0.901 | 0.911 | 0.907 | 0.973 | 0.890 | 0.951 |
| avec End of loan | 12,009 | 0.996 | 0.996 | 0.971 | 0.985 | 0.996 | 0.938 | 0.977 |

## Recouvrement des top 50

| variante | top50 out_strength | top50 in_strength | top50 pagerank | top50 reverse_pagerank | top50 out_closeness | top50 betweenness |
|---|---|---|---|---|---|---|
| sans jeunes/réserves | 0.98 | 0.78 | 0.70 | 0.60 | 0.94 | 0.58 |
| 2010–2016 | 0.72 | 0.70 | 0.24 | 0.64 | 0.54 | 0.44 |
| 2017–2023 | 0.76 | 0.46 | 0.54 | 0.62 | 0.64 | 0.46 |
| sans type Unknown | 0.86 | 0.76 | 0.62 | 0.42 | 0.74 | 0.52 |
| avec End of loan | 0.76 | 0.58 | 0.80 | 0.92 | 0.92 | 0.60 |

## Top 10 : sans jeunes/réserves

| reverse_pagerank | pagerank | betweenness | out_closeness |
|---|---|---|---|
| Genoa CFC | FSV Duisburg | BSV Schwarz-Weiß Rehden | HNK Hajduk Split |
| Parma Calcio 1913 | SC Ostbahn XI | TuS Koblenz | Udinese Calcio |
| Juventus FC | Pallokerho-35 | TSG Neustrelitz | HNK Rijeka |
| Inter Milan | SV Zeilsheim | Mosta FC | NK Istra 1961 |
| Chelsea FC | FC Kiffen | NK Hrvatski Dragovoljac | Red Star Belgrade |
| Udinese Calcio | Tampere United | KFC Uerdingen 05 | GNK Dinamo Zagreb |
| AS Roma | Hilal 1994 Bergheim | FC International Leipzig | Parma Calcio 1913 |
| Atalanta BC | Hamm United FC | FK Spartaks Jurmala | Genoa CFC |
| SL Benfica | SV Hönnepel-Niedermörmter | SV 1910 Neuhof | Olympiacos Piraeus |
| UC Sampdoria | Arminia Hannover | Parma Calcio 1913 | CSKA-Sofia |

## Top 10 : 2010–2016

| reverse_pagerank | pagerank | betweenness | out_closeness |
|---|---|---|---|
| FC Carl Zeiss Jena U17 | SC Ostbahn XI | Parma Calcio 1913 | HNK Hajduk Split |
| Hallescher FC U17 | BSV Hürtürkel | BSV Schwarz-Weiß Rehden | Parma Calcio 1913 |
| AKA Burgenland U16 | Hilal 1994 Bergheim | SVN Zweibrücken | Udinese Calcio |
| AKA Rapid Wien U16 | Tennis Borussia Berlin | Atlantis FC | Olympiacos Piraeus |
| 1.FC Tatran Presov U19 | TuS Germania Schnelsen | Germania Halberstadt | AC Milan |
| 1.FC Magdeburg U17 | FC Ararat Yerevan | FC Oberneuland | CSKA-Sofia |
| 1.FSV Mainz 05 U17 | Paide Linnameeskond | SpVgg Unterhaching | Red Star Belgrade |
| 1.FC Saarbrücken U17 | Kalev Tallinn | FC 08 Homburg | TSG 1899 Hoffenheim |
| FC Nitra U19 | BC Sport Kassel | Kalev Tallinn | HNK Rijeka |
| Borussia Dortmund U17 | Rhyl FC (- 2020) | SV Kapfenberg | SL Benfica |

## Top 10 : 2017–2023

| reverse_pagerank | pagerank | betweenness | out_closeness |
|---|---|---|---|
| Rot-Weiß Erfurt U17 | FSV Duisburg | SV 1910 Neuhof | Vejle Boldklub |
| FK Sarajevo Academy U17 | Tampere United | FC Mauerwerk | NK Lokomotiva Zagreb |
| AKA LASK OÖ U16 | SV Wörgl | FC International Leipzig | GNK Dinamo Zagreb |
| AKA SV Ried U16 | Ganzhou Ruishi | SV Straelen | Fortuna Sittard |
| NK Primorac Stobrec | Mardin 1969 Spor | SV Horn | HNK Rijeka |
| AKA Steiermark - Sturm Graz U16 | Bombonera Gifu | FC Wacker Innsbruck | Slaven Belupo Koprivnica |
| Hallescher FC U17 | SV Hönnepel-Niedermörmter | FC Chiasso | Genoa CFC |
| AKA Red Bull Salzburg U16 | FC Mauerwerk | BSV Schwarz-Weiß Rehden | Udinese Calcio |
| Nîmes Olympique U19 | NK Jedinstvo Bihac | Türkgücü München | FK Spartaks Jurmala |
| Olympique Lyon U19 | FC Hertha Wels II | 1.FC Phönix Lübeck | FK Partizan Belgrade |
