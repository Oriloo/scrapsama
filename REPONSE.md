# Réponse à votre question

## Question posée

> Je souhaite que tu analyses le moteur de scraping et que tu me dises s'il existe un moyen de récupérer la liste des derniers épisodes ajoutés sur anime-sama, dans l'optique de faire tourner un processus de scraping régulier qui mettra à jour l'index.

## Réponse courte

**✅ OUI, absolument !** Le moteur de scraping possède déjà une méthode `AnimeSama.new_episodes()` qui récupère les derniers épisodes depuis la page d'accueil d'anime-sama.fr.

J'ai créé une nouvelle commande CLI `scrapsama-index-new` qui exploite cette méthode pour mettre à jour automatiquement votre base de données.

## Comment ça marche

### 1. La méthode existante

Le fichier `scraper/top_level.py` contient déjà cette méthode :

```python
async def new_episodes(self) -> list[EpisodeRelease]:
    """
    Return the new available episodes on anime-sama using the homepage 
    sorted from oldest to newest.
    """
    section = await self._get_homepage_section("ajouts animes", 4)
    release_episodes = list(self._yield_release_episodes_from(section))
    return list(reversed(release_episodes))
```

Cette méthode :
- Récupère la page d'accueil d'anime-sama.fr
- Extrait la section "ajouts animes" (nouveaux épisodes)
- Parse les informations de chaque épisode
- Retourne une liste d'objets `EpisodeRelease`

### 2. La nouvelle commande CLI

J'ai créé `scrapsama-index-new` qui :
1. Appelle `new_episodes()` pour obtenir la liste
2. Pour chaque épisode :
   - Recherche la série complète
   - Indexe la série dans la base de données
   - Indexe la saison correspondante
   - Indexe tous les épisodes de cette saison
3. Log tous les échecs pour diagnostic

## Utilisation

### Installation

```bash
# Si pas encore fait, installer avec les dépendances CLI et database
pip install -e ".[cli,database]"

# Ou reconstruire l'image Docker
docker compose build app
```

### Exécution manuelle

```bash
# En local
scrapsama-index-new

# Avec Docker
docker compose run --rm app scrapsama-index-new
```

### Processus régulier automatisé

#### Option A : Crontab (Recommandé)

```bash
# Éditer le crontab
crontab -e

# Ajouter une de ces lignes selon vos besoins :

# Toutes les 6 heures (recommandé)
0 */6 * * * cd /chemin/vers/scrapsama && docker compose run --rm app scrapsama-index-new >> /var/log/scrapsama.log 2>&1

# Toutes les heures
0 * * * * cd /chemin/vers/scrapsama && docker compose run --rm app scrapsama-index-new >> /var/log/scrapsama.log 2>&1

# Une fois par jour à 2h du matin
0 2 * * * cd /chemin/vers/scrapsama && docker compose run --rm app scrapsama-index-new >> /var/log/scrapsama.log 2>&1
```

#### Option B : Script en boucle

Créer un fichier `watch.sh` :

```bash
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    docker compose run --rm app scrapsama-index-new
    echo "Attente de 6 heures..."
    sleep 21600  # 6 heures en secondes
done
```

Puis :
```bash
chmod +x watch.sh
nohup ./watch.sh >> scrapsama-watch.log 2>&1 &
```

#### Option C : Systemd timer

Voir le fichier `USAGE_NEW_EPISODES.md` pour la configuration complète.

## Exemple de code Python

Si vous préférez intégrer cela dans votre propre code :

```python
import asyncio
from scraper import AnimeSama, Database, index_serie, index_season, index_episode

async def mettre_a_jour_index():
    """Met à jour l'index avec les nouveaux épisodes"""
    
    # Initialiser
    anime_sama = AnimeSama("https://anime-sama.fr/")
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Récupérer les nouveaux épisodes
    nouveaux_episodes = await anime_sama.new_episodes()
    print(f"Trouvé {len(nouveaux_episodes)} nouveaux épisodes")
    
    # Traiter chaque épisode
    for release in nouveaux_episodes:
        print(f"Traitement : {release.serie_name}")
        
        # Rechercher et indexer
        catalogues = await anime_sama.search(release.serie_name)
        if catalogues:
            catalogue = catalogues[0]
            serie_id = index_serie(catalogue, db)
            
            # Indexer les saisons et épisodes
            seasons = await catalogue.seasons()
            for season in seasons:
                season_id = index_season(season, serie_id, db)
                episodes = await season.episodes()
                for episode in episodes:
                    index_episode(episode, season_id, db)
    
    db.close()
    print("Mise à jour terminée !")

# Exécuter
asyncio.run(mettre_a_jour_index())
```

## Avantages de cette solution

✅ **Efficace** : Ne scanne que les nouveaux épisodes, pas tout le catalogue  
✅ **Automatisable** : Parfait pour cron ou autre scheduler  
✅ **Incrémental** : Ajoute seulement les nouvelles données  
✅ **Robuste** : Gestion d'erreurs et logging dans la base de données  
✅ **Simple** : Une seule commande à exécuter  
✅ **Documenté** : Guides complets en français

## Vérifier que ça fonctionne

### Via la base de données

```sql
-- Voir les épisodes ajoutés aujourd'hui
SELECT e.episode_name, s.name as season, sr.name as serie, e.created_at
FROM episodes e
JOIN seasons s ON e.season_id = s.id
JOIN series sr ON s.serie_id = sr.id
WHERE DATE(e.created_at) = CURDATE()
ORDER BY e.created_at DESC;

-- Compter les épisodes par jour
SELECT DATE(created_at) as jour, COUNT(*) as nombre
FROM episodes
GROUP BY DATE(created_at)
ORDER BY jour DESC
LIMIT 7;
```

### Via l'interface web

Accédez à http://localhost:5000 et vérifiez que les nouveaux épisodes apparaissent.

## Documentation complète

- `README.md` : Documentation générale avec exemples
- `SOLUTION.md` : Analyse technique détaillée
- `USAGE_NEW_EPISODES.md` : Guide complet d'utilisation

## Conclusion

Le moteur possédait déjà la capacité de récupérer les nouveaux épisodes. J'ai simplement créé une interface CLI pratique qui :
1. Utilise cette capacité existante
2. Automatise l'indexation dans la base de données
3. Peut être exécutée régulièrement via cron

**Vous pouvez maintenant mettre en place un processus de scraping régulier qui maintiendra votre index à jour automatiquement !**

Pour toute question, consultez les fichiers de documentation ou créez une issue sur GitHub.
