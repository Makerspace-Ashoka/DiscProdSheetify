from abc import ABC, abstractmethod

# This is our "Interface" - the standard plug socket.
class ParserInterface(ABC):
    @abstractmethod
    def parse(self, html: str) -> str:
        """Takes HTML content and returns a formatted string 'item_name-product_identifier'."""
        pass

# This is our first "device" that fits the plug.
class AiStudioParser(ParserInterface):
    def __init__(self, api_key: str):
        self._api_key = api_key # Store the key for later use

    def parse(self, html: str) -> str:
        print("Connecting to AI Studio with a key ending in '...{self._api_key[-4]}'")
        return "NVIDIA_RTX_4090-GA102-300-A1"

# This is our second "device", ready for the future.
class LocalLlmParser(ParserInterface):
    def parse(self, html: str) -> str:
        print("Connecting to Local LLM server...")
        # (Future code for the local model goes here)
        return "Arduino_Uno-ATMEGA328P"