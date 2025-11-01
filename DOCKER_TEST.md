# Test du Setup Docker

## Prérequis

- Docker et Docker Compose installés
- Port 3306, 8191 disponibles (ou modifiés dans `.env`)

## Démarrage des services

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Démarrer tous les services
docker compose up -d

# Vérifier que tous les services sont démarrés
docker compose ps
```

## Vérification de FlareSolverr

```bash
# Vérifier que FlareSolverr est accessible
curl http://localhost:8191/health

# Devrait retourner: {"status":"ok"}
```

## Vérification de la base de données

```bash
# Accéder au conteneur MySQL
docker compose exec db mysql -u scrapsama_user -pscrapsama_pass scrapsama

# Lister les tables (après avoir indexé des séries)
SHOW TABLES;

# Quitter MySQL
exit
```

## Utilisation du scraper

```bash
# Accéder au conteneur scraper
docker compose exec scraper bash

# À l'intérieur du conteneur, exécuter les commandes d'indexation
scrapsama-index       # Indexer une série spécifique
scrapsama-index-all   # Indexer toutes les séries
scrapsama-index-new   # Indexer les nouveaux épisodes

# Ou directement depuis l'hôte
docker compose exec scraper scrapsama-index
```

## Test de l'intégration FlareSolverr

```bash
# À l'intérieur du conteneur scraper
docker compose exec scraper python3 -c "
import os
from scraper.flaresolverr import create_client
import asyncio

async def test():
    client = create_client(use_flaresolverr=True)
    print(f'FlareSolverr URL: {os.getenv(\"FLARESOLVERR_URL\")}')
    print('Client créé avec succès!')
    await client.aclose()

asyncio.run(test())
"
```

## Arrêt des services

```bash
# Arrêter les services
docker compose down

# Arrêter et supprimer les volumes (données de la base de données)
docker compose down -v
```

## Logs

```bash
# Voir les logs de tous les services
docker compose logs -f

# Voir les logs d'un service spécifique
docker compose logs -f scraper
docker compose logs -f flaresolverr
docker compose logs -f db
```

## Résolution de problèmes

### Le scraper ne peut pas se connecter à la base de données

1. Vérifier que le service DB est démarré : `docker compose ps`
2. Vérifier les logs : `docker compose logs db`
3. Attendre que MySQL soit complètement initialisé (peut prendre 30-60 secondes)

### FlareSolverr n'est pas accessible

1. Vérifier que le service est démarré : `docker compose ps`
2. Vérifier les logs : `docker compose logs flaresolverr`
3. Tester l'endpoint de santé : `curl http://localhost:8191/health`

### Erreurs SSL lors du build

Si vous rencontrez des erreurs SSL lors de la construction de l'image Docker, cela est géré automatiquement dans le Dockerfile avec les options `--trusted-host`.
