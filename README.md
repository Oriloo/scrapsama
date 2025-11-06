# Scrapsama

Scraper pour indexer des séries dans une base de données.

## Installation

**Note pour utilisateurs Windows** : Si vous obtenez l'erreur `exec /vpn/entrypoint.sh: no such file or directory`, c'est un problème de fins de ligne. Voir TEMP.md section "Dépannage" → "Erreur exec /vpn/entrypoint.sh".

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama

# 1. Télécharger un fichier OpenVPN de ProtonVPN (OBLIGATOIRE)
# Allez sur https://account.protonvpn.com/downloads
# Téléchargez un fichier .ovpn et placez-le dans vpn-config/protonvpn.ovpn
mkdir -p vpn-config
# Copiez votre fichier téléchargé ici

# 2. Activer le volume dans docker-compose.yml
# Décommentez la ligne: - ./vpn-config/protonvpn.ovpn:/vpn/config/protonvpn.ovpn:ro

# 3. Configurer les identifiants
cp .env.example .env
# Éditez .env avec vos identifiants ProtonVPN OpenVPN/IKEv2

# 4. Démarrer les services
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

## License

GPL-3.0
