# HIGH-LEVEL MODULE: Depends only on ABSTRACTIONS (interfaces)
from .fetchers import FetcherInterface
from .parsers import ParserInterface
from .writers import WriterInterface

class BotOrchestrator:
    # Dependencies are INJECTED via the constructor.
    def __init__(
        self,
        fetcher: FetcherInterface,
        parser: ParserInterface,
        writer: WriterInterface
    ):
        self._fetcher = fetcher
        self._parser = parser
        self._writer = writer
        print(f"Orchestrator initialized with:")
        print(f"  - Fetcher: {type(fetcher).__name__}")
        print(f"  - Parser:  {type(parser).__name__}")
        print(f"  - Writer:  {type(writer).__name__}")

    def process_single_url(self, url: str):
        """
        This is the core business logic. Notice how it's clean, high-level,
        and completely independent of any specific implementation details.
        """
        print(f"\n--- Processing URL: {url} ---")
        
        # 1. Fetch
        html_content = self._fetcher.fetch(url)
        if not html_content:
            print("Processing failed: Could not fetch HTML.")
            return

        # 2. Parse
        parsed_data = self._parser.parse(html_content)
        if not parsed_data:
            print("Processing failed: Could not parse HTML.")
            return

        # 3. Write
        self._writer.write(parsed_data)
        
        print("--- Process complete. ---")