# Scrapsama

Scraper pour indexer des séries dans une base de données.

## Installation

### Option 1: Installation avec Docker (Recommandé)

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama

# Copier le fichier d'environnement exemple
cp .env.example .env

# Modifier le fichier .env avec vos paramètres si nécessaire
# nano .env

# Démarrer tous les services (MySQL, FlareSolverr, Scraper)
docker-compose up -d
```

### Option 2: Installation manuelle

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .[cli,database]
```

## Utilisation

### Avec Docker

```bash
# Accéder au conteneur scraper
docker-compose exec scraper bash

# Exécuter les commandes d'indexation
scrapsama-index
scrapsama-index-all
scrapsama-index-new

# Ou exécuter directement une commande
docker-compose exec scraper scrapsama-index
docker-compose exec scraper scrapsama-index-all
docker-compose exec scraper scrapsama-index-new
```

### Sans Docker

```bash
source venv/bin/activate
scrapsama-index
scrapsama-index-all
scrapsama-index-new
```

## Services Docker

Le setup Docker inclut les services suivants :

- **scraper** : Application principale de scraping
- **db** : Base de données MySQL 8.0
- **flaresolverr** : Service pour contourner la protection Cloudflare

### Commandes Docker utiles

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f scraper
docker-compose logs -f flaresolverr

# Reconstruire l'image du scraper après des modifications
docker-compose build scraper
docker-compose up -d scraper
```

## Configuration

### Avec Docker

Les variables d'environnement sont configurées dans le fichier `.env` pour docker-compose :

- `DB_HOST` : Hôte de la base de données (par défaut: `db`)
- `DB_PORT` : Port de la base de données (par défaut: `3306`)
- `DB_NAME` : Nom de la base de données (par défaut: `scrapsama`)
- `DB_USER` : Utilisateur de la base de données (par défaut: `scrapsama_user`)
- `DB_PASS` : Mot de passe de la base de données (par défaut: `scrapsama_pass`)
- `FLARESOLVERR_URL` : URL de FlareSolverr (par défaut: `http://flaresolverr:8191/v1`)

**Note** : Le fichier `.env` n'est pas copié dans le conteneur Docker. Les variables sont automatiquement injectées par docker-compose au démarrage du conteneur.

### FlareSolverr

FlareSolverr est disponible pour contourner la protection Cloudflare si nécessaire. **Par défaut, il n'est pas utilisé** car anime-sama.fr fonctionne normalement sans.

Pour activer FlareSolverr dans votre code :
```python
from scraper import AnimeSama, create_client

# Option 1 : Activer FlareSolverr pour AnimeSama
anime = AnimeSama("https://anime-sama.fr/", use_flaresolverr=True)

# Option 2 : Créer un client personnalisé
client = create_client(use_flaresolverr=True)
anime = AnimeSama("https://anime-sama.fr/", client=client)
```

### Sans Docker

Pour l'installation manuelle, créez un fichier `.env` à la racine du projet avec les mêmes variables (adaptez `DB_HOST` selon votre configuration locale).

## Licence

GPL-3.0
