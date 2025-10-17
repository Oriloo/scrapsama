# Guide d'utilisation : Indexation des nouveaux épisodes

## Introduction

Ce guide explique comment utiliser la nouvelle fonctionnalité d'indexation automatique des nouveaux épisodes ajoutés sur anime-sama.fr.

## Prérequis

1. MySQL installé et configuré
2. Variables d'environnement configurées (voir `.env.example`)
3. Package installé avec les dépendances : `pip install -e ".[cli,database]"`

## Utilisation de base

### Commande CLI

```bash
scrapsama-index-new
```

Cette commande va :
1. Se connecter à la base de données
2. Récupérer la liste des nouveaux épisodes depuis anime-sama.fr
3. Pour chaque nouvel épisode :
   - Rechercher la série complète
   - Indexer la série (si nécessaire)
   - Indexer la saison
   - Indexer tous les épisodes de cette saison
4. Afficher un résumé des opérations

### Avec Docker

```bash
docker compose run --rm app scrapsama-index-new
```

## Automatisation

### Option 1 : Crontab (Linux/macOS)

Éditez votre crontab :
```bash
crontab -e
```

Ajoutez une ligne pour exécuter la commande régulièrement :

```bash
# Toutes les 6 heures
0 */6 * * * cd /chemin/vers/scrapsama && docker compose run --rm app scrapsama-index-new >> /var/log/scrapsama-index.log 2>&1

# Tous les jours à 2h du matin
0 2 * * * cd /chemin/vers/scrapsama && docker compose run --rm app scrapsama-index-new >> /var/log/scrapsama-index.log 2>&1

# Toutes les heures
0 * * * * cd /chemin/vers/scrapsama && docker compose run --rm app scrapsama-index-new >> /var/log/scrapsama-index.log 2>&1
```

### Option 2 : Systemd Timer (Linux)

**1. Créer le service :**

Fichier `/etc/systemd/system/scrapsama-index-new.service` :
```ini
[Unit]
Description=Index new anime episodes from anime-sama.fr
After=network.target docker.service mysql.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/chemin/vers/scrapsama
ExecStart=/usr/bin/docker compose run --rm app scrapsama-index-new
User=votre-utilisateur
Group=votre-groupe
StandardOutput=journal
StandardError=journal
```

**2. Créer le timer :**

Fichier `/etc/systemd/system/scrapsama-index-new.timer` :
```ini
[Unit]
Description=Run scrapsama-index-new every 6 hours
Requires=scrapsama-index-new.service

[Timer]
OnBootSec=15min
OnUnitActiveSec=6h
AccuracySec=1min

[Install]
WantedBy=timers.target
```

**3. Activer et démarrer le timer :**
```bash
sudo systemctl daemon-reload
sudo systemctl enable scrapsama-index-new.timer
sudo systemctl start scrapsama-index-new.timer

# Vérifier le statut
sudo systemctl status scrapsama-index-new.timer

# Voir les logs
sudo journalctl -u scrapsama-index-new.service -f
```

### Option 3 : Script shell avec boucle

Créer un script `watch-new-episodes.sh` :
```bash
#!/bin/bash

# Intervalle en secondes (6 heures = 21600 secondes)
INTERVAL=21600

while true; do
    echo "=== $(date) ==="
    echo "Indexing new episodes..."
    
    docker compose run --rm app scrapsama-index-new
    
    echo "Waiting $INTERVAL seconds until next run..."
    sleep $INTERVAL
done
```

Rendre le script exécutable et le lancer en arrière-plan :
```bash
chmod +x watch-new-episodes.sh
nohup ./watch-new-episodes.sh >> /var/log/scrapsama-watch.log 2>&1 &
```

## Utilisation en Python

Si vous souhaitez intégrer cette fonctionnalité dans votre propre code Python :

### Exemple 1 : Récupérer les nouveaux épisodes

