# src/writers.py
import asyncio
import logging
from .interfaces import WriterInterface
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .data_models import EnrichedProductInfo # Import the new model

logger = logging.getLogger(__name__)

class GoogleSheetWriter(WriterInterface):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, credentials_path: str, spreadsheet_id: str, sheet_name: str):
        # We only store the configuration, not the live service object.
        self._credentials_path = credentials_path
        self._spreadsheet_id = spreadsheet_id
        self._sheet_name = sheet_name
        logger.info(f"GoogleSheetWriter configured for sheet: {self._spreadsheet_id}")

    # The header row for our sheet
    HEADER = [
        "Timestamp", "User", "Platform", "Item Name", "Model Number",
        "Generic Name", "Category", "Quantity", "Unit Price", "GST Included?",
        "Total Cost", "Availability", "Est. Delivery", "URL"
    ]

    async def write(self, data: EnrichedProductInfo): # Update input type
        """Asynchronously writes a ProductInfo object to the sheet."""
        await asyncio.to_thread(self._blocking_write, data)
    
    def _blocking_write(self, data: EnrichedProductInfo): # Update input type
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

            # --- Check for Header and Add if Missing ---
            current_header = sheet.values().get(spreadsheetId=self._spreadsheet_id, range=f"{self._sheet_name}!A1:N1").execute()
            if not current_header.get('values'):
                logger.info("Header not found in sheet. Writing new header.")
                sheet.values().update(
                    spreadsheetId=self._spreadsheet_id,
                    range=f"{self._sheet_name}!A1",
                    valueInputOption="USER_ENTERED",
                    body={'values': [self.HEADER]}
                ).execute()

            # --- Unpack the data from our two sources ---
            ai = data.ai_data
            new_row = [
                data.processed_timestamp, data.requesting_user, ai.platform,
                ai.item_name, ai.model_number, ai.generic_name,
                ai.category, ai.quantity_required, ai.price_per_unit,
                str(ai.is_gst_included) if ai.is_gst_included is not None else "N/A",
                ai.total_cost, ai.availability, ai.estimated_delivery,
                data.source_url
            ]
            
            logger.info(f"Writing structured data for '{ai.item_name}' to Google Sheet...")
            sheet.values().append(
                spreadsheetId=self._spreadsheet_id,
                range=self._sheet_name,
                valueInputOption="USER_ENTERED",
                body={'values': [new_row]}
            ).execute()
            logger.info("Write successful.")
            
        except Exception as e:
            logger.error(f"An unexpected error occurred in _blocking_write for '{ai.item_name}': {e}", exc_info=True)