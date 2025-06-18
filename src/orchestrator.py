from .parsers import ParserInterface

class BotOrchestrator:
    # We use "Dependency Injection" to provide the parser
    def __init__(self, parser: ParserInterface):
        self._parser = parser
        print(f"Orchestrator initialized with {type(parser).__name__}.")

    def process_single_url(self, url: str):
        """
        This is the core logic for processing one URL.
        """
        print(f"\nProcessing URL: {url}")
        
        # In a real scenario, we'd call the HtmlFetcher here.
        # For now, we'll use dummy HTML.
        dummy_html = "<html><body><h1>Some Product</h1><p>Model: 123-XYZ</p></body></html>"
        print("Step 1: Fetched HTML.")

        # Here's the key part: The orchestrator doesn't know or care
        # which parser it's using. It just calls .parse().
        parsed_data = self._parser.parse(dummy_html)
        print("Step 2: Parsed HTML.")

        # In a real scenario, we'd call the SheetWriter here.
        print(f"Step 3: Writing '{parsed_data}' to Google Sheets.")
        print("Process complete.")