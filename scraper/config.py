"""Configuration module for scraper."""
import os
from typing import Optional


def get_anime_sama_url() -> str:
    """Get the Anime-Sama URL from environment variable.

    Returns:
        str: The Anime-Sama URL, defaults to https://anime-sama.org/
    """
    return os.getenv('ANIME_SAMA_URL', 'https://anime-sama.org/')


def get_flaresolverr_url() -> Optional[str]:
    """Get the FlareSolverr URL from environment variable.

    Returns:
        Optional[str]: The FlareSolverr URL if enabled, None otherwise
    """
    enabled = os.getenv('FLARESOLVERR_ENABLED', 'false').lower() == 'true'
    if not enabled:
        return None
    return os.getenv('FLARESOLVERR_URL', 'http://flaresolverr:8191/v1')

