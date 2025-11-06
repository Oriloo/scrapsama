# Scrapsama

Scraper pour indexer des séries dans une base de données.

## Fonctionnalités

- Scraping sécurisé via ProtonVPN avec kill switch strict
- Indexation automatique des séries et épisodes
- Support de FlareSolverr pour contourner les protections anti-bot
- Interface web optionnelle pour consulter la base de données

## Installation

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama

# Créer le fichier de configuration
cp .env.example .env

# Éditer .env avec vos identifiants ProtonVPN
# Voir TEMP.md pour la documentation complète

# Démarrer les services
docker compose up -d
docker compose run --rm app python scraper/init_db.py
```

```bash
# Services optionnels
docker compose --profile mysql --profile pma --profile web up -d
```

## Utilisation

```
docker compose run --rm app scrapsama-index
docker compose run --rm app scrapsama-index-all
docker compose run --rm app scrapsama-index-new
```

## Configuration ProtonVPN

Ce projet intègre ProtonVPN pour router tout le trafic du scraper via un tunnel VPN sécurisé avec kill switch.

**Documentation complète** : Voir [TEMP.md](TEMP.md) pour :
- Configuration des identifiants ProtonVPN
- Choix du serveur VPN
- Vérification du fonctionnement
- Dépannage

**Variables requises** dans `.env` :
- `PROTONVPN_USERNAME` : Votre username OpenVPN/IKEv2
- `PROTONVPN_PASSWORD` : Votre password OpenVPN/IKEv2  
- `PROTONVPN_SERVER` : Serveur à utiliser (ex: `nl-free-01.protonvpn.net`)

## License

GPL-3.0
