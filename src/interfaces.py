from abc import ABC, abstractmethod
from .data_models import ProductInfo

class FetcherInterface(ABC):
    @abstractmethod
    async def fetch(self, url: str, headless: bool) -> str:
        """Asynchronously fetches content and returns a path (for images) or the content itself (for HTML)."""
        pass

class ParserInterface(ABC):
    @abstractmethod
    async def parse(self, content_path_or_html: str, user_message: str) -> ProductInfo:
        """Asynchronously parses content (from a file path or a string) and returns structured data."""
        pass

class WriterInterface(ABC):
    @abstractmethod
    async def write(self, data: ProductInfo):
        """Asynchronously writes data to the destination."""
        pass