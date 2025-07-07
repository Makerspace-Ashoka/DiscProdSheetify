import asyncio
import logging
from datetime import datetime, timezone
from .data_models import WorkItem, ProductInfo
from .interfaces import FetcherInterface, ParserInterface, WriterInterface

logger = logging.getLogger(__name__)

class ProcessingWorker:
    def __init__(self, fetcher: FetcherInterface, parser: ParserInterface, writer: WriterInterface, max_concurrent_jobs: int):
        self._fetcher = fetcher
        self._parser = parser
        self._writer = writer
        # Only allows `max_concurrent_jobs` to run at once.
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        logger.info(f"ProcessingWorker initialized with a concurrency limit of {max_concurrent_jobs} jobs.")

    async def process_url(self, item: WorkItem):
        # async with will wait here if the semaphore is full (e.g., if 3 jobs are already running)
        # before starting a new one.
        async with self._semaphore:
            logger.info(f"Worker starting job for URL: {item.url}")
            try:
                # --- ATTEMPT 1: Default Headless Fetch ---
                logger.info(f"Attempt 1 (Headless) for URL: {item.url}")
                content_path = await self._fetcher.fetch(item.url, headless=True)
                if not content_path:
                    logger.warning(f"Fetching failed for {item.url}. Aborting job.")
                    return

                parsed_data = await self._parser.parse(content_path, item.message_content)

                # --- DECISION POINT: Now using the boolean flag ---
                if parsed_data.is_captcha:
                    logger.warning(f"CAPTCHA detected on first attempt for {item.url}. Retrying in headed mode.")

                    # --- ATTEMPT 2: Headed Fetch Fallback ---
                    content_path = await self._fetcher.fetch(item.url, headless=False)
                    if not content_path:
                        logger.error(f"Headed fallback fetch also failed for {item.url}. Aborting job.")
                        return
                    
                    # Re-parse the new screenshot
                    parsed_data = await self._parser.parse(content_path, item.message_content)

                # --- FINAL CHECK AND WRITE ---
                if "ERROR" in (parsed_data.item_name or ""):
                    logger.warning(f"Parsing failed for {item.url} with result: {parsed_data}. Aborting job.")
                    return
                
                # Enrich the data with info the LLM can't know
                parsed_data.processed_timestamp = datetime.now(timezone.utc).isoformat()
                parsed_data.requesting_user = item.user_name
                parsed_data.source_url = item.url # We can add sanitization here later

                await self._writer.write(parsed_data)
                logger.info(f"Successfully processed and wrote structured data for: {item.url}")

            except Exception as e:
                logger.error(f"An unhandled exception occurred while processing {item.url}: {e}", exc_info=True)
            finally:
                logger.info(f"Worker finished job for: {item.url}")