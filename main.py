import os
import sys # Import sys to exit gracefully
from dotenv import load_dotenv

# Import our components
from src.orchestrator import BotOrchestrator
from src.discord_reader import DiscordReader
from src.fetchers import BasicHtmlFetcher, SeleniumFetcher
from src.parsers import AiStudioParser, GeminiImageParser
from src.writers import GoogleSheetWriter


def main():
    # --- Configuration and Secret Loading ---
    
    # Build a path to the .env file inside the 'config' directory.
    # os.path.dirname(__file__) gets the directory of the current script (our root).
    # os.path.join() correctly combines them into a path like 'D:/.../product_scraper_bot/config/.env'.
    project_root = os.path.dirname(__file__)
    dotenv_path = os.path.join(project_root, 'config', '.env')
    
    # Load the .env file from the specified path.
    load_dotenv(dotenv_path=dotenv_path)
    
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        print("FATAL: DISCORD_BOT_TOKEN not found in .env file.")
        sys.exit(1) # Exit the program with an error code

    ai_studio_key = os.getenv("AI_STUDIO_API_KEY")
    if not ai_studio_key:
        print("FATAL: AI_STUDIO_API_KEY not found in .env file.")
        sys.exit(1)

    sheets_creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON_PATH")
    if not sheets_creds_path:
        print("FATAL: GOOGLE_SHEETS_CREDENTIALS_JSON_PATH not found in .env file.")
        sys.exit(1)
    
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("FATAL: GOOGLE_SHEET_ID not found in .env file.")
        sys.exit(1)

    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not sheet_name:
        print("FATAL: GOOGLE_SHEET_NAME not found in .env file.")
        sys.exit(1)

    # By this point, Pylance KNOWS that each of these variables must be a string.
    # The "None" timeline was terminated by sys.exit().

    # --- Component Assembly ---
    print("Assembling v2 components...")
    fetcher = SeleniumFetcher()
    parser = GeminiImageParser(api_key=ai_studio_key)
    writer = GoogleSheetWriter(
        credentials_path=sheets_creds_path,
        spreadsheet_id=sheet_id,
        sheet_name=sheet_name
    )
    
    orchestrator = BotOrchestrator(fetcher=fetcher, parser=parser, writer=writer)
    discord_reader = DiscordReader(bot_token=discord_token, orchestrator=orchestrator)

    # --- Start the Bot ---
    discord_reader.run()


if __name__ == "__main__":
    main()