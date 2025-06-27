# src/writers.py
import asyncio
import logging
from .interfaces import WriterInterface
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleSheetWriter(WriterInterface):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, credentials_path: str, spreadsheet_id: str, sheet_name: str):
        # We only store the configuration, not the live service object.
        self._credentials_path = credentials_path
        self._spreadsheet_id = spreadsheet_id
        self._sheet_name = sheet_name
        logger.info(f"GoogleSheetWriter configured for sheet: {self._spreadsheet_id}")

    async def write(self, data: str):
        # We are still dispatching the blocking work to a separate thread.
        await asyncio.to_thread(self._blocking_write, data)
    
    def _blocking_write(self, data: str):
        """
        Contains the synchronous, blocking Google Sheets API call.
        CRITICALLY, it now creates its own service object for thread safety.
        """
        try:
            # Each thread creates its own credentials and service object. No sharing.
            creds = service_account.Credentials.from_service_account_file(
                self._credentials_path, scopes=self.SCOPES
            )
            service = build("sheets", "v4", credentials=creds)
            sheet = service.spreadsheets()

            values = [[data]]
            body = {'values': values}
            
            logger.info(f"Writing '{data}' to Google Sheet...")
            sheet.values().append(
                spreadsheetId=self._spreadsheet_id,
                range=self._sheet_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            logger.info("Write successful.")
            
        except HttpError as err:
            logger.error(f"Google Sheets API error while writing '{data}': {err}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred in _blocking_write for '{data}': {e}", exc_info=True)