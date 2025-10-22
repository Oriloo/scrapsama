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
from ..season import Season

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
    
    # Tracking counters for logging
    new_series_count = 0
    new_seasons_count = 0
    new_episodes_count = 0
    error_count = 0
    
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
                error_count += 1
                continue
            
            # Find the exact matching catalogue (usually the first one is correct)
            catalogue = catalogues[0]
            
            # Index the series if not already done in this run
            serie_id: Optional[int] = None
            if release.serie_name not in series_processed:
                serie_id, is_new_serie = index_serie(catalogue, db)
                if not serie_id:
                    console.print(f"[red]  ✗ Failed to index series: {catalogue.name}[/]")
                    error_count += 1
                    continue
                console.print(f"[green]  ✓ Series {'created' if is_new_serie else 'updated'} (ID: {serie_id})[/]")
                if is_new_serie:
                    new_series_count += 1
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
                error_count += 1
                continue
            
            # Create Season object directly from release.page_url
            # This avoids fetching all seasons which is slow for series with many seasons
            # The release.page_url contains the season URL, but we need to truncate it
            # to just the base season URL without language suffixes
            
            # Truncate URL to base season URL
            # From: https://anime-sama.fr/catalogue/{serie}/{season}/vostfr/
            # or:   https://anime-sama.fr/catalogue/{serie}/{season}-vostfr/
            # To:   https://anime-sama.fr/catalogue/{serie}/{season}/
            url_parts = release.page_url.rstrip('/').split('/')
            
            # URL structure: [https:, '', anime-sama.fr, catalogue, {serie}, {season}, ...]
            # We want to keep up to and including the season part (index 5)
            # and discard any language parts that follow
            if len(url_parts) < 6:
                console.print(f"[yellow]  ⚠ Invalid URL format: {release.page_url}[/]")
                error_count += 1
                continue
            
            # Reconstruct base season URL (up to season part, then add trailing /)
            base_season_url = '/'.join(url_parts[:6]) + '/'
            
            # Extract season name from the URL part
            season_part = url_parts[5]
            # Remove any language suffix from season name (e.g., "saison11-vostfr" -> "saison11")
            season_name = season_part.replace('-vostfr', '').replace('-vf', '').replace('-', ' ').title()
            
            # Create Season object with the truncated base URL
            target_season = Season(
                url=base_season_url,
                name=season_name,
                serie_name=catalogue.name,
                client=anime_sama.client
            )
            
            console.print(f"[cyan]  → Targeting season: {target_season.name}[/]")
            
            # Check if season already exists in database to avoid re-indexing
            # For index-new, we only want to process genuinely new seasons
            # Check by URL only as it uniquely identifies a season
            cursor = db._connection.cursor()
            try:
                cursor.execute("""
                    SELECT id FROM seasons 
                    WHERE url = %s
                """, (base_season_url,))
                existing_season = cursor.fetchone()
            finally:
                cursor.close()
            
            if existing_season:
                season_id = existing_season[0]
                console.print(f"  [green]✓ Season already exists in database (ID: {season_id}), skipping[/]")
                # Skip this season as it's already been indexed
                continue
            
            # Season doesn't exist, so we need to index it
            season = target_season
            console.print(f"  [cyan]Processing new season: {season.name}[/]")
            
            # Index the season
            season_id, is_new_season = index_season(season, serie_id, db)
            if not season_id:
                console.print(f"    [red]✗ Failed to index season: {season.name}[/]")
                error_count += 1
                continue
            
            console.print(f"    [green]✓ Season {'created' if is_new_season else 'updated'} (ID: {season_id})[/]")
            if is_new_season:
                new_seasons_count += 1
            
            # Get and index episodes
            with spinner(f"Getting episodes for [blue]{season.name}"):
                try:
                    episodes = await season.episodes()
                except Exception as e:
                    error_msg = str(e)
                    console.print(f"    [red]✗ Error getting episodes: {error_msg}[/]")
                    error_count += 1
                    continue
            
            if not episodes:
                console.print(f"    [yellow]⚠ No episodes found for {season.name}[/]")
                continue
            
            console.print(f"    [green]✓ Found {len(episodes)} episode(s)[/]")
            
            # Index each episode
            for episode_num, episode in enumerate(episodes, 1):
                total_processed += 1
                try:
                    success, is_new_episode = index_episode(episode, season_id, db)
                    if success:
                        total_indexed += 1
                        if is_new_episode:
                            new_episodes_count += 1
                        status = "created" if is_new_episode else "updated"
                        console.print(f"      [green]✓[/] [{episode_num}/{len(episodes)}] {episode.name} ({status})")
                    else:
                        error_count += 1
                        console.print(f"      [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Failed to index")
                except Exception as e:
                    error_count += 1
                    console.print(f"      [red]✗[/] [{episode_num}/{len(episodes)}] {episode.name} - Error: {e}")
        
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]  ✗ Error processing release: {error_msg}[/]")
            error_count += 1
            continue
    
    # Log the indexing operation
    db.log_indexing("index-new", new_series_count, new_seasons_count, new_episodes_count, error_count)
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
