# Scrapsama

Scraper pour indexer des séries dans une base de données.

## Installation

### Installation standard

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Installation avec Docker

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama
```

Créez un fichier `.env` avec vos paramètres de base de données :
```bash
cp .env.example .env
# Éditez .env avec vos identifiants
```

Puis lancez avec Docker :
```bash
# Build l'image
docker build -t scrapsama .

# Ou utilisez docker-compose
docker-compose up -d
```

## Utilisation

### Utilisation standard

```bash
source scrapsama-env/bin/activate
scrapsama-index
scrapsama-index-all
scrapsama-index-new
```

### Utilisation avec Docker

```bash
# Indexer une série spécifique (interactif)
docker run --rm -it --env-file .env scrapsama scrapsama-index

# Indexer toutes les séries
docker run --rm --env-file .env scrapsama scrapsama-index-all

# Indexer les nouveaux épisodes
docker run --rm --env-file .env scrapsama scrapsama-index-new
```

Avec docker-compose :
```bash
# Commande par défaut (scrapsama-index-new)
docker-compose up

# Pour une autre commande
docker-compose run --rm scraper scrapsama-index
docker-compose run --rm scraper scrapsama-index-all
```

## Configuration

Le scraper nécessite une connexion à une base de données MySQL. Configurez les variables d'environnement suivantes dans un fichier `.env` :

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=scrapsama
DB_USER=root
DB_PASS=password
```

## Licence

GPL-3.0
