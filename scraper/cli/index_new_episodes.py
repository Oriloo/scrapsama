#!/usr/bin/env python3
"""Index new episodes from anime-sama homepage to the database.

This script fetches the latest episodes from anime-sama.fr homepage
and indexes them to the database. It's designed to be run regularly
(e.g., via cron) to keep the database up-to-date with new content.
"""
import asyncio
import logging
import sys
from typing import Optional

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


async def index_new_episodes() -> None:
    """Index new episodes from the anime-sama homepage."""
    console.print("\n[cyan bold]Fetching latest episodes from anime-sama.fr[/]\n")
    
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
    
    # Get new episodes from homepage
    anime_sama = AnimeSama("https://anime-sama.fr/")
    
    with spinner("Fetching latest episodes from homepage"):
        try:
            episode_releases = await anime_sama.new_episodes()
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]Error fetching new episodes: {error_msg}[/]")
            db.close()
            return
    
    if not episode_releases:
        console.print("[yellow]No new episodes found on homepage[/]")
        db.close()
        return
    
    console.print(f"[green]Found {len(episode_releases)} new episode release(s)[/]\n")
    
    total_processed = 0
    total_indexed = 0
    series_processed = set()
    
    # Process each episode release
    for release_num, release in enumerate(episode_releases, 1):
        console.print(f"\n[cyan]Processing release {release_num}/{len(episode_releases)}:[/]")
        console.print(f"  Series: {release.serie_name}")
        console.print(f"  Language: {release.language}")
        console.print(f"  Description: {release.descriptive}")
        
        try:
            # Search for the series to get full catalogue information
            with spinner(f"Searching for series [blue]{release.serie_name}"):
                catalogues = await anime_sama.search(release.serie_name)
            
            if not catalogues:
                console.print(f"[yellow]  ⚠ Series not found: {release.serie_name}[/]")
                db.log_failure("series", release.serie_name, "Series not found in search",
                              f"Searched for '{release.serie_name}' but got no results")
                continue
            
            # Find the exact matching catalogue (usually the first one is correct)
            catalogue = catalogues[0]
            
            # Index the series if not already done in this run
            serie_id: Optional[int] = None
            if release.serie_name not in series_processed:
                serie_id = index_serie(catalogue, db)
                if not serie_id:
                    console.print(f"[red]  ✗ Failed to index series: {catalogue.name}[/]")
                    continue
                console.print(f"[green]  ✓ Series indexed (ID: {serie_id})[/]")
                series_processed.add(release.serie_name)
            else:
                # Get serie_id from database
                cursor = db._connection.cursor()
                try:
                    cursor.execute("SELECT id FROM series WHERE name = %s", (release.serie_name,))
                    result = cursor.fetchone()
                    serie_id = result[0] if result else None
                finally:
                    cursor.close()
                
                if serie_id:
                    console.print(f"[green]  ✓ Series already processed (ID: {serie_id})[/]")
            
            if not serie_id:
                console.print(f"[red]  ✗ Failed to get series ID for: {release.serie_name}[/]")
                continue
            
            # Get all seasons
            with spinner(f"Getting seasons for [blue]{catalogue.name}"):
                try:
                    seasons = await catalogue.seasons()
                except Exception as e:
                    error_msg = str(e)
                    console.print(f"[red]  ✗ Error getting seasons: {error_msg}[/]")
                    db.log_failure("series", catalogue.name, "Failed to get seasons", error_msg, serie_id)
                    continue
            
            if not seasons:
                console.print(f"[yellow]  ⚠ No seasons found for {catalogue.name}[/]")
                continue
            
            console.print(f"[green]  ✓ Found {len(seasons)} season(s)[/]")
            
            # Try to find the season from the release page_url
            # The page_url contains the season URL
            target_season = None
            for season in seasons:
                if season.url in release.page_url or release.page_url.startswith(season.url):
                    target_season = season
                    break
            
            if not target_season:
                # If we can't match by URL, try to match by the descriptive text
                # or just process all seasons (safer option)
                console.print(f"[yellow]  ⚠ Could not identify specific season, indexing all seasons[/]")
                seasons_to_process = seasons
            else:
                console.print(f"[cyan]  → Found matching season: {target_season.name}[/]")
                seasons_to_process = [target_season]
            
            # Process selected seasons
            for season in seasons_to_process:
                console.print(f"  [cyan]Processing season: {season.name}[/]")
                
                # Index the season
                season_id = index_season(season, serie_id, db)
                if not season_id:
                    console.print(f"    [red]✗ Failed to index season: {season.name}[/]")
                    continue
                
                console.print(f"    [green]✓ Season indexed (ID: {season_id})[/]")
                
                # Get and index episodes
                with spinner(f"Getting episodes for [blue]{season.name}"):
                    try:
                        episodes = await season.episodes()
                    except Exception as e:
                        error_msg = str(e)
                        console.print(f"    [red]✗ Error getting episodes: {error_msg}[/]")
                        db.log_failure("season", f"{catalogue.name} - {season.name}",
                                      "Failed to get episodes", error_msg, season_id)
                        continue
                
                if not episodes:
                    console.print(f"    [yellow]⚠ No episodes found for {season.name}[/]")
                    continue
                
                console.print(f"    [green]✓ Found {len(episodes)} episode(s)[/]")
                
                # Index each episode
                for episode_num, episode in enumerate(episodes, 1):
                    total_processed += 1
                    try:
                        success = index_episode(episode, season_id, db)
                        if success:
                            total_indexed += 1
                            console.print(f"      [green]✓[/] [{episode_num}/{len(episodes)}] {episode.name}")
                        else:
                            console.print(f"      [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Failed to index")
                    except Exception as e:
                        console.print(f"      [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Error: {e}")
        
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]  ✗ Error processing release: {error_msg}[/]")
            db.log_failure("series", release.serie_name, "Exception processing release", error_msg)
            continue
    
    db.close()
    
    # Summary
    console.print("\n[cyan bold]Indexing Complete![/]")
    console.print(f"Total episode releases on homepage: {len(episode_releases)}")
    console.print(f"Total episodes processed: {total_processed}")
    console.print(f"Successfully indexed: {total_indexed}")
    if total_indexed < total_processed:
        console.print(f"[yellow]Failed to index: {total_processed - total_indexed}[/]")


def main() -> int:
    """Main entry point for the index-new-episodes script."""
    try:
        asyncio.run(index_new_episodes())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError, EOFError):
        console.print("\n[red]Exiting...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
