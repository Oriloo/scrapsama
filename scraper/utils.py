import re
from typing import Any, TypeVar, cast, get_args
from itertools import zip_longest
from collections.abc import Callable, Generator, Iterable, Sequence

from httpx import AsyncClient

T = TypeVar("T")


def create_http_client() -> AsyncClient:
    """
    Create an AsyncClient with headers to bypass Cloudflare protection.
    
    Returns:
        AsyncClient configured with browser-like headers
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }
    return AsyncClient(headers=headers, follow_redirects=True)


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
