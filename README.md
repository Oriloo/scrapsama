# Scrapsama

API Python pour indexer les séries anime depuis anime-sama.fr dans une base de données MySQL.

## Fonctionnalités

- **Indexation**: Outils CLI pour indexer les séries anime, les saisons et les épisodes dans une base de données MySQL
- **API Python**: API complète pour rechercher, récupérer et indexer les anime
- **Base de données**: Backend MySQL pour stocker les informations des séries et les URLs des lecteurs

## Installation sous Linux

### Prérequis

- Python 3.10 ou supérieur
- MySQL 8.0 ou supérieur
- pip (gestionnaire de paquets Python)

### Étape 1: Installer Python et les dépendances système

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server
```

### Étape 2: Configurer MySQL

```bash
# Sécuriser l'installation MySQL
sudo mysql_secure_installation

# Se connecter à MySQL
sudo mysql -u root -p

# Créer la base de données et l'utilisateur
CREATE DATABASE scrapsama_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'scrapsama_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON scrapsama_db.* TO 'scrapsama_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Étape 3: Installer Scrapsama

```bash
# Cloner le dépôt
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Installer le package en mode développement
pip install -e .
```

### Étape 4: Configuration

Créer un fichier de configuration pour les variables d'environnement:

```bash
# Créer le fichier ~/.scrapsama_env
cat > ~/.scrapsama_env << 'EOF'
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=scrapsama_db
export DB_USER=scrapsama_user
export DB_PASSWORD=votre_mot_de_passe
EOF

# Charger les variables d'environnement
source ~/.scrapsama_env

# Pour charger automatiquement au démarrage, ajouter à ~/.bashrc
echo "source ~/.scrapsama_env" >> ~/.bashrc
```

### Étape 5: Initialiser la base de données

La base de données sera automatiquement initialisée lors de la première utilisation des outils CLI.

## Utilisation

### Outils en ligne de commande

**Indexer une série spécifique:**
```bash
# Activer l'environnement virtuel si nécessaire
source scrapsama-env/bin/activate  # ou source venv/bin/activate

# Lancer l'indexation (vous serez invité à entrer le nom de la série)
scrapsama-index
```

**Indexer toutes les séries:**
```bash
scrapsama-index-all
```

**Indexer les nouveaux épisodes:**
```bash
# Cette commande récupère les derniers épisodes depuis la page d'accueil
# Parfait pour être exécuté régulièrement via cron
scrapsama-index-new
```

### Automatiser les mises à jour avec cron

Pour maintenir votre base de données à jour avec les nouveaux épisodes:

```bash
# Éditer le crontab
crontab -e

# Ajouter une ligne pour exécuter toutes les 6 heures
0 */6 * * * /home/votreuser/scrapsama-env/bin/scrapsama-index-new >> /var/log/scrapsama.log 2>&1

# Ou pour exécuter tous les jours à 2h du matin
0 2 * * * /home/votreuser/scrapsama-env/bin/scrapsama-index-new >> /var/log/scrapsama.log 2>&1
```

### Automatiser avec systemd (méthode moderne)

**Créer le service:**
```bash
sudo nano /etc/systemd/system/scrapsama-index-new.service
```

Contenu du fichier:
```ini
[Unit]
Description=Indexer les nouveaux épisodes anime
After=network.target mysql.service

[Service]
Type=oneshot
User=votreuser
WorkingDirectory=/home/votreuser
Environment="DB_HOST=localhost"
Environment="DB_PORT=3306"
Environment="DB_NAME=scrapsama_db"
Environment="DB_USER=scrapsama_user"
Environment="DB_PASSWORD=votre_mot_de_passe"
ExecStart=/home/votreuser/scrapsama-env/bin/scrapsama-index-new
StandardOutput=append:/var/log/scrapsama.log
StandardError=append:/var/log/scrapsama.log
```

**Créer le timer:**
```bash
sudo nano /etc/systemd/system/scrapsama-index-new.timer
```

Contenu du fichier:
```ini
[Unit]
Description=Exécuter scrapsama-index-new toutes les 6 heures

[Timer]
OnBootSec=15min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
```

**Activer et démarrer:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable scrapsama-index-new.timer
sudo systemctl start scrapsama-index-new.timer

