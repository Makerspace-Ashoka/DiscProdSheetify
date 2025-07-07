import os
import asyncio
import sys # Import sys to exit gracefully
import logging
from dotenv import load_dotenv
from src.worker import ProcessingWorker

# Import our components
from src.discord_reader import DiscordReader
from src.fetchers import SeleniumFetcher
from src.interfaces import FetcherInterface, ParserInterface, WriterInterface
from src.logging_config import setup_logging
from src.parsers import GeminiImageParser
from src.worker import ProcessingWorker
from src.writers import GoogleSheetWriter

logger = logging.getLogger(__name__)

# The worker task that consumes from the queue
async def queue_consumer(work_queue: asyncio.Queue, worker: ProcessingWorker):
    logger.info("Queue consumer started.")
    while True:
        # We now get a WorkItem object from the queue.
        work_item = await work_queue.get()

        # --- DEBUGGING LOG ---
        logger.info(f"Got object of type {type(work_item).__name__} from queue.")

        logger.info(f"Got item from queue for URL: {work_item.url}. Creating task.")
        asyncio.create_task(worker.process_url(work_item))
        # We mark the task as done immediately for the queue.
        # The actual work happens in the background.
        work_queue.task_done()

async def main():
    setup_logging()  # Set up logging configuration

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
        logger.info("FATAL: DISCORD_BOT_TOKEN not found in .env file.")
        sys.exit(1) # Exit the program with an error code

    ai_studio_key = os.getenv("AI_STUDIO_API_KEY")
    if not ai_studio_key:
        logger.info("FATAL: AI_STUDIO_API_KEY not found in .env file.")
        sys.exit(1)

    sheets_creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON_PATH")
    if not sheets_creds_path:
        logger.info("FATAL: GOOGLE_SHEETS_CREDENTIALS_JSON_PATH not found in .env file.")
        sys.exit(1)
    
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        logger.info("FATAL: GOOGLE_SHEET_ID not found in .env file.")
        sys.exit(1)

    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not sheet_name:
        logger.info("FATAL: GOOGLE_SHEET_NAME not found in .env file.")
        sys.exit(1)

    # By this point, Pylance KNOWS that each of these variables must be a string.
    # The "None" timeline was terminated by sys.exit().

    # --- Assemble Components ---
    logger.info("Assembling V3 components...")
    work_queue = asyncio.Queue()
    fetcher: FetcherInterface = SeleniumFetcher()
    parser: ParserInterface = GeminiImageParser(api_key=ai_studio_key)
    writer: WriterInterface = GoogleSheetWriter(
        credentials_path=sheets_creds_path,
        spreadsheet_id=sheet_id,
        sheet_name=sheet_name
    )
    worker = ProcessingWorker(fetcher, parser, writer, max_concurrent_jobs=3)
    discord_reader = DiscordReader(bot_token=discord_token, work_queue=work_queue)

    # --- Start All Services ---
    try:
        logger.info("Starting all services...")
        # Start the queue consumer in the background
        consumer_task = asyncio.create_task(queue_consumer(work_queue, worker))
        # Start the Discord bot in the foreground. This will run forever.
        await discord_reader.start()
    except KeyboardInterrupt:
        logger.info("Shutdown signal received.")
    finally:
        logger.info("Application shutting down.")
        # In a real app, you might have more cleanup here.
        # For now, tasks will be cancelled when the program exits.

if __name__ == "__main__":
    asyncio.run(main())