# Scrapsama

Scraper pour indexer des séries dans une base de données.

## Installation

```bash
git clone https://github.com/Oriloo/scrapsama.git
cd scrapsama
docker compose up -d
docker compose run --rm app python init_db.py
```

## Utilisation

```bash
docker compose run --rm app scrapsama-index
docker compose run --rm app scrapsama-index-all
docker compose run --rm app scrapsama-index-new
```

## License

GPL-3.0
