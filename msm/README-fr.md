[🇬🇧 Read the English version](./README.md)

# MSM - Mini Stack Machine

Simulateur d'une machine à pile minimale avec un jeu d'instructions simple.

Prend en entrée un fichier texte contenant le code assembleur à exécuter (ou via l'entrée standard), et affiche le résultat sur la console.

## Attribution
Ce simulateur a été créé par [Thomas LAVERGNE](https://perso.limsi.fr/lavergne/).

Lien de téléchargement original : [https://perso.limsi.fr/lavergne/app4-compil/msm.tgz](https://perso.limsi.fr/lavergne/app4-compil/msm.tgz)

## Compilation
Pour compiler le programme MSM, vous pouvez utiliser soit `make`, soit un compilateur C comme `gcc`.

**Avec Make :** Exécutez la commande suivante dans le terminal :
```bash
make msm
```

**Avec GCC :** Si `make` n'est pas disponible, vous pouvez compiler le programme manuellement avec :
```bash
gcc -o msm msm.c
```

## Exécution

Pour exécuter le programme MSM, vous pouvez utiliser la commande suivante dans le terminal :
```bash
./msm <nom_du_fichier_asm>
```
ou via l'entrée standard :
```bash
cat <nom_du_fichier_asm> | ./msm
```

**Remarque :** Le programme doit inclure une étiquette `.start` pour indiquer le point d'entrée de l'exécution.

### Mode Débogage
Vous pouvez activer le mode débogage avec l'option `-d`. Cela affichera des informations détaillées sur l'exécution du programme, y compris l'instruction en cours et l'état de la pile. Utilisez `-d` plusieurs fois pour plus de verbosité.

Exemple :
```bash
./msm -d <nom_du_fichier_asm>
```

### Taille de la Mémoire
La taille de la mémoire par défaut est de 64 KB. Vous pouvez l'augmenter à 16 MB avec l'option `-m`.

Exemple :
```bash
./msm -m <nom_du_fichier_asm>
```

### Gestion des Erreurs
Le simulateur MSM fournit des messages d'erreur détaillés pour des problèmes tels que :
- Étiquettes non définies.
- Instructions invalides.
- Nombre d'arguments incorrect.
- Échecs d'allocation mémoire.

## Jeu d'instructions

### Contrôle du programme

#### halt
Termine l'exécution du programme.

### Manipulation de la pile

#### drop [int]
Supprime les n éléments au sommet de la pile.

#### dup
Empile une copie de l'élément au sommet de la pile.

#### swap
Inverse les deux éléments au sommet de la pile.

#### push [int]
Empile une constante entière au sommet de la pile.

#### get [int]
Empile une copie de la N-ième valeur depuis la base de la pile au sommet de celle-ci.

#### set [int]
Dépile la valeur au sommet de la pile et l'affecte à la N-ième valeur depuis la base de la pile.

### Accès à la mémoire

#### read
Dépile une adresse mémoire, puis empile le contenu de la case mémoire à cette adresse.

#### write
Dépile une valeur puis une adresse. Affecte la valeur à la case mémoire indiquée par l'adresse.

### Arithmétique et logique

#### add / sub / mul / div / mod
Dépile deux valeurs du haut de la pile, applique l'opération correspondante et empile le résultat.  
Attention, pour réaliser l'opération A-B par exemple, la valeur de A doit être empilée en premier suivie de la valeur de B.

#### not
Négation logique du sommet de la pile. Dépile une valeur puis empile 0 si cette dernière est non nulle et 1 sinon.

#### and / or
Réalise l'opération logique entre les deux valeurs au sommet de la pile.

### Comparaisons

#### cmpeq / cmpne / cmplt / cmple / cmpgt / cmpge
Dépile deux valeurs du sommet de la pile et empile le résultat de la comparaison des deux :  
- `cmpeq` -> A == B  
- `cmpne` -> A != B  
- `cmplt` -> A < B  
- `cmple` -> A <= B  
- `cmpgt` -> A > B  
- `cmpge` -> A >= B  

### Branchements

#### jump [label]
Saut inconditionnel à l'adresse indiquée.

#### jumpt / jumpf [label]
Saut conditionnel. Dépile une valeur entière du sommet de la pile, si elle est différente (resp. égale) de zéro, saute à l'adresse indiquée, sinon continue l'exécution à l'instruction suivante.

### Appels de fonctions

#### prep [label]
Prépare un appel à la fonction [label]. Réserve deux emplacements au sommet de la pile.

#### call [int]
Réalise l'appel à la fonction préparée par une instruction `prep` dont les [int] arguments ont été empilés.

#### ret
Retourne depuis une fonction en renvoyant la valeur au sommet de la pile. Réinitialise la pile dans l'état où elle était au moment de l'instruction `prep` correspondante et empile la valeur résultat.

#### resn [int]
Réserve [int] emplacements sur la pile. Typiquement pour les variables locales.

### Communication

#### send
Dépile la valeur au sommet de la pile et l'envoie sur la console sous la forme d'un octet interprété comme un caractère.

#### recv
Empile un entier sur la pile correspondant au prochain octet lu depuis la console.

#### dbg
Dépile la valeur au sommet de la pile et l'affiche comme un entier sur la console.
