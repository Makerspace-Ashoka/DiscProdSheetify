from abc import ABC, abstractmethod
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class WriterInterface(ABC):
    @abstractmethod
    def write(self, data: str):
        """Takes formatted data and writes it to the destination."""
        pass

class GoogleSheetWriter(WriterInterface):
    # The SCOPES define what our service account is allowed to do.
    # For this, we only need permission to edit spreadsheets.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, credentials_path: str, spreadsheet_id: str, sheet_name: str):
        if not credentials_path:
            raise ValueError("Google credentials path cannot be empty.")
        
        # Load the service account credentials from the JSON file.
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=self.SCOPES
        )
        
        # Build the Sheets API service object.
        service = build("sheets", "v4", credentials=creds)
        
        self._sheet = service.spreadsheets()
        self._spreadsheet_id = spreadsheet_id
        self._sheet_name = sheet_name # The name of the specific sheet (e.g., "Sheet1")
        print(f"GoogleSheetWriter initialized for sheet: {spreadsheet_id}")

    def write(self, data: str):
        # The data we want to write. The Sheets API expects a list of lists.
        # Each inner list is a row.
        values = [
            [data]  # We are writing our single piece of data to the first column.
        ]
        
        body = {
            'values': values
        }
        
        try:
            print(f"Writing '{data}' to Google Sheet...")
            # We use append() to add a new row without overwriting existing data.
            # The 'valueInputOption' determines how the data is interpreted.
            # 'USER_ENTERED' means it will be treated as if you typed it directly into the cell.
            self._sheet.values().append(
                spreadsheetId=self._spreadsheet_id,
                range=self._sheet_name, # Append to the specified sheet
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            print("Write successful.")
            
        except HttpError as err:
            print(f"An error occurred while writing to Google Sheets: {err}")