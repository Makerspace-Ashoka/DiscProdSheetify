import requests
import time
import os
import asyncio
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from .interfaces import FetcherInterface

# Each module should get its own logger instance.
logger = logging.getLogger(__name__)

# The BasicHtmlFetcher is deprecated in favor of SeleniumFetcher and needs to be adapted to be async before using it in the future.
class BasicHtmlFetcher(FetcherInterface):
    async def fetch(self, url: str, headless: bool) -> str:
        """
        Fetches the HTML content of a given URL using the requests library.
        This is a simple fetcher that does not execute JavaScript.
        """
        # We wrap the blocking requests call in asyncio.to_thread to avoid blocking the event loop.
        return await asyncio.to_thread(self._blocking_fetch, url)
    
    def _blocking_fetch(self, url: str) -> str:
        # This is a more convincing set of headers, mimicking a real browser on Windows.
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive'
        }
        
        try:
            print(f"Fetching HTML from {url}...")
            # We set a timeout to prevent our bot from hanging indefinitely on a slow website.
            response = requests.get(url, headers=headers, timeout=10)
            
            # This is a critical line. It will automatically raise an exception if the
            # website returns an error (e.g., 404 Not Found, 503 Service Unavailable).
            response.raise_for_status()
            
            # If everything was successful, we return the page's HTML content.
            return response.text
        
        # This will catch any network-related errors or the error from raise_for_status().
        except requests.RequestException as e:
            print(f"Error: Could not fetch URL {url}. Reason: {e}")
            # We return an empty string to signal failure to the orchestrator.
            # This is a predictable, safe value.
            return ""

class SeleniumFetcher(FetcherInterface):
    """
    A fetcher that uses a real browser to load a page, take a screenshot,
    and return the path to the screenshot file.
    """
    def __init__(self):
        self.screenshot_dir = os.path.join("logs", "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)  # Ensure the directory exists
        logger.info(f"Screenshots will be saved to: {self.screenshot_dir}")
    
    async def fetch(self, url: str, headless: bool = True) -> str:
        """
        Asynchronously fetches a URL using Selenium.
        Cab be run in either headless (default) or headed mode.
        """
        # We wrap the entire blocking selenium logic in asyncio.to_thread
        return await asyncio.to_thread(self._blocking_fetch, url, headless)
    
    def _blocking_fetch(self, url: str, headless: bool) -> str:
        # Configure Chrome to run in "headless" mode (no visible UI)
        chrome_options = Options()

        if headless:
            logger.info("Running Selenium in HEADLESS mode.")
            chrome_options.add_argument("--headless")  # Run in headless mode
        else:
            logger.info("Running Selenium in HEADED mode.")

        chrome_options.add_argument("--window-size=1920,1080") # A standard desktop resolution

        # --- FIX: Silence Selenium DevTools logging ---
        chrome_options.add_argument("--log-level=3") # Only show fatal errors
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = ChromeService(log_path=os.devnull)

        driver = None # Initialize to None
        try:
            # Selenium Manager automatically handles the chromedriver. Magic!
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info(f"Selenium navigating to {url}...")
            driver.get(url)
            
            # Wait for a few seconds to let JavaScript load.
            # A more advanced solution uses WebDriverWait, but this is fine for V2.
            time.sleep(5)
            
            # --- NEW: Screenshot naming and logging ---
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # Sanitize the URL to create a safe filename
            sanitized_url = re.sub(r'https?://(www\.)?', '', url)
            sanitized_url = re.sub(r'[\\/:*?"<>|]', '_', sanitized_url)[:75] # Keep it reasonably short
            
            filename = f"{timestamp}_{sanitized_url}.png"
            screenshot_path = os.path.join(self.screenshot_dir, filename)
            
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            return screenshot_path

        except Exception as e:
            logger.error(f"Selenium failed to fetch {url}: {e}", exc_info=True)
            return "" # Return empty string on failure
        
        finally:
            # CRITICAL: Always close the browser to avoid memory leaks.
            if driver:
                driver.quit()