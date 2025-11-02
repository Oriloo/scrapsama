"""
FlareSolverr client wrapper for bypassing anti-bot protections.
This module provides a custom HTTP client that uses FlareSolverr when enabled.
"""

import asyncio
import logging
import os
from typing import Any, Optional
from httpx import AsyncClient, Response, Request
import json

logger = logging.getLogger(__name__)


class FlareSolverrClient(AsyncClient):
    """
    Custom AsyncClient that routes requests through FlareSolverr when enabled.
    Falls back to regular httpx behavior when FlareSolverr is disabled or unavailable.
    """

    def __init__(
        self,
        flaresolverr_url: Optional[str] = None,
        flaresolverr_enabled: bool = True,
        max_timeout: int = 60000,
        **kwargs: Any,
    ) -> None:
        """
        Initialize FlareSolverr client.
        
        Args:
            flaresolverr_url: URL of FlareSolverr service (e.g., http://localhost:8191/v1)
            flaresolverr_enabled: Whether to use FlareSolverr or fallback to regular httpx
            max_timeout: Maximum timeout for FlareSolverr requests in milliseconds
            **kwargs: Additional arguments passed to AsyncClient
        """
        super().__init__(**kwargs)
        
        # Get configuration from environment or use provided values
        self.flaresolverr_url = flaresolverr_url or os.getenv(
            "FLARESOLVERR_URL", "http://localhost:8191/v1"
        )
        enabled_env = os.getenv("FLARESOLVERR_ENABLED", "true").lower()
        self.flaresolverr_enabled = flaresolverr_enabled and enabled_env in ("true", "1", "yes")
        self.max_timeout = max_timeout
        
        # Session management
        self.session_id: Optional[str] = None
        self._lock = asyncio.Lock()
        
        # Anti-detection headers to mimic a real browser
        if "headers" not in kwargs:
            self.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            })
        
        if self.flaresolverr_enabled:
            logger.info(f"FlareSolverr enabled at {self.flaresolverr_url}")
        else:
            logger.info("FlareSolverr disabled, using regular httpx client")

    async def _create_session(self) -> bool:
        """Create a FlareSolverr session for reuse."""
        try:
            async with self._lock:
                if self.session_id:
                    return True
                
                payload = {
                    "cmd": "sessions.create",
                }
                
                response = await super().post(self.flaresolverr_url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        self.session_id = data.get("session")
                        logger.info(f"FlareSolverr session created: {self.session_id}")
                        return True
                
                logger.warning("Failed to create FlareSolverr session")
                return False
        except Exception as e:
            logger.error(f"Error creating FlareSolverr session: {e}")
            return False

    async def _destroy_session(self) -> None:
        """Destroy the current FlareSolverr session."""
        try:
            async with self._lock:
                if not self.session_id:
                    return
                
                payload = {
                    "cmd": "sessions.destroy",
                    "session": self.session_id,
                }
                
                await super().post(self.flaresolverr_url, json=payload, timeout=10)
                logger.info(f"FlareSolverr session destroyed: {self.session_id}")
                self.session_id = None
        except Exception as e:
            logger.error(f"Error destroying FlareSolverr session: {e}")

    async def _request_via_flaresolverr(
        self, method: str, url: str, **kwargs: Any
    ) -> Response:
        """
        Make a request through FlareSolverr.
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            Response object with the result from FlareSolverr
        """
        # Ensure session exists
        if not self.session_id:
            await self._create_session()
        
        payload = {
            "cmd": "request.get" if method.upper() == "GET" else "request.post",
            "url": str(url),
            "maxTimeout": self.max_timeout,
        }
        
        if self.session_id:
            payload["session"] = self.session_id
        
        # Add POST data if present
        if method.upper() == "POST" and "data" in kwargs:
            payload["postData"] = kwargs["data"]
        
        try:
            # Make request to FlareSolverr
            fs_response = await super().post(
                self.flaresolverr_url,
                json=payload,
                timeout=self.max_timeout / 1000 + 10,  # Convert to seconds and add buffer
            )
            
            if fs_response.status_code != 200:
                logger.warning(f"FlareSolverr returned status {fs_response.status_code}, falling back to direct request")
                return await super().request(method, url, **kwargs)
            
            data = fs_response.json()
            
            if data.get("status") != "ok":
                logger.warning(f"FlareSolverr request failed: {data.get('message')}, falling back to direct request")
                return await super().request(method, url, **kwargs)
            
            solution = data.get("solution", {})
            
            # Create a mock Response object with FlareSolverr's result
            # We use a simple approach by creating a request and response
            response_data = {
                "status_code": solution.get("status", 200),
                "headers": solution.get("headers", {}),
                "content": solution.get("response", "").encode("utf-8"),
            }
            
            # Build a proper response
            request = Request(method, url)
            response = Response(
                status_code=response_data["status_code"],
                headers=response_data["headers"],
                content=response_data["content"],
                request=request,
            )
            
            logger.debug(f"FlareSolverr request successful for {url}")
            return response
            
        except Exception as e:
            logger.error(f"Error in FlareSolverr request: {e}, falling back to direct request")
            return await super().request(method, url, **kwargs)

    async def request(
        self, method: str, url: str, **kwargs: Any
    ) -> Response:
        """
        Override request method to route through FlareSolverr when enabled.
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            Response object
        """
        if not self.flaresolverr_enabled:
            return await super().request(method, url, **kwargs)
        
        # Only use FlareSolverr for GET requests by default
        # POST requests can be added if needed
        if method.upper() == "GET":
            return await self._request_via_flaresolverr(method, url, **kwargs)
        
        return await super().request(method, url, **kwargs)

    async def get(self, url: str, **kwargs: Any) -> Response:
        """Override get method."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Response:
        """Override post method."""
        return await self.request("POST", url, **kwargs)

    async def aclose(self) -> None:
        """Override close to cleanup FlareSolverr session."""
        if self.flaresolverr_enabled and self.session_id:
            await self._destroy_session()
        await super().aclose()

    async def __aexit__(self, *args: Any) -> None:
        """Override context manager exit."""
        await self.aclose()


def create_client(
    flaresolverr_url: Optional[str] = None,
    flaresolverr_enabled: Optional[bool] = None,
    **kwargs: Any,
) -> FlareSolverrClient:
    """
    Factory function to create a FlareSolverr-enabled client.
    
    Args:
        flaresolverr_url: URL of FlareSolverr service
        flaresolverr_enabled: Whether to enable FlareSolverr
        **kwargs: Additional arguments for AsyncClient
        
    Returns:
        FlareSolverrClient instance
    """
    if flaresolverr_enabled is None:
        enabled_env = os.getenv("FLARESOLVERR_ENABLED", "true").lower()
        flaresolverr_enabled = enabled_env in ("true", "1", "yes")
    
    return FlareSolverrClient(
        flaresolverr_url=flaresolverr_url,
        flaresolverr_enabled=flaresolverr_enabled,
        **kwargs,
    )
