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
La plateforme mission transition propose un grand nombre de programmes de subvention, incluant leurs critères d'elligibilité.
L'objectif du projet est de recommander des programmes de financement pertinents à des entreprises visitant le site.

Mission transition propose une API qui propose l'ensemble des missions avec des détails.
La pipeline sauvegarde les missions ainsi que plusieurs caractéristiques des programmes dans un fichier :
`data/interim/mission_transition.parquet`.

SIRENE
------
L'API sirene est l'API du gouvernement qui propose des informations administratives sur les entreprises.
Ces informations peuvent servir à estimer le profil des entreprises qui recoivent des subventions.

Chaque siret unique présent dans le fichier `ademe` est requêté et les données de l'établissement sauvegardées dans une base sqlite : `data/interim/mission-transition.sql`.
La pipeline permet de mettre à jour uniquement les nouveaux siret lors de mise à jour du fichier ADEME.
