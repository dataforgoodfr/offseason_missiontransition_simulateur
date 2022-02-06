Data pipeline
=============


ADEME
-----
Les données de l'ADEME permettent de relier un programme d'aide à une entreprise.
Le nom du projet servira à le relier à un projet de mission transition,
et le siret servira de base pour obtenir des features liées à l'entreprise bénéficiaire.
Puisque une subvention liée à un projet peut être octroyée plusieurs fois,
un identifiant unique est attribué à chaque projet.


Mission transition
------------------
Un identifiant unique est attribué à chaque subvention unique.
Enfin, l'unique notion utilisée pour l'apprentissage sera la liste des topic concernant la subvention.
Ces topics sont initialement transformés sous la forme one hot.


Sirene
------
L'API sirene permet d'obtenir des informations sur les établissements bénéficiant d'une subvention.
Dans un premier temps, seul le NAF de l'établissement est considéré, encodé par sa position dans le référentiel officiel.


Matching ADEME - mission transition
-----------------------------------
A l'heure actuelle, les subventions proposées sur le site de l'ADEME et celles sur mission transition ne correspondent pas.
Aucun id n'est présent pour relier les deux bases de données et le noms des subventions ne correspondent pas.
N'ayant pas les subvention octroyées par mission transition, on va chercher à identifier les correspondances entre les deux ensembles de subvention.

Dans un premier temps, on sélectionne toutes les subventions ADEME présentes au sein de mission transition.
On suppose que celles ci correspondent au subventions présentes dans la base ADEME, avec une formulation différente.
On liste ensuite toutes les combinaisons possibles contenant une subvention de chaque base de données.
Puis, on évalue la similarité des noms de chaque couple.
Cette similarité est évaluée avec le maximum entre trois métriques (partial_ratio, token_set_ratio, token_sort_ratio), décrites dans cet [article](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/).
Finalement, seuls les couples de subventions dont la similarité est supérieure à un seuil défini sont conservées.

A l'heure actuelle, aucune métrique ne permet d'estimer la pertinence et/ou la qualité du matching.
Cela sera nécessaire pour tester de nouvelles méthodes de matching.


Jointure
--------
En utilisant le matching de l'étape précédente, on peut relier les siret avec des subvention mission transition.


Augmentation
------------
Les données de l'ADEME ne représentent que les entreprises qui ont obtenu une subvention.
Les subventions refusées ne sont pas fournies.
Dans l'optique de faire un score de correspondance, il faut ajouter des refus.
Parmi toutes les combinaisons de subvention et d'enterprises (réalisées ou non),
on garde 5x plus de combinaisons non réalisées que réalisées.


Features finales
----------------
Finalement on crée un ensemble de variables qui dépendent à la fois des données d'entreprises et de la subvention.
Cette étape crée en plus les variables nécessaires à l'entrainement.
5 groupes sont créés en fonction du dernier chiffre du siren.
Les informations spécifiques à une entreprise ne sont donc pas mélangées entre l'ensemble d'entrainement et de validation.
