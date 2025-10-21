#!/usr/bin/env python3
"""Index all available series to the database.

This script automatically indexes all seasons and episodes of all available series
to the database without any manual selection.
"""
import asyncio
import logging
import sys

from rich import get_console
from rich.logging import RichHandler
from rich.status import Status

from ..top_level import AnimeSama
from ..database import Database, index_episode, index_serie, index_season

console = get_console()
console._highlight = False
logging.basicConfig(format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])


def spinner(text: str) -> Status:
    return console.status(text, spinner_style="cyan")


async def index_all_available_series() -> None:
    """Index all available series and their episodes to the database."""
    console.print("\n[cyan bold]Starting full catalogue indexing[/]\n")
    
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
    
    # Get all available series
    with spinner("Fetching all available series from anime-sama.fr"):
        anime_sama = AnimeSama("https://anime-sama.fr/")
        catalogues = await anime_sama.all_catalogues()
    
    if not catalogues:
        console.print("[yellow]No series found[/]")
        db.close()
        return
    
    console.print(f"[green]Found {len(catalogues)} series to index[/]\n")
    
    total_series = len(catalogues)
    total_episodes = 0
    total_indexed = 0
    failed_series = []
    
    # Tracking counters for logging
    new_series_count = 0
    new_seasons_count = 0
    new_episodes_count = 0
    error_count = 0
    
    # Process each series
    for series_num, catalogue in enumerate(catalogues, 1):
        console.print(f"\n[cyan bold]Processing series {series_num}/{total_series}: {catalogue.name}[/]")
        
        try:
            # Index the series first
            serie_id = index_serie(catalogue, db)
            if not serie_id:
                console.print(f"[red]Failed to index series: {catalogue.name}[/]")
                failed_series.append(catalogue.name)
                error_count += 1
                continue
            
            console.print(f"[green]✓ Series indexed (ID: {serie_id})[/]")
            new_series_count += 1
            
            # Get all seasons
            with spinner(f"Getting seasons for [blue]{catalogue.name}"):
                try:
                    seasons = await catalogue.seasons()
                except Exception as e:
                    error_msg = str(e)
                    console.print(f"[red]Error getting seasons: {error_msg}[/]")
                    failed_series.append(catalogue.name)
                    error_count += 1
                    continue
            
            if not seasons:
                console.print(f"[yellow]No seasons found for {catalogue.name}[/]")
                error_count += 1
                continue
            
            console.print(f"[green]Found {len(seasons)} season(s)[/]")
            
            # Process each season
            for season_num, season in enumerate(seasons, 1):
                console.print(f"  [cyan]Season {season_num}/{len(seasons)}: {season.name}[/]")
                
                # Index the season
                season_id = index_season(season, serie_id, db)
                if not season_id:
                    console.print(f"  [red]Failed to index season: {season.name}[/]")
                    error_count += 1
                    continue
                
                console.print(f"  [green]✓ Season indexed (ID: {season_id})[/]")
                new_seasons_count += 1
                
                with spinner(f"Getting episodes for [blue]{season.name}"):
                    try:
                        episodes = await season.episodes()
                    except Exception as e:
                        error_msg = str(e)
                        console.print(f"  [red]Error getting episodes for {season.name}: {error_msg}[/]")
                        error_count += 1
                        continue
                
                if not episodes:
                    console.print(f"  [yellow]No episodes found for {season.name}[/]")
                    continue
                
                console.print(f"  [green]Found {len(episodes)} episode(s)[/]")
                
                # Index each episode
                for episode_num, episode in enumerate(episodes, 1):
                    total_episodes += 1
                    try:
                        success = index_episode(episode, season_id, db)
                        if success:
                            total_indexed += 1
                            new_episodes_count += 1
                            console.print(f"    [green]✓[/] [{episode_num}/{len(episodes)}] {episode.name}")
                        else:
                            error_count += 1
                            console.print(f"    [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Failed to index")
                    except Exception as e:
                        error_count += 1
                        console.print(f"    [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Error: {e}")
        
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]Error processing series {catalogue.name}: {error_msg}[/]")
            failed_series.append(catalogue.name)
            error_count += 1
            continue
    
    # Log the indexing operation
    db.log_indexing("index-all", new_series_count, new_seasons_count, new_episodes_count, error_count)
    db.close()
    
    # Summary
    console.print("\n[cyan bold]Indexing Complete![/]")
    console.print(f"Total series processed: {total_series}")
    console.print(f"Total episodes processed: {total_episodes}")
    console.print(f"Successfully indexed: {total_indexed}")
    if total_indexed < total_episodes:
        console.print(f"[yellow]Failed to index: {total_episodes - total_indexed}[/]")
    if failed_series:
        console.print(f"[yellow]Series with errors ({len(failed_series)}):[/]")
        for series_name in failed_series:
            console.print(f"  - {series_name}")


def main() -> int:
    """Main entry point for the index-all-series script."""
    try:
        asyncio.run(index_all_available_series())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError, EOFError):
        console.print("\n[red]Exiting...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
