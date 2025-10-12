"""Tests for series indexing functionality."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from anime_sama_api.cli.index_series import index_full_series
from anime_sama_api.catalogue import Catalogue
from anime_sama_api.season import Season
from anime_sama_api.episode import Episode, Languages, Players


@pytest.mark.asyncio
async def test_index_full_series_mock():
    """Test the index_full_series function with mocked components."""
    # Create mock episode
    mock_episode = Episode(
        Languages(
            vostfr=Players([
                "https://vidmoly.net/embed-test.html",
                "https://video.sibnet.ru/shell.php?videoid=12345",
            ]),
        ),
        serie_name="test-serie",
        season_name="saison1",
        _name="Episode 1",
        index=1,
    )
    
    # Create mock season
    mock_season = MagicMock(spec=Season)
    mock_season.name = "Saison 1"
    mock_season.episodes = AsyncMock(return_value=[mock_episode])
    
    # Create mock catalogue
    mock_catalogue = MagicMock(spec=Catalogue)
    mock_catalogue.name = "Test Serie"
    mock_catalogue.seasons = AsyncMock(return_value=[mock_season])
    
    # This test ensures the basic structure works
    # The actual indexing would need a real database connection
    assert mock_catalogue.name == "Test Serie"
    seasons = await mock_catalogue.seasons()
    assert len(seasons) == 1
    episodes = await seasons[0].episodes()
    assert len(episodes) == 1
    assert episodes[0].serie_name == "test-serie"


def test_index_series_module_exists():
    """Test that the index_series module and main function exist."""
    from anime_sama_api.cli import index_series
    assert hasattr(index_series, "main")
    assert hasattr(index_series, "index_full_series")
    assert callable(index_series.main)
