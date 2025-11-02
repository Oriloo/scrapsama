"""Configuration module for scraper."""
import os
from typing import Optional


def get_anime_sama_url() -> str:
    """Get the Anime-Sama URL from environment variable.

    Returns:
        str: The Anime-Sama URL

    Raises:
        ValueError: If ANIME_SAMA_URL environment variable is not set
    """
    url = os.getenv('ANIME_SAMA_URL')
    if not url:
        raise ValueError("ANIME_SAMA_URL environment variable is required but not set")
    return url


def get_flaresolverr_url() -> Optional[str]:
    """Get the FlareSolverr URL from environment variable.

    Returns:
        Optional[str]: The FlareSolverr URL if enabled, None otherwise

    Raises:
        ValueError: If FLARESOLVERR_ENABLED or FLARESOLVERR_URL are not set
    """
    enabled_str = os.getenv('FLARESOLVERR_ENABLED')
    if not enabled_str:
        raise ValueError("FLARESOLVERR_ENABLED environment variable is required but not set")

    enabled = enabled_str.lower() == 'true'
    if not enabled:
        return None

    url = os.getenv('FLARESOLVERR_URL')
    if not url:
        raise ValueError("FLARESOLVERR_URL environment variable is required but not set when FLARESOLVERR_ENABLED is true")
    return url

