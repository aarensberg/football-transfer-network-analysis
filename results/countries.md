# A6. Réseau agrégé par pays

Généré par `uv run python -m ftna.countries`. Table complète : `results/tables/country_flows.csv`.

- Transferts entre clubs de pays connus : 917,518 ; part **domestique** : 84.9%.
- Part des transferts entre deux clubs de la **même ligue la saison du transfert** : 35.6% (ligue connue pour les deux clubs dans 56.8% des transferts) ; avec la dernière ligue connue : 33.8%.
- Transferts internationaux : 138,785 ; dont entre pays du même bloc de communautés (A5) : 31.2%.
- Pays : 110 ; couples de pays reliés : 7,131.

## Pays les plus fermés et les plus ouverts (≥ 20 clubs)

| pays | clubs | part domestique | pays partenaires |
|---|---|---|---|
| Iran | 140 | 0.930 | 83 |
| Germany | 2,238 | 0.903 | 101 |
| Hongkong | 54 | 0.893 | 70 |
| Italy | 769 | 0.887 | 102 |
| Türkiye | 387 | 0.872 | 85 |
| Chinese Taipei | 22 | 0.862 | 19 |
| Finland | 301 | 0.844 | 97 |
| Algeria | 46 | 0.840 | 63 |
| Estonia | 139 | 0.840 | 69 |
| Austria | 688 | 0.838 | 87 |

| pays | clubs | part domestique | pays partenaires |
|---|---|---|---|
| Lithuania | 33 | 0.374 | 83 |
| Cyprus | 45 | 0.414 | 94 |
| Azerbaijan | 21 | 0.429 | 84 |
| Croatia | 57 | 0.459 | 87 |
| Uruguay | 40 | 0.477 | 77 |
| Romania | 52 | 0.480 | 98 |
| Paraguay | 24 | 0.483 | 67 |
| Slovenia | 67 | 0.488 | 82 |
| Australia | 55 | 0.513 | 88 |
| Slovakia | 81 | 0.517 | 92 |

## Soldes internationaux

| pays | exportés | importés | solde (exp. − imp.) |
|---|---|---|---|
| England | 7,148 | 4,362 | 2,786 |
| France | 6,019 | 3,681 | 2,338 |
| Brazil | 4,767 | 3,340 | 1,427 |
| Italy | 5,549 | 4,452 | 1,097 |
| Argentina | 4,279 | 3,426 | 853 |
| Uruguay | 2,359 | 1,554 | 805 |
| Croatia | 2,847 | 2,093 | 754 |
| Ukraine | 2,014 | 1,333 | 681 |
| Serbia | 3,167 | 2,676 | 491 |
| Colombia | 2,036 | 1,557 | 479 |

| pays | exportés | importés | solde (exp. − imp.) |
|---|---|---|---|
| Türkiye | 2,109 | 3,579 | -1,470 |
| Austria | 2,710 | 3,736 | -1,026 |
| United States | 1,778 | 2,693 | -915 |
| Switzerland | 2,117 | 2,767 | -650 |
| Cyprus | 2,037 | 2,654 | -617 |
| Saudi Arabia | 789 | 1,332 | -543 |
| Scotland | 1,540 | 2,035 | -495 |
| Poland | 2,206 | 2,689 | -483 |
| Luxembourg | 644 | 1,101 | -457 |
| Thailand | 707 | 1,146 | -439 |

Figure : `results/figures/country_balance.pdf`.

## Pays les plus connectés (nombre de pays partenaires)

| pays | pays partenaires | exportés | importés |
|---|---|---|---|
| Spain | 103 | 4,597 | 4,484 |
| Italy | 102 | 5,549 | 4,452 |
| Portugal | 102 | 4,179 | 3,762 |
| Malta | 102 | 723 | 1,058 |
| Germany | 101 | 6,232 | 6,229 |
| Brazil | 101 | 4,767 | 3,340 |
| United States | 101 | 1,778 | 2,693 |
| Sweden | 99 | 2,032 | 2,045 |
| Romania | 98 | 1,758 | 2,016 |
| Finland | 97 | 1,081 | 1,232 |

## Principaux corridors internationaux

| de | vers | transferts | même bloc (A5) |
|---|---|---|---|
| England | Scotland | 1,332 | oui |
| France | Belgium | 900 | oui |
| Brazil | Portugal | 888 | oui |
| Germany | Austria | 847 |  |
| Austria | Germany | 755 |  |
| Scotland | England | 737 | oui |
| Argentina | Chile | 685 | oui |
| Czech Republic | Slovakia | 660 | oui |
| Germany | Türkiye | 619 |  |
| England | Wales | 595 | oui |
| England | Spain | 584 |  |
| Slovakia | Czech Republic | 573 | oui |
| Slovenia | Austria | 542 |  |
| France | Switzerland | 525 |  |
| Belgium | France | 522 | oui |
| Uruguay | Argentina | 501 | oui |
| Serbia | Bosnia-Herzegovina | 497 | oui |
| Portugal | Brazil | 491 | oui |
| Belgium | Netherlands | 480 | oui |
| Croatia | Slovenia | 471 | oui |
| Chile | Argentina | 463 | oui |
| Italy | Switzerland | 454 |  |
| Italy | Spain | 447 |  |
| Croatia | Bosnia-Herzegovina | 445 | oui |
| France | England | 439 |  |
