from .parsers import ParserInterface 

class BotOrchestrator:
    # We "plug in" the device when we create the orchestrator.
    def __init__(self, parser: ParserInterface):
        self._parser = parser
        # ... other initializations for fetcher, writer ...

    def process_url(self, url: str):
        # ... fetch the html ...
        html = "<html>... some dummy html ...</html>"

        # The orchestrator is CLOSED for modification. It doesn't care which parser it is.
        # It just calls the standard 'parse' method.
        parsed_data = self._parser.parse(html) 
        
        print(f"Orchestrator received data: {parsed_data}")
        # ... send data to the SheetWriter ...