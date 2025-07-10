import asyncio
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo # <-- ADD THIS IMPORT
from .data_models import WorkItem, AiProductInfo, EnrichedProductInfo
from .interfaces import FetcherInterface, ParserInterface, WriterInterface

logger = logging.getLogger(__name__)

class ProcessingWorker:
    def __init__(
        self,
        fetcher_class, # Pass the class, not an instance
        parser_class,  # Pass the class
        writer_class,  # Pass the class
        component_config: dict, # Pass all the config needed to init them
        max_concurrent_jobs: int
    ):
        self._fetcher_class = fetcher_class
        self._parser_class = parser_class
        self._writer_class = writer_class
        self._config = component_config
        # Only allows `max_concurrent_jobs` to run at once.
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        logger.info(f"ProcessingWorker initialized to create per-job component instances with a concurrency limit of {max_concurrent_jobs} jobs.")

    async def process_url(self, item: WorkItem):
        # async with will wait here if the semaphore is full (e.g., if 3 jobs are already running)
        # before starting a new one.
        async with self._semaphore:
            # --- PER-JOB INSTANTIATION ---
            # Every job gets its own fresh set of tools. No sharing!
            fetcher: FetcherInterface = self._fetcher_class()
            parser: ParserInterface = self._parser_class(api_key=self._config["api_key"])
            writer: WriterInterface = self._writer_class(
                credentials_path=self._config["creds_path"],
                spreadsheet_id=self._config["sheet_id"],
                sheet_name=self._config["sheet_name"],
            )
            # --- END INSTANTIATION ---

            logger.info(f"Worker starting job for URL: {item.url}")
            try:
                # --- ATTEMPT 1: Default Headless Fetch ---
                logger.info(f"Attempt 1 (Headless) for URL: {item.url}")
                content_path = await fetcher.fetch(item.url, headless=True)
                if not content_path:
                    logger.warning(f"Fetching failed for {item.url}. Aborting job.")
                    return

                ai_result = await parser.parse(content_path, item.message_content)

                # --- DECISION POINT: Now using the boolean flag ---
                if ai_result.is_captcha:
                    logger.warning(f"CAPTCHA detected on first attempt for {item.url}. Retrying in headed mode.")

                    # --- ATTEMPT 2: Headed Fetch Fallback ---
                    content_path = await fetcher.fetch(item.url, headless=False)
                    if not content_path:
                        logger.error(f"Headed fallback fetch also failed for {item.url}. Aborting job.")
                        return
                    
                    # Re-parse the new screenshot
                    ai_result = await parser.parse(content_path, item.message_content)

                # --- FINAL CHECK AND WRITE ---
                if "ERROR" in (ai_result.item_name or ""):
                    logger.warning(f"Parsing failed for {item.url} with result: {ai_result}. Aborting job.")
                    return
                
                # Enrich the data with info the LLM can't know
                final_record = EnrichedProductInfo(
                    ai_data=ai_result,
                    processed_timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
                    requesting_user=item.user_name,
                    source_url=item.url # We can add sanitization here later
                )

                await writer.write(final_record)
                logger.info(f"Successfully processed and wrote structured data for: {item.url}")

            except Exception as e:
                logger.error(f"An unhandled exception occurred while processing {item.url}: {e}", exc_info=True)
            finally:
                logger.info(f"Worker finished job for: {item.url}")