import os
from dotenv import load_dotenv

from src.orchestrator import BotOrchestrator
# ... (our other imports)

# We'll need to update our class constructors to accept the secrets
from src.parsers import AiStudioParser
from src.writers import GoogleSheetWriter
from src.fetchers import BasicHtmlFetcher


def main():
    # Load variables from .env file into the environment
    load_dotenv()

    # Retrieve the secrets from the environment
    ai_studio_key = os.getenv("AI_STUDIO_API_KEY")
    sheets_creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON_PATH")

    # A check to make sure the secrets are loaded
    if not ai_studio_key or not sheets_creds_path:
        print("Error: Secrets not found. Make sure you have a .env file with the correct variables.")
        return

    # Now we pass the secrets to the constructors of the classes that need them.
    # This is still Dependency Injection!
    parser = AiStudioParser(api_key=ai_studio_key)
    writer = GoogleSheetWriter(credentials_path=sheets_creds_path)
    fetcher = BasicHtmlFetcher() # Doesn't need a secret

    bot = BotOrchestrator(fetcher=fetcher, parser=parser, writer=writer)
    bot.process_single_url("https://example.com")


if __name__ == "__main__":
    main()