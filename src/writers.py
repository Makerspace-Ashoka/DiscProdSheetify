from abc import ABC, abstractmethod

class WriterInterface(ABC):
    @abstractmethod
    def write(self, data: str):
        """Takes formatted data and writes it to the destination."""
        pass

class GoogleSheetWriter(WriterInterface):
    def write(self, data: str):
        # In the future, this will contain Google Sheets API logic.
        print(f"Writing '{data}' to Google Sheet...")
        # For now, we just pretend it worked.
        print("Write successful.")