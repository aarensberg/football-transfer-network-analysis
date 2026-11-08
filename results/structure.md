# A1. Structure du réseau

Généré par `uv run python -m ftna.structure`.

- Nœuds : 12,009 ; arêtes orientées : 450,217 ; arêtes non orientées : 357,567 ; densité orientée : 3.12e-03.
- Clubs uniquement vendeurs (degré entrant nul) : 232 ; uniquement acheteurs (degré sortant nul) : 137.

## Degrés et forces

| mesure | moyenne | médiane | q90 | q99 | max |
|---|---|---|---|---|---|
| in_degree | 37.5 | 28 | 87 | 134 | 202 |
| out_degree | 37.5 | 27 | 88 | 145 | 278 |
| in_strength | 76.6 | 56 | 177 | 273 | 442 |
| out_strength | 76.6 | 54 | 179 | 298 | 926 |

Corrélation de Spearman entre degré entrant et sortant : 0.908 ; entre force entrante et sortante : 0.851.

Figure : `results/figures/degree_ccdf.pdf`.

## Réciprocité

- Réciprocité (arêtes) : 0.412, contre 3.12e-03 attendu sous G(n, m) orienté.
- Part des transferts sur des couples réciproques : 0.552.

## Clustering (graphe non orienté, non pondéré)

- Clustering moyen observé : 0.336 ; transitivité : 0.252.
- G(n, m) de même taille : espérance 4.96e-03.
- Modèle de configuration (mêmes degrés, graine 42, 354,815 arêtes après nettoyage) : clustering moyen 0.015, transitivité 0.015.

## Assortativité de degré

- out→in (vendeur→acheteur) : 0.490
- in→in : 0.459
- out→out : 0.526
- non orienté : 0.501
