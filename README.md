This project is archive. I do not have the time to work on it anymore. I may make some small fixes if a breaking issue arises. 

# Anime-Sama API - Series Indexing

An API for anime-sama.fr focused on indexing anime series information into a MySQL database.

**Focus:** This codebase is dedicated to series indexing functionality - storing anime/manga series, seasons, episodes, and video links in a database.

**Key Feature:** 
- **Automatic series indexing**: Index all episodes of a series with a single command using `anime-sama-index-series`.

I have implemented all the features I care about. This project is now in maintenance mode.

# Installation
Requirements:
- Python 3.10 or higher
- MySQL 8.0+ (for database storage)

You can simply install it with (note that you can use tools like pipx to isolate the installation):
```bash
pip install anime-sama-api[cli,database]
```
And to run it:
```bash
anime-sama-index-series
```

## Docker Installation
For a complete setup with MySQL and phpMyAdmin, see [DOCKER.md](DOCKER.md).

Quick start:
```bash
docker compose up -d
docker compose run --rm app anime-sama-index-series
```

Or using Make:
```bash
make up
make run
```

# For developers
## Requirements
- git
- Python 3.10+

## Install locally
```bash
git clone https://github.com/Sky-NiniKo/anime-sama_api.git
cd anime-sama_downloader
pip install -e .[cli,database]
```

## Run
```bash
anime-sama-index-series
```

## Update
In the `anime_sama` folder:
```bash
git pull
```

## Contribution
I am open to contribution. Please only open a PR for ONE change. AKA, don't do "Various improvements" and explain your motivation behind your improvement ("Various typos fix"/"Cleanup" is fine).
