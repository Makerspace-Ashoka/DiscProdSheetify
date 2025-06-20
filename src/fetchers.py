from abc import ABC, abstractmethod
import requests

class FetcherInterface(ABC):
    @abstractmethod
    def fetch(self, url: str) -> str:
        """Takes a URL and returns the HTML content as a string."""
        pass

class BasicHtmlFetcher(FetcherInterface):
    def fetch(self, url: str) -> str:
        # This is a more convincing set of headers, mimicking a real browser on Windows.
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive'
        }
        
        try:
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