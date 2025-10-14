#!/usr/bin/env python3
"""Index all episodes of a series to the database.

This script automatically indexes all seasons and episodes of a given series
to the database without any manual selection.
"""
import asyncio
import logging
import sys

from rich import get_console
from rich.logging import RichHandler
from rich.status import Status

from .utils import safe_input, select_one

from ..top_level import AnimeSama
from ..database import Database, index_episode, index_serie, index_season

console = get_console()
console._highlight = False
logging.basicConfig(format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])


def spinner(text: str) -> Status:
    return console.status(text, spinner_style="cyan")


async def index_full_series() -> None:
    """Index all seasons and episodes of a series to the database."""
    query = safe_input("Series name: \033[0;34m", str)

    with spinner(f"Searching for [blue]{query}"):
        catalogues = await AnimeSama("https://anime-sama.fr/").search(query)
    
    if not catalogues:
        console.print(f"[red]No series found for query: {query}[/]")
        return
    
    catalogue = select_one(catalogues)
    
    console.print(f"\n[cyan bold]Starting full series indexing for: {catalogue.name}[/]")
    
    # Initialize database connection
    db = Database()
    if not db.connect():
        console.print("[red]Failed to connect to database. Please check your configuration.[/]")
        console.print("\nMake sure:")
        console.print("  1. MySQL is running")
        console.print("  2. Database credentials are correct")
        console.print("  3. mysql-connector-python is installed: pip install mysql-connector-python")
        return
    
    if not db.initialize_schema():
        console.print("[red]Failed to initialize database schema.[/]")
        db.close()
        return
    
    # Index the series first
    with spinner(f"Indexing series [blue]{catalogue.name}"):
        serie_id = index_serie(catalogue, db)
    
    if not serie_id:
        console.print(f"[red]Failed to index series: {catalogue.name}[/]")
        db.close()
        return
    
    console.print(f"[green]✓ Series indexed (ID: {serie_id})[/]")
    
    # Get all seasons
    with spinner(f"Getting all seasons for [blue]{catalogue.name}"):
        try:
            seasons = await catalogue.seasons()
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]Error getting seasons: {error_msg}[/]")
            db.log_failure("series", catalogue.name, "Failed to get seasons", error_msg, serie_id)
            db.close()
            return
    
    if not seasons:
        console.print(f"[yellow]No seasons found for {catalogue.name}[/]")
        db.close()
        return
    
    console.print(f"[green]Found {len(seasons)} season(s)[/]")
    
    total_episodes = 0
    total_indexed = 0
    
    # Process each season
    for season_num, season in enumerate(seasons, 1):
        console.print(f"\n[cyan]Processing season {season_num}/{len(seasons)}: {season.name}[/]")
        
        # Index the season
        season_id = index_season(season, serie_id, db)
        if not season_id:
            console.print(f"[red]Failed to index season: {season.name}[/]")
            continue
        
        console.print(f"[green]✓ Season indexed (ID: {season_id})[/]")
        
        with spinner(f"Getting episodes for [blue]{season.name}"):
            try:
                episodes = await season.episodes()
            except Exception as e:
                error_msg = str(e)
                console.print(f"[red]Error getting episodes for {season.name}: {error_msg}[/]")
                db.log_failure("season", f"{catalogue.name} - {season.name}", 
                              "Failed to get episodes", error_msg, season_id)
                continue
        
        if not episodes:
            console.print(f"[yellow]No episodes found for {season.name}[/]")
            continue
        
        console.print(f"[green]Found {len(episodes)} episode(s)[/]")
        
        # Index each episode
        for episode_num, episode in enumerate(episodes, 1):
            total_episodes += 1
            try:
                success = index_episode(episode, season_id, db)
                if success:
                    total_indexed += 1
                    console.print(f"  [green]✓[/] [{episode_num}/{len(episodes)}] {episode.name}")
                else:
                    console.print(f"  [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Failed to index")
            except Exception as e:
                console.print(f"  [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Error: {e}")
    
    db.close()
    
    # Summary
    console.print("\n[cyan bold]Indexing Complete![/]")
    console.print(f"Series: {catalogue.name}")
    console.print(f"Total episodes processed: {total_episodes}")
    console.print(f"Successfully indexed: {total_indexed}")
    if total_indexed < total_episodes:
        console.print(f"[yellow]Failed to index: {total_episodes - total_indexed}[/]")


def main() -> int:
    """Main entry point for the index-series script."""
    try:
        asyncio.run(index_full_series())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError, EOFError):
        console.print("\n[red]Exiting...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
