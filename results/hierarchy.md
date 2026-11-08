# A9. Hiérarchie des flux

Généré par `uv run python -m ftna.hierarchy`. Valeur marchande des clubs dans `club_league` (saison du transfert), transferts du graphe 2010–2023 ; seuls les transferts dont les deux clubs ont une valeur > 0 sont comparés.

## Saison = année du transfert

| catégorie | transferts valorisés | couverture | vers moins valorisé | vers plus valorisé | médiane log10(acheteur/vendeur) |
|---|---|---|---|---|---|
| tous | 324,369 | 0.352 | 0.613 | 0.384 | -0.119 |
| définitif payé | 24,078 |  | 0.354 | 0.645 | 0.206 |
| définitif sans montant | 169,088 |  | 0.582 | 0.414 | -0.071 |
| prêt | 70,048 |  | 0.854 | 0.145 | -0.479 |
| type inconnu | 61,155 |  | 0.523 | 0.473 | -0.025 |

## Robustesse : saison précédente

| catégorie | transferts valorisés | couverture | vers moins valorisé | vers plus valorisé | médiane log10(acheteur/vendeur) |
|---|---|---|---|---|---|
| tous | 307,264 | 0.334 | 0.605 | 0.392 | -0.110 |
| définitif payé | 23,712 |  | 0.386 | 0.614 | 0.159 |
| définitif sans montant | 162,453 |  | 0.574 | 0.421 | -0.064 |
| prêt | 65,129 |  | 0.841 | 0.158 | -0.470 |
| type inconnu | 55,970 |  | 0.510 | 0.486 | -0.012 |

Figure : `results/figures/value_ratio.pdf`.
