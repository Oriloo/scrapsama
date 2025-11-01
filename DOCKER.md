# Docker Guide pour Scrapsama

Ce guide explique comment utiliser Scrapsama avec Docker.

## Prérequis

- Docker installé sur votre système
- Docker Compose (optionnel mais recommandé)
- Une base de données MySQL accessible (elle restera externe au conteneur)

## Configuration

### 1. Fichier .env

Créez un fichier `.env` à la racine du projet avec vos paramètres de base de données :

```bash
DB_HOST=mysql.example.com
DB_PORT=3306
DB_NAME=scrapsama
DB_USER=votre_utilisateur
DB_PASS=votre_mot_de_passe
```

**Important :** Si votre base de données MySQL est sur votre machine locale et vous utilisez Docker, utilisez :
- `host.docker.internal` (sur Mac/Windows) ou
- L'adresse IP de votre machine (sur Linux) comme `DB_HOST`

## Utilisation

### Option 1 : Docker simple

#### Build l'image

```bash
docker build -t scrapsama .
```

#### Exécuter les commandes

```bash
# Indexer une série spécifique (mode interactif)
docker run --rm -it --env-file .env scrapsama scrapsama-index

# Indexer toutes les séries
docker run --rm --env-file .env scrapsama scrapsama-index-all

# Indexer les nouveaux épisodes (commande par défaut)
docker run --rm --env-file .env scrapsama scrapsama-index-new
```

#### Explications des options

- `--rm` : Supprime le conteneur après exécution
- `-it` : Mode interactif (nécessaire pour `scrapsama-index`)
- `--env-file .env` : Charge les variables d'environnement depuis le fichier .env

### Option 2 : Docker Compose (Recommandé)

#### Configuration

Le fichier `docker-compose.yml` est déjà configuré. Il lit automatiquement les variables d'environnement depuis votre fichier `.env`.

#### Exécuter les commandes

```bash
# Commande par défaut (scrapsama-index-new)
docker-compose up

# Ou en arrière-plan
docker-compose up -d

# Pour une autre commande
docker-compose run --rm scraper scrapsama-index
docker-compose run --rm scraper scrapsama-index-all

# Arrêter les conteneurs
docker-compose down
```

### Option 3 : Variables d'environnement inline

Si vous ne voulez pas créer de fichier `.env` :

```bash
docker run --rm \
  -e DB_HOST=mysql.example.com \
  -e DB_PORT=3306 \
  -e DB_NAME=scrapsama \
  -e DB_USER=votre_utilisateur \
  -e DB_PASS=votre_mot_de_passe \
  scrapsama scrapsama-index-new
```

## Configuration avancée

### Personnaliser le docker-compose

Créez un fichier `docker-compose.override.yml` :

```yaml
version: '3.8'

services:
  scraper:
    environment:
      - DB_HOST=votre-host
      - DB_PORT=3306
      - DB_NAME=scrapsama
      - DB_USER=votre-utilisateur
      - DB_PASS=votre-mot-de-passe
    # Pour exécuter périodiquement (avec un cron externe ou Kubernetes CronJob)
    command: scrapsama-index-new
```

### Exécution périodique avec cron

Pour exécuter automatiquement l'indexation des nouveaux épisodes :

```bash
# Ajouter dans votre crontab (crontab -e)
# Exécute toutes les heures
0 * * * * cd /chemin/vers/scrapsama && docker-compose run --rm scraper scrapsama-index-new
```

### Utiliser un fichier .env monté

Si vous préférez monter votre fichier `.env` directement :

```yaml
services:
  scraper:
    volumes:
      - ./.env:/app/.env:ro
```

## Dépannage

### Impossible de se connecter à la base de données

1. Vérifiez que MySQL accepte les connexions externes
2. Vérifiez votre `DB_HOST` :
   - Pour MySQL sur la machine hôte : utilisez `host.docker.internal` (Mac/Windows)
   - Pour Linux : utilisez l'IP de votre machine (pas `localhost`)
3. Vérifiez les règles de pare-feu

### Erreur SSL pendant le build

L'erreur SSL peut survenir dans certains environnements CI/CD. Si vous rencontrez ce problème, décommentez cette ligne dans le Dockerfile :

```dockerfile
ENV PIP_TRUSTED_HOST=pypi.org pypi.python.org files.pythonhosted.org
```

## Architecture

- **Conteneur Python** : Contient le scraper et toutes ses dépendances
- **Base de données** : Reste externe, accessible via les variables d'environnement
- **Données** : Aucune donnée n'est stockée dans le conteneur (stateless)

## Sécurité

- Le fichier `.env` est exclu du build Docker (via `.dockerignore`)
- Ne commitez jamais votre fichier `.env` avec des vraies credentials
- Utilisez des secrets Docker ou des variables d'environnement sécurisées en production

## Support

Pour toute question, ouvrez une issue sur GitHub.
