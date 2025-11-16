# Rapport des fonctionnalités du compilateur

## Pipeline de compilation

| Fonctionnalité | État | Commentaire |
| --- | --- | --- |
| Lexeur (espaces, `//`, `/* */`) | ✅ Implémentée | |
| Analyse syntaxique (descente récursive) | ✅ Implémentée | |
| Analyse sémantique (symboles, scopes, boucles) | ✅ Implémentée | |
| Optimisation AST – pliage de constantes | ✅ Implémentée | |
| Optimisation AST – élimination de code mort | ⚠️ Partielle | Supprime `drop` constants et branches déterministes |
| Optimisation ASM | ❌ Non implémentée | |
| Génération de code MSM | ✅ Implémentée | |

## Interface CLI & outils

| Fonctionnalité | État | Commentaire |
| --- | --- | --- |
| Entrées (fichier, `--string`, `--stdin`) | ✅ Implémentée | |
| Sorties (fichier, `--stdout`) | ✅ Implémentée | |
| Mode verbeux `--debug` | ⚠️ Partiel | Logger pas invoqué partout |
| Exemples prêts à l’emploi (`examples/`) | ✅ Implémentée | |
| Suite de tests Pytest | ✅ Implémentée | |

## Gestion des erreurs

| Fonctionnalité | État | Commentaire |
| --- | --- | --- |
| `CompilationError` avec ligne/colonne | ✅ Implémentée | |
| Impression de la ligne fautive | ⚠️ Partielle | Manque sur quelques cas |
| Classes d’erreurs dédiées (LexerError, …) | ❌ Non implémentées | |

## Opérateurs unaires

| Opérateur | État | Commentaire |
| --- | --- | --- |
| `+` (no-op) | ✅ Fonctionne | |
| `-` (négation) | ✅ Fonctionne | |
| `!` | ✅ Fonctionne | |
| `*` (déréférencement) | ✅ Fonctionne | |
| `&` (adresse) | ✅ Fonctionne | |
| `++` suffixe | ✅ Fonctionne | Limité aux identifiants |
| `--` suffixe | ✅ Fonctionne | Limité aux identifiants |

## Opérateurs binaires

| Opérateur | État | Commentaire |
| --- | --- | --- |
| `+`, `-`, `*`, `/`, `%` | ✅ Fonctionne | Division/modulo tronquées façon C |
| `==`, `!=` | ✅ Fonctionne | |
| `<`, `<=`, `>`, `>=` | ✅ Fonctionne | |
| `&&`, `||` | ✅ Fonctionne | Résultat normalisé à 0/1 |

## Autres expressions

| Élément | État | Commentaire |
| --- | --- | --- |
| Constantes entières | ✅ Fonctionne | |
| Parenthèses | ✅ Fonctionne | |
| Identifiants | ✅ Fonctionne | |
| Appels de fonction | ✅ Fonctionne | |
| Indexation via `ptr[i]` | ✅ Fonctionne | Transformé en addition + déréf |

## Conditionnelles

| Élément | État | Commentaire |
| --- | --- | --- |
| `if` | ✅ Fonctionne | |
| `else` | ✅ Fonctionne | |

## Boucles et contrôle

| Élément | État | Commentaire |
| --- | --- | --- |
| `while` | ✅ Fonctionne | |
| `do … while` | ✅ Fonctionne | |
| `for` | ✅ Fonctionne | Déclarations et étapes supportées |
| `break` | ✅ Fonctionne | Vérifie présence dans une boucle |
| `continue` | ✅ Fonctionne | Gère cibles personnalisées |

## Variables & scopes

| Élément | État | Commentaire |
| --- | --- | --- |
| Déclarations `int` (simples ou multiples) | ✅ Fonctionne | |
| Initialisation (`int a = 5;`) | ✅ Fonctionne | |
| Portée par blocs (`{}`) | ✅ Fonctionne | Piles de scopes dans `SymbolTable` |
| Portée des fonctions | ✅ Fonctionne | Paramètres réservés automatiquement |
| Assignation `=` | ✅ Fonctionne | Vérifie cibles (`ref`/`deref`) |

## Fonctions

| Élément | État | Commentaire |
| --- | --- | --- |
| Définition (`int foo(...) {}`) | ✅ Fonctionne | Empêche doublons & nom `start` |
| Appel | ✅ Fonctionne | Préparation des arguments |
| Arguments multiples | ✅ Fonctionne | |
| Retour `return expr;` | ✅ Fonctionne | Imposé dans contexte fonction |

## Pointeurs & tableaux simulés

| Élément | État | Commentaire |
| --- | --- | --- |
| Déclaration de pointeur (`int *p`) | ✅ Fonctionne | |
| Déréférencement `*p` | ✅ Fonctionne | |
| Adresse `&var` | ✅ Fonctionne | Calcule BP relatif |
| Indexation `p[i]` / `p[-1]` | ✅ Fonctionne | Basé sur addition + déréf |
| Parcours de « tableaux » consécutifs | ⚠️ Partiel | Requiert slots manuels |

## Entrées / sorties & pseudo-bibliothèque

| Élément | État | Commentaire |
| --- | --- | --- |
| `debug expr;` | ✅ Fonctionne | Génère `dbg` |
| `send`, `recv` | ❌ Non implémentés | Tokens sans support AST |
| `malloc`, `free`, `print` | ❌ Non implémentés | |

## Bonus & divers

| Élément | État | Commentaire |
| --- | --- | --- |
| Commentaires `//` et `/* */` | ✅ Fonctionne | Gestion d’erreurs sur fin manquante |
| Fichiers d’exemples pédagogiques | ✅ Fait | 5 programmes démonstratifs |
