import asyncio
import logging
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

    async def process_url(self, url: str):
        # async with will wait here if the semaphore is full (e.g., if 3 jobs are already running)
        # before starting a new one.
        async with self._semaphore:
            logger.info(f"Worker starting job for: {url}")
            try:
                # --- ATTEMPT 1: Default Headless Fetch ---
                logger.info(f"Attempt 1 (Headless) for URL: {url}")
                content_path = await self._fetcher.fetch(url, headless=True)
                if not content_path:
                    logger.warning(f"Fetching failed for {url}. Aborting job.")
                    return

                parsed_data = await self._parser.parse(content_path)

                # --- DECISION POINT: Analyze Parser's Output ---
                if parsed_data == "ERROR_CAPTCHA_DETECTED":
                    logger.warning(f"CAPTCHA detected on first attempt for {url}. Retrying in headed mode.")

                    # --- ATTEMPT 2: Headed Fetch Fallback ---
                    content_path = await self._fetcher.fetch(url, headless=False)
                    if not content_path:
                        logger.error(f"Headed fallback fetch also failed for {url}. Aborting job.")
                        return
                    
                    # Re-parse the new screenshot
                    parsed_data = await self._parser.parse(content_path)

                # --- FINAL CHECK AND WRITE ---
                if "ERROR" in parsed_data:
                    logger.warning(f"Parsing failed for {url} with result: {parsed_data}. Aborting job.")
                    return

                await self._writer.write(parsed_data)
                logger.info(f"Successfully processed and wrote data for: {url}")

            except Exception as e:
                logger.error(f"An unhandled exception occurred while processing {url}: {e}", exc_info=True)
            finally:
                logger.info(f"Worker finished job for: {url}")