```python
import asyncio
from scraper import AnimeSama

async def main():
    anime_sama = AnimeSama("https://anime-sama.fr/")
    episodes = await anime_sama.new_episodes()
    
    print(f"Trouvé {len(episodes)} nouveaux épisodes :")
    for ep in episodes:
        print(f"  - {ep.serie_name}")
        print(f"    Descriptif : {ep.descriptive}")
        print(f"    Langue : {ep.language}")
        print(f"    URL : {ep.page_url}")
        print()

asyncio.run(main())
```

### Exemple 2 : Indexer les nouveaux épisodes

```python
import asyncio
from scraper import AnimeSama, Database, index_serie, index_season, index_episode

async def index_new_episodes():
    # Initialiser
    anime_sama = AnimeSama("https://anime-sama.fr/")
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Récupérer les nouveaux épisodes
    episodes = await anime_sama.new_episodes()
    
    # Traiter chaque épisode
    for release in episodes:
        print(f"Traitement de {release.serie_name}...")
        
        # Rechercher la série
        catalogues = await anime_sama.search(release.serie_name)
        if not catalogues:
            continue
        
        catalogue = catalogues[0]
        
        # Indexer la série
        serie_id = index_serie(catalogue, db)
        if not serie_id:
            continue
        
        # Indexer les saisons et épisodes
        seasons = await catalogue.seasons()
        for season in seasons:
            season_id = index_season(season, serie_id, db)
            if not season_id:
                continue
            
            episodes = await season.episodes()
            for episode in episodes:
                index_episode(episode, season_id, db)
    
    db.close()
    print("Indexation terminée !")

asyncio.run(index_new_episodes())
```

## Surveillance et débogage

### Consulter les logs

Les échecs d'indexation sont enregistrés dans la table `failures` de la base de données :

```sql
-- Voir les échecs récents
SELECT * FROM failures 
ORDER BY created_at DESC 
LIMIT 10;

-- Échecs par type
SELECT entity_type, COUNT(*) as count 
FROM failures 
GROUP BY entity_type;

-- Échecs d'une série spécifique
SELECT * FROM failures 
WHERE entity_name LIKE '%nom de la série%'
ORDER BY created_at DESC;
```

### Vérifier les nouveaux épisodes indexés

```sql
-- Épisodes ajoutés récemment
SELECT e.*, s.name as season_name, sr.name as serie_name
FROM episodes e
JOIN seasons s ON e.season_id = s.id
JOIN series sr ON s.serie_id = sr.id
WHERE e.created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY e.created_at DESC;

-- Nombre d'épisodes par jour
SELECT DATE(created_at) as date, COUNT(*) as count
FROM episodes
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 7;
```

## Dépannage

### Erreur de connexion à la base de données

Vérifiez les variables d'environnement :
```bash
echo $DB_HOST
echo $DB_PORT
echo $DB_NAME
echo $DB_USER
```

### Erreur de connexion à anime-sama.fr

Vérifiez que le site est accessible :
```bash
curl -I https://anime-sama.fr/
```

### Commande introuvable

Réinstallez le package :
```bash
pip install -e .
```

Ou reconstruisez l'image Docker :
```bash
docker compose build app
```

## Meilleures pratiques

1. **Fréquence d'exécution** : Exécutez la commande toutes les 6 heures pour un bon équilibre entre fraîcheur des données et charge serveur.

2. **Sauvegarde** : Pensez à sauvegarder votre base de données régulièrement :
   ```bash
   docker compose exec db mysqldump -u root -prootpassword scrapsama_db > backup.sql
   ```

3. **Monitoring** : Surveillez les logs et la table `failures` pour détecter les problèmes.

4. **Nettoyage** : Pensez à nettoyer les anciennes entrées de la table `failures` :
   ```sql
   DELETE FROM failures WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
   ```

## Support

Pour toute question ou problème :
1. Consultez la documentation : [README.md](README.md)
2. Vérifiez les issues GitHub : https://github.com/Oriloo/scrapsama/issues
3. Créez une nouvelle issue si nécessaire

## Conclusion

Cette fonctionnalité permet de maintenir votre base de données à jour automatiquement avec les derniers épisodes d'anime-sama.fr. Une fois configurée, elle fonctionne de manière autonome et ne nécessite aucune intervention manuelle.
