from abc import ABC, abstractmethod
import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class FetcherInterface(ABC):
    @abstractmethod
    def fetch(self, url: str) -> str:
        """Takes a URL and returns the HTML content as a string."""
        pass

class BasicHtmlFetcher(FetcherInterface):
    def fetch(self, url: str) -> str:
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
    def fetch(self, url: str) -> str:
        # Configure Chrome to run in "headless" mode (no visible UI)
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080") # A standard desktop resolution

        driver = None # Initialize to None
        try:
            # Selenium Manager automatically handles the chromedriver. Magic!
            driver = webdriver.Chrome(options=chrome_options)
            
            print(f"Selenium is navigating to {url}...")
            driver.get(url)
            
            # Wait for a few seconds to let JavaScript load.
            # A more advanced solution uses WebDriverWait, but this is fine for V2.
            time.sleep(5)
            
            # Define where to save the screenshot.
            screenshot_path = "product_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Return the path to the file.
            return screenshot_path

        except Exception as e:
            print(f"An error occurred during Selenium fetching: {e}")
            return "" # Return empty string on failure
        
        finally:
            # CRITICAL: Always close the browser to avoid memory leaks.
            if driver:
                driver.quit()