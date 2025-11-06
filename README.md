# Scrapsama

Scraper pour indexer des séries dans une base de données.

## Installation

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama
cp .env.example .env
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