# Vérifier le statut
sudo systemctl status scrapsama-index-new.timer
```

### API Python

**Indexer une série spécifique:**
```python
import asyncio
from scraper import AnimeSama, Database

async def index_series(name):
    # Rechercher la série
    anime_sama = AnimeSama("https://anime-sama.fr/")
    catalogues = await anime_sama.search(name)
    
    if not catalogues:
        print(f"Aucune série trouvée pour '{name}'")
        return
    
    catalogue = catalogues[0]
    
    # Initialiser la base de données
    db = Database()
    db.connect()
    db.initialize_schema()
    
    # Indexer la série, les saisons et les épisodes
    from scraper.database import index_serie, index_season
    serie_id = index_serie(catalogue, db)
    
    seasons = await catalogue.seasons()
    for season in seasons:
        season_id = index_season(season, serie_id, db)
        episodes = await season.episodes()
        for episode in episodes:
            from scraper.database import index_episode
            index_episode(episode, season_id, db)
    
    db.close()
    print(f"Série '{name}' indexée avec succès!")

# Exécuter
asyncio.run(index_series("one piece"))
```

**Récupérer les nouveaux épisodes:**
```python
import asyncio
from scraper import AnimeSama

async def get_new_episodes():
    anime_sama = AnimeSama("https://anime-sama.fr/")
    episode_releases = await anime_sama.new_episodes()
    
    for release in episode_releases:
        print(f"{release.serie_name} - {release.descriptive} ({release.language})")
        print(f"  URL: {release.page_url}")

asyncio.run(get_new_episodes())
```

**Rechercher et lister les séries:**
```python
import asyncio
from scraper import AnimeSama

async def search_anime(query):
    anime_sama = AnimeSama("https://anime-sama.fr/")
    results = await anime_sama.search(query)
    
    for catalogue in results:
        print(f"Nom: {catalogue.name}")
        print(f"URL: {catalogue.url}")
        print(f"Genres: {', '.join(catalogue.genres)}")
        print("---")

asyncio.run(search_anime("naruto"))
```

## Schéma de la base de données

La base de données comprend 5 tables principales:

**Table series:**
- id (CLÉ PRIMAIRE)
- name, url
- alternative_names, genres, categories, languages (JSON)
- image_url, advancement, correspondence, synopsis
- is_mature (boolean)
- created_at, updated_at

**Table seasons:**
- id (CLÉ PRIMAIRE)
- serie_id (CLÉ ÉTRANGÈRE → series.id)
- name, url
- created_at, updated_at

**Table episodes:**
- id (CLÉ PRIMAIRE)
- season_id (CLÉ ÉTRANGÈRE → seasons.id)
- serie_name, season_name, episode_name, episode_index, season_number
- created_at, updated_at

**Table players:**
- id (CLÉ PRIMAIRE)
- episode_id (CLÉ ÉTRANGÈRE → episodes.id)
- language, player_url, player_hostname, player_order
- created_at

**Table logs:**
- id (CLÉ PRIMAIRE)
- command (ex: "index[nom_série]", "index-all", "index-new")
- new_series, new_seasons, new_episodes (nombre d'éléments nouvellement indexés)
- error_count (nombre d'erreurs rencontrées)
- created_at

La table logs enregistre toutes les opérations d'indexation.

## Dépannage

### Erreur de connexion à la base de données

Si vous obtenez une erreur de connexion:
```bash
# Vérifier que MySQL est démarré
sudo systemctl status mysql

# Vérifier les identifiants dans ~/.scrapsama_env
source ~/.scrapsama_env
echo $DB_HOST $DB_PORT $DB_NAME $DB_USER
```

### Commande non trouvée

Si `scrapsama-index` n'est pas trouvé:
```bash
# Assurez-vous que l'environnement virtuel est activé
source scrapsama-env/bin/activate  # ou source venv/bin/activate

# Vérifier que le package est installé
pip list | grep scrapsama
```

### Erreur de permissions MySQL

Si vous rencontrez des erreurs de permissions:
```bash
sudo mysql -u root -p
GRANT ALL PRIVILEGES ON scrapsama_db.* TO 'scrapsama_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Licence

GPL-3.0
