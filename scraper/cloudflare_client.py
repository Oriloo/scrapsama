"""
Cloudflare-aware HTTP client for bypassing Cloudflare protection.

This module provides an AsyncClient that uses cloudscraper to obtain
the necessary cookies and headers to bypass Cloudflare's bot detection.
"""

from typing import Any
from httpx import AsyncClient
import cloudscraper


def create_cloudflare_client(**kwargs: Any) -> AsyncClient:
    """
    Create an httpx AsyncClient configured with cloudscraper headers.
    
    This function uses cloudscraper to generate appropriate headers and user agent
    that can bypass Cloudflare's protection, then creates an httpx AsyncClient
    with those headers.
    
    Args:
        **kwargs: Additional keyword arguments to pass to AsyncClient constructor
        
    Returns:
        AsyncClient: An httpx AsyncClient configured with cloudscraper headers
    """
    # Create a cloudscraper session to get proper headers
    scraper = cloudscraper.create_scraper()
    
    # Extract headers from cloudscraper session
    headers = dict(scraper.headers)
    
    # Merge with any user-provided headers (without modifying original kwargs)
    user_headers = kwargs.get('headers', {})
    if user_headers:
        headers.update(user_headers)
        # Create a copy of kwargs without 'headers' key
        kwargs = {k: v for k, v in kwargs.items() if k != 'headers'}
    
    # Create AsyncClient with cloudscraper headers
    return AsyncClient(headers=headers, **kwargs)
