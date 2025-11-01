"""FlareSolverr integration for bypassing Cloudflare protection.

This module provides a custom httpx transport that routes requests through
FlareSolverr when needed to bypass Cloudflare and other bot protection.
"""
import logging
import os
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class FlareSolverrTransport(httpx.AsyncHTTPTransport):
    """Custom httpx transport that uses FlareSolverr for requests."""
    
    def __init__(self, flaresolverr_url: Optional[str] = None, **kwargs):
        """Initialize FlareSolverr transport.
        
        Args:
            flaresolverr_url: URL of FlareSolverr API (e.g., http://localhost:8191/v1)
            **kwargs: Additional arguments passed to AsyncHTTPTransport
        """
        super().__init__(**kwargs)
        self.flaresolverr_url = flaresolverr_url or os.getenv("FLARESOLVERR_URL")
        self.enabled = bool(self.flaresolverr_url)
        self._flaresolverr_client: Optional[httpx.AsyncClient] = None
        
        if self.enabled:
            logger.info(f"FlareSolverr enabled at: {self.flaresolverr_url}")
        else:
            logger.info("FlareSolverr disabled (no URL configured)")
    
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle request through FlareSolverr if enabled.
        
        Args:
            request: The httpx request to handle
            
        Returns:
            httpx.Response from either FlareSolverr or direct request
        """
        # If FlareSolverr is not enabled, use default transport
        if not self.enabled:
            return await super().handle_async_request(request)
        
        # Try FlareSolverr first
        try:
            return await self._flaresolverr_request(request)
        except Exception as e:
            logger.warning(f"FlareSolverr request failed: {e}, falling back to direct request")
            # Fallback to direct request
            return await super().handle_async_request(request)
    
    async def _flaresolverr_request(self, request: httpx.Request) -> httpx.Response:
        """Send request through FlareSolverr.
        
        Args:
            request: The original httpx request
            
        Returns:
            httpx.Response constructed from FlareSolverr response
        """
        if self._flaresolverr_client is None:
            self._flaresolverr_client = httpx.AsyncClient()
        
        # Prepare FlareSolverr request payload
        payload = {
            "cmd": "request.get",
            "url": str(request.url),
            "maxTimeout": 60000,
        }
        
        # Add POST data if present
        if request.method == "POST" and request.content:
            payload["cmd"] = "request.post"
            payload["postData"] = request.content.decode() if isinstance(request.content, bytes) else request.content
        
        # Send request to FlareSolverr
        flare_response = await self._flaresolverr_client.post(
            self.flaresolverr_url,
            json=payload,
            timeout=70.0
        )
        flare_response.raise_for_status()
        
        # Parse FlareSolverr response
        flare_data = flare_response.json()
        
        if flare_data.get("status") != "ok":
            raise Exception(f"FlareSolverr error: {flare_data.get('message', 'Unknown error')}")
        
        solution = flare_data.get("solution", {})
        
        # Construct httpx.Response from FlareSolverr solution
        response = httpx.Response(
            status_code=solution.get("status", 200),
            headers=solution.get("headers", {}),
            content=solution.get("response", "").encode("utf-8"),
            request=request,
        )
        
        return response
    
    async def aclose(self) -> None:
        """Close the transport and any associated clients."""
        if self._flaresolverr_client is not None:
            await self._flaresolverr_client.aclose()
        await super().aclose()


def create_client(
    use_flaresolverr: bool = True,
    flaresolverr_url: Optional[str] = None,
    **kwargs
) -> httpx.AsyncClient:
    """Create an httpx AsyncClient with optional FlareSolverr support.
    
    Args:
        use_flaresolverr: Whether to enable FlareSolverr (default: True if URL is available)
        flaresolverr_url: URL of FlareSolverr API (uses FLARESOLVERR_URL env var if not provided)
        **kwargs: Additional arguments passed to AsyncClient
        
    Returns:
        httpx.AsyncClient configured with or without FlareSolverr
    """
    if use_flaresolverr:
        url = flaresolverr_url or os.getenv("FLARESOLVERR_URL")
        if url:
            transport = FlareSolverrTransport(flaresolverr_url=url)
            return httpx.AsyncClient(transport=transport, **kwargs)
        else:
            logger.info("FlareSolverr URL not configured, using standard httpx client")
    
    # Return standard client if FlareSolverr is disabled or not available
    return httpx.AsyncClient(**kwargs)
