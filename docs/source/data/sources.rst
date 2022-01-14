Sources de données
==================

ADEME
-----
L'ADEME est une agence gouvernementale pour l'environnement.
Elle finance des projects pour la transition écologique.
L'ADEME met à disposition une API pour pour télécharger près de 20k subventions attribuées, avec le siret de leur bénéficiaire.
Ces données vont permettre d'identifier le profil d'entreprise pour chaque type de subvention.


L'API fournit un unique fichier excel avec différentes informations.
Les informations suivantes sont récupérées.
- `siret` : siret du bénéficiaire
- `siren` : siren du bénéficiaire (extrait du siret)
- `denomination` : dénomination du bénéficiaire
- `montant` : montant du financement
- `nature` : nature du financement
- `object` : nom du programme de subvention.

L'ensemble des lignes n'ayant pas un siret valide (au moins 11 chiffres) sont retirés; soit 10% des données.

Les données finales sont stockées dans `data/interim/ademe.parquet`.

mission transition
------------------


SIRENE
------
