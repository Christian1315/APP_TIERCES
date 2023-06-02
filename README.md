# README

## Pourquoi Fedrelay 

APP TIERCES, est un ensemble des APPS tierces relatives à la plateforme FEDRELAY.COM. Elles sont comme des microservices accompagnant la plateforme.

## Development Technology
- Django

## BASE DE DONNEE
- ELLE N'EXIGE AU CUNE BASE DE DONNEE


## Execution Procedure

Accéder au projet
```bash
$ git clone https://gitlab.com/fedrelay/back.git

$ cd back 

```
Installer les dépendances
```bash

==== INSATALLATION D\'UN NOUVEL ENVIRONNEMENT DJANGO ============
$ python -m venv env

==== INSATALLATION DES AUTRES DEPENDANCES  ============
$ env\Scripts\activate
$ python -m pip install Django
$ python install -r requirements.txt 

```
PARAMETRAGE
```
Accédez à module>_env.py puis changer la variable __BASE_URL par le BASE_URL de l'API fedrelay

Ex: __BASE_URL = "https://api.fedrelay.com"(Sans slash à la fin) ##Si c'est l'api en ligne que vous prefez

ou

__BASE_URL = "http://localhost:3000" ##Si vous avez une version local de l'api fedrelay pour les tests

```
Démarrer le serveur en développement
```bash

==== DEMARRAGE REEL DU PROJET ============
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
