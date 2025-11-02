"""Tests for HTTP client configuration to bypass Cloudflare protection."""
import unittest
from scraper.utils import create_http_client, CURL_CFFI_AVAILABLE
from scraper.top_level import AnimeSama
from scraper.catalogue import Catalogue
from scraper.season import Season


class TestCloudflareBypass(unittest.TestCase):
    """Test that HTTP client is configured with proper headers."""
    
    def test_create_http_client_has_user_agent(self):
        """Test that create_http_client() returns a client with User-Agent header."""
        client = create_http_client()
        
        # Check that the client was created
        self.assertIsNotNone(client)
        
        if CURL_CFFI_AVAILABLE:
            # curl_cffi uses CompatibleAsyncSession wrapper
            from scraper.utils import CompatibleAsyncSession
            self.assertIsInstance(client, CompatibleAsyncSession)
        else:
            # httpx should have headers
            self.assertIn("User-Agent", client.headers)
            self.assertIn("Mozilla", client.headers["User-Agent"])
            self.assertIn("Accept", client.headers)
            self.assertIn("Accept-Language", client.headers)
            self.assertTrue(client.follow_redirects)
    
    def test_anime_sama_uses_custom_client(self):
        """Test that AnimeSama class uses the custom HTTP client."""
        anime_sama = AnimeSama("https://anime-sama.org/")
        
        # Check that the client exists and is the right type
        self.assertIsNotNone(anime_sama.client)
        
        if CURL_CFFI_AVAILABLE:
            from scraper.utils import CompatibleAsyncSession
            self.assertIsInstance(anime_sama.client, CompatibleAsyncSession)
        else:
            self.assertIn("User-Agent", anime_sama.client.headers)
            self.assertIn("Mozilla", anime_sama.client.headers["User-Agent"])
    
    def test_catalogue_uses_custom_client(self):
        """Test that Catalogue class uses the custom HTTP client."""
        catalogue = Catalogue(url="https://anime-sama.org/catalogue/frieren/")
        
        # Check that the client exists
        self.assertIsNotNone(catalogue.client)
        
        if CURL_CFFI_AVAILABLE:
            from scraper.utils import CompatibleAsyncSession
            self.assertIsInstance(catalogue.client, CompatibleAsyncSession)
        else:
            self.assertIn("User-Agent", catalogue.client.headers)
            self.assertIn("Mozilla", catalogue.client.headers["User-Agent"])
    
    def test_season_uses_custom_client(self):
        """Test that Season class uses the custom HTTP client."""
        season = Season(url="https://anime-sama.org/catalogue/frieren/saison1-vostfr/")
        
        # Check that the client exists
        self.assertIsNotNone(season.client)
        
        if CURL_CFFI_AVAILABLE:
            from scraper.utils import CompatibleAsyncSession
            self.assertIsInstance(season.client, CompatibleAsyncSession)
        else:
            self.assertIn("User-Agent", season.client.headers)
            self.assertIn("Mozilla", season.client.headers["User-Agent"])
    
    def test_custom_client_can_be_passed(self):
        """Test that a custom client can still be passed to the classes."""
        from httpx import AsyncClient
        
        custom_client = AsyncClient(headers={"Custom-Header": "test"})
        
        anime_sama = AnimeSama("https://anime-sama.org/", client=custom_client)
        self.assertEqual(anime_sama.client, custom_client)
        self.assertIn("Custom-Header", anime_sama.client.headers)


if __name__ == '__main__':
    unittest.main()
