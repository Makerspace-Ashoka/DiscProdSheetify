import os
import sys # Import sys to exit gracefully
from dotenv import load_dotenv

# Import our components
from src.orchestrator import BotOrchestrator
from src.discord_reader import DiscordReader
from src.fetchers import BasicHtmlFetcher
from src.parsers import AiStudioParser
from src.writers import GoogleSheetWriter


def main():
    # Load variables from .env file into the environment
    load_dotenv()

    # --- Configuration and Secret Loading ---
    # We check each critical variable one by one.
    
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        print("FATAL: DISCORD_BOT_TOKEN not found in .env file.")
        sys.exit(1) # Exit the program with an error code

    ai_studio_key = os.getenv("AI_STUDIO_API_KEY")
    if not ai_studio_key:
        print("FATAL: AI_STUDIO_API_KEY not found in .env file.")
        sys.exit(1)

    sheets_creds_path = os.getenv("SERVICE_ACCOUNT_JSON_PATH")
    if not sheets_creds_path:
        print("FATAL: SERVICE_ACCOUNT_JSON_PATH not found in .env file.")
        sys.exit(1)

    # By this point, Pylance KNOWS that each of these variables must be a string.
    # The "None" timeline was terminated by sys.exit().

    # --- Component Assembly ---
    print("Assembling components...")
    fetcher = BasicHtmlFetcher()
    parser = AiStudioParser(api_key=ai_studio_key)
    writer = GoogleSheetWriter(credentials_path=sheets_creds_path)
    
    orchestrator = BotOrchestrator(fetcher=fetcher, parser=parser, writer=writer)
    discord_reader = DiscordReader(bot_token=discord_token, orchestrator=orchestrator)

    # --- Start the Bot ---
    discord_reader.run()


if __name__ == "__main__":
    main()