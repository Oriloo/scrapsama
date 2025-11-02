"""
Async wrapper for cloudscraper to provide compatibility with existing async httpx-based code.
This wrapper allows the scraper to bypass Cloudflare protection while maintaining async functionality.
"""

import asyncio
from typing import Any
from functools import partial

try:
    import cloudscraper
except ImportError:
    cloudscraper = None  # type: ignore


class CloudscraperResponse:
    """Wrapper to make cloudscraper response compatible with httpx.Response interface."""
    
    def __init__(self, response: Any) -> None:
        self._response = response
        self.status_code = response.status_code
        self.text = response.text
        self.content = response.content
        self.headers = response.headers
        self.url = response.url
    
    @property
    def is_success(self) -> bool:
        """Check if response status code is 2xx."""
        return 200 <= self.status_code < 300
    
    def raise_for_status(self) -> "CloudscraperResponse":
        """Raise exception for 4xx/5xx status codes."""
        self._response.raise_for_status()
        return self


class AsyncCloudscraperClient:
    """
    Async wrapper for cloudscraper that provides an httpx.AsyncClient-like interface.
    
    This client bypasses Cloudflare protection while maintaining compatibility with
    the existing async codebase. All synchronous cloudscraper calls are executed
    in a thread pool to avoid blocking the event loop.
    """
    
    def __init__(self) -> None:
        if cloudscraper is None:
            raise ImportError(
                "cloudscraper is not installed. Install it with: pip install cloudscraper"
            )
        self._scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
    
    async def get(self, url: str, **kwargs: Any) -> CloudscraperResponse:
        """
        Async GET request using cloudscraper.
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments to pass to cloudscraper.get()
        
        Returns:
            CloudscraperResponse: Response object compatible with httpx.Response
        """
        # Run the synchronous cloudscraper request in a thread pool
        # Use get_running_loop() to get the current event loop at runtime
        loop = asyncio.get_running_loop()
        func = partial(self._scraper.get, url, **kwargs)
        response = await loop.run_in_executor(None, func)
        return CloudscraperResponse(response)
    
    async def __aenter__(self) -> "AsyncCloudscraperClient":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        # Close the session if needed
        loop = asyncio.get_running_loop()
        if hasattr(self._scraper, 'close'):
            await loop.run_in_executor(None, self._scraper.close)
