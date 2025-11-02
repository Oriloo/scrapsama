import re
from typing import Any, TypeVar, cast, get_args
from itertools import zip_longest
from collections.abc import Callable, Generator, Iterable, Sequence

try:
    from curl_cffi.requests import AsyncSession as CurlAsyncSession, Response as CurlResponse
    CURL_CFFI_AVAILABLE = True
    
    class CompatibleResponse:
        """Wrapper to make curl_cffi Response compatible with httpx Response."""
        def __init__(self, response: CurlResponse):
            self._response = response
        
        @property
        def is_success(self) -> bool:
            """Compatibility property for httpx's is_success."""
            return 200 <= self._response.status_code < 300
        
        @property
        def text(self) -> str:
            return self._response.text
        
        @property
        def status_code(self) -> int:
            return self._response.status_code
        
        def raise_for_status(self):
            return self._response.raise_for_status()
    
    class CompatibleAsyncSession:
        """Wrapper to make curl_cffi AsyncSession return compatible responses."""
        def __init__(self, *args, **kwargs):
            self._session = CurlAsyncSession(*args, **kwargs)
        
        async def get(self, url: str, **kwargs):
            response = await self._session.get(url, **kwargs)
            return CompatibleResponse(response)
        
        async def post(self, url: str, **kwargs):
            response = await self._session.post(url, **kwargs)
            return CompatibleResponse(response)
        
        async def aclose(self):
            await self._session.close()
        
        def __getattr__(self, name):
            # Delegate other attributes to the wrapped session
            return getattr(self._session, name)
    
except ImportError:
    from httpx import AsyncClient
    CURL_CFFI_AVAILABLE = False

T = TypeVar("T")


def create_http_client():
    """
    Create an HTTP client with Cloudflare bypass capabilities.
    
    Uses curl_cffi if available (better Cloudflare bypass), otherwise falls back to httpx.
    
    Returns:
        CompatibleAsyncSession (curl_cffi wrapper) or AsyncClient (httpx)
    """
    if CURL_CFFI_AVAILABLE:
        # Use curl_cffi with chrome120 impersonation for better Cloudflare bypass
        return CompatibleAsyncSession(impersonate="chrome120", timeout=30.0)
    else:
        # Fallback to httpx with comprehensive headers
        from httpx import AsyncClient
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://anime-sama.org/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Cache-Control": "max-age=0",
        }
        return AsyncClient(headers=headers, follow_redirects=True, timeout=30.0)


# By Mike Müller (https://stackoverflow.com/a/38059462)
def zip_varlen(
    *iterables: Sequence[Iterable[T]], sentinel: object = object()
) -> list[list[T]]:
    return cast(
        list[list[T]],
        [
            [entry for entry in iterable if entry is not sentinel]
            for iterable in zip_longest(*iterables, fillvalue=sentinel)
        ],
    )


def split_and_strip(string: str, delimiters: Iterable[str] | str) -> list[str]:
    if isinstance(delimiters, str):
        return [part.strip() for part in string.split(delimiters)]

    string_list = [string]
    for delimiter in delimiters:
        string_list = sum((part.split(delimiter) for part in string_list), [])
    return [part.strip() for part in string_list]


def remove_some_js_comments(string: str) -> str:
    string = re.sub(r"\/\*[\W\w]*?\*\/", "", string)  # Remove /* ... */
    return re.sub(r"<!--[\W\w]*?-->", "", string)  # Remove <!-- ... -->


# TODO: this callback_when_false is curse, should be remove
def is_Literal(
    value: Any, Lit: Any, callback_when_false: Callable[[Any], None] = lambda _: None
) -> bool:
    if value in get_args(Lit):
        return True
    callback_when_false(value)
    return False


def filter_literal(
    iterable: Iterable[Any],
    Lit: T,
    callback_when_false: Callable[[Any], None] = lambda _: None,
) -> Generator[T]:
    return (value for value in iterable if is_Literal(value, Lit, callback_when_false))
