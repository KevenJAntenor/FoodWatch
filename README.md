
# Project README

  

## Overview

Ce projet fournit une application Web permettant de récupérer un ensemble de données provenant de la ville de Montréal et d'offrir des

services à partir de ces données, comme gérer les demandes d'inspection et les données sur les infractions pour les établissements dans la ville de Montréal. Il comprend des fonctionnalités permettant aux utilisateurs de rechercher des contraventions(violations), de soumettre ou supprimer des demandes d'inspection, de créer des profils utilisateur et de recevoir des notifications sur les nouvelles violations. De plus, les administrateurs peuvent gérer les établissements, notamment mettre à jour les noms des établissements et les supprimer.

  

## Technologies utilisées

- **Python** : Le backend de l'application est principalement construit à l'aide de Python, avec le framework Flask pour créer des applications Web.

- **SQLite** : L'application utilise SQLite comme système de gestion de base de données pour stocker et gérer les données liées aux violations, aux établissements, aux utilisateurs et aux sessions.

- **HTML/CSS** : L'interface utilisateur frontend est développée en utilisant HTML et CSS.

- **JavaScript** : Certains éléments dynamiques du frontend sont implémentés à l'aide de JavaScript.

- **Flask** : Flask est utilisé pour acheminer les requêtes HTTP, restituer des modèles HTML et gérer les sessions utilisateur.

- **APScheduler** : Cette bibliothèque est utilisée pour planifier des tâches en arrière-plan, telles que la synchronisation des données.

- **YAML** : les fichiers YAML sont utilisés pour la configuration, comme les informations d'administration et les paramètres de messagerie.

- **Tweepy** : Tweepy est utilisé pour publier des notifications sur de nouvelles violations sur Twitter.

- **SMTP** : L'application utilise SMTP pour envoyer des notifications par e-mail aux utilisateurs.

  

## Features

### Apercu bref des User Features

- **Rechercher des violations** : les utilisateurs peuvent rechercher des violations en fonction de différents critères, tels que le nom de l'établissement, le propriétaire ou l'adresse.

- **Soumettre des demandes d'inspection** : les utilisateurs peuvent soumettre des demandes d'inspection en fournissant des détails tels que le nom de l'établissement, l'adresse, la date de la visite et la description du problème.

- **Créer des profils utilisateur** : les utilisateurs peuvent créer des profils en fournissant leur nom, leur adresse e-mail, leur mot de passe et en sélectionnant les établissements qu'ils souhaitent surveiller.

- **Recevoir des notifications** : les utilisateurs reçoivent des notifications par e-mail concernant les nouvelles violations détectées dans les établissements qu'ils surveillent.

- **Synchronisation des données** : L'application synchronise périodiquement les données d'une source externe (données ouvertes de Montréal) pour mettre à jour la base de données avec de nouvelles violations.

- **Notifications Twitter** : les administrateurs peuvent publier des notifications sur les nouvelles violations sur Twitter.

  

### Fonctionnalités d'administrateur

- **Gérer les établissements** : les administrateurs peuvent mettre à jour les noms des établissements et supprimer des établissements spécifiques.

- les informations sur la connexion en tant qu'adminitrateur sont dans `config_admin.yaml`

  
  

## Installation

  
  
  

1. Clonez le depot sur votre ordinateur local.

  

Dans le projet nouvellement créé, vous pouvez exécuter quelques commandes :

  

`source venv/bin/activate` ou

`.\venv\Scripts\activate`

  

Active l'environnement virtuel requis pour l'isolation des dépendances du projet.

  

[Read more about venv.](https://https://docs.python.org/3/library/venv.html)

  

2. Installez les dépendances requises à l'aide de `pip install -r requirements.txt`.

3. Mettez à jour les fichiers de configuration (`config_admin.yaml` et `config.yml`) avec vos paramètres appropriés.

4. Exécutez l'application Flask à l'aide de `flask run`.

  

## Utilisation

1. Accédez à l'application Web déployé via un navigateur Web : - [Flask Api App](https://flask-api-app-stable-ruypocr56a-nn.a.run.app/) 
2. Accédez à l'application Web locallement via un navigateur Web : http://127.0.0.1:5000

3. Les utilisateurs peuvent s'inscrire et se connecter pour accéder à des fonctionnalités telles que les violations de recherche, soumettre des demandes d'inspection et créer des profils.

4. Les administrateurs peuvent se connecter pour accéder à des fonctionnalités supplémentaires telles que la gestion des établissements et le déclenchement de la synchronisation des données.

  
  

## Contributeurs

- [Wu, Zhao Lin](https://gitlab.info.uqam.ca/wu.zhao_lin)

- [Antenor, Keven Jude](https://gitlab.info.uqam.ca/antenor.keven_jude)

  
  

## Reference

  

Offical Website

  

- [Flask](http://flask.pocoo.org/)

- [Flask Extension](http://flask.pocoo.org/extensions/)

- [Flask restplus](http://flask-restplus.readthedocs.io/en/stable/)

- [Flask-SQLalchemy](http://flask-sqlalchemy.pocoo.org/2.1/)

- [Flask-OAuth](https://pythonhosted.org/Flask-OAuth/)

- [elasticsearch-dsl](http://elasticsearch-dsl.readthedocs.io/en/latest/index.html)

- [gunicorn](http://gunicorn.org/)

  

Tutorial

  

- [Flask Overview](https://www.slideshare.net/maxcnunes1/flask-python-16299282)

- [In Flask we trust](http://igordavydenko.com/talks/ua-pycon-2012.pdf)

  

- [Wiki Page](https://github.com/tsungtwu/flask-example/wiki)
