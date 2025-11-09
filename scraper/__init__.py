from .top_level import AnimeSama
from .catalogue import Catalogue
from .season import Season
from .episode import Episode, Languages, Players
from .langs import Lang, LangId, lang2ids, id2lang, flags
from .database import Database, DatabaseConfig, index_episode
from .flaresolverr_client import FlareSolverrClient, create_client

try:
    from .cli.index_series import main
except ImportError:
    import sys

    def main() -> int:
        print(
            "This scrapsama function could not run because the required "
            "dependencies were not installed.\nMake sure you've installed "
            "everything with: pip install 'scrapsama[cli]'"
        )

        sys.exit(1)


# __package__ = "scrapsama"
__all__ = [
    "AnimeSama",
    "Catalogue",
    "Season",
    "Players",
    "Languages",
    "Episode",
    "Lang",
    "LangId",
    "lang2ids",
    "id2lang",
    "flags",
    "main",
    "Database",
    "DatabaseConfig",
    "index_episode",
    "FlareSolverrClient",
    "create_client",
]

"""__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "scrapsama")  # noqa"""
