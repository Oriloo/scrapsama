from .top_level import AnimeSama
from .catalogue import Catalogue
from .season import Season
from .episode import Episode, Languages, Players
from .langs import Lang, LangId, lang2ids, id2lang, flags
from .database import Database, DatabaseConfig, index_episode

try:
    from .cli.index_series import main
except ImportError:
    import sys

    def main() -> int:
        print(
            "This anime-sama_api function could not run because the required "
            "dependencies were not installed.\nMake sure you've installed "
            "everything with: pip install 'anime-sama_api[cli]'"
        )

        sys.exit(1)


# __package__ = "anime-sama_api"
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
]

"""__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "anime-sama_api")  # noqa"""
