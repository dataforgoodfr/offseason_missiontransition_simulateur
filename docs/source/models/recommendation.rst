Recommandation
==============

L'objectif de cette modélisation est d'estimer la pertinence d'une subvention pour une entreprise,
à partir de subventions attribuées et de subventions refusées.
Les subventions refusées sont simulée par des paires aléatoires de subventions et d'entreprises.

Le dataset d'entrainement est séparé en 5 sous ensembles pour évaluer la performance moyenne.
Chacun des sous ensemble est défini par le dernier chiffre du siren de l'entreprise.
Ainsi, une entreprise n'appartient qu'à un seul ensemble alors qu'une subvention peut apparaitre dans plusieurs ensemble.
Les modèles sont comparés à travers la métrique ROC, moyennée sur les différents sous-ensemble de validation.

Afin de collaborer sur les modèles d'entrainement, les différents modèles générés, ainsi que leurs performances, sont centralisées sur une plateforme de tracking : [neptune](https://app.neptune.ai/mission-transiton-simulateur/mission-transition-simulateur/experiments?split=tbl&dash=charts&viewId=standard-view).
Les identifiants pour se connecter à la plateforme sont disponible sur demande auprès des responsables du projet.

Afin d'entrainer un modèle, ajouter un fichier json dans `references/models`.
Ce fichier doit contenir les éléments suivants :
- model_type : le type de modèle à utiliser. La liste des mots clefs acceptés est définie dans cette [librairie](https://gitlab.com/cgoudet/cgoudetcore/-/blob/main/cgoudetcore/learning.py#L14).
- model_opt : la liste des paramètres du classifier.
- sample_weight : la colonne à utiliser comme poids (occurence).
- features : la liste des features à utiliser pour le modèle.
Après l'entrainement, le fichier json sera enrichi de meta données.
Si le modèle mérite d'être conservé pour l'historique, le fichier json pourra être versionné.

Pour lancer un entrainement, lancer la commande suivante.
Par défaut la routine ne sauvegarde pas l'expérience dans neptune.
```
python -m src.models.train_reco <config_name_without_extension> --save <0_or_1>
```

Modèles
-------

Baseline_rf
~~~~~~~~~~~
Ce modèle servira de baseline pour les futurs modèles.
Il se contente d'appliquer un random forest sur le code naf de l'établissement et sur les topic de la subvention, représentés sous forme onehot.
