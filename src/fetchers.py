from abc import ABC, abstractmethod
import requests # The de facto standard library for making HTTP requests in Python

class FetcherInterface(ABC):
    @abstractmethod
    def fetch(self, url: str) -> str:
        """Takes a URL and returns the HTML content as a string."""
        pass

class BasicHtmlFetcher(FetcherInterface):
    def fetch(self, url: str) -> str:
        try:
            # We add a User-Agent header to identify our bot. Many websites block
            # requests from scripts with no User-Agent.
            headers = {'User-Agent': 'ProductLinkScraperBot/1.0'}
            
            print(f"Fetching HTML from {url}...")
            # We set a timeout to prevent our bot from hanging indefinitely on a slow website.
            response = requests.get(url, headers=headers, timeout=10)
            
            # This is a critical line. It will automatically raise an exception if the
            # website returns an error (e.g., 404 Not Found, 503 Service Unavailable).
            response.raise_for_status()
            
            # If everything was successful, we return the page's HTML content.
            return response.text
        
        # This will catch any network-related errors or the error from raise_for_status().
        except requests.RequestException as e:
            print(f"Error: Could not fetch URL {url}. Reason: {e}")
            # We return an empty string to signal failure to the orchestrator.
            # This is a predictable, safe value.
            return ""