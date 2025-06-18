from abc import ABC, abstractmethod
import requests # We'll add a real library here for a more realistic example

class FetcherInterface(ABC):
    @abstractmethod
    def fetch(self, url: str) -> str:
        """Takes a URL and returns the HTML content as a string."""
        pass

class BasicHtmlFetcher(FetcherInterface):
    def fetch(self, url: str) -> str:
        try:
            print(f"Fetching HTML from {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return "" # Return empty string on failure