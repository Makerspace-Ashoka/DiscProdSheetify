import google.genai as genai
from google.genai import types
import os
import PIL.Image
import asyncio
import logging
from .interfaces import ParserInterface

logger = logging.getLogger(__name__)

# The AiStudioParser class is deprecated in favor of GeminiImageParser and needs to be adapeted to be async and use logging 
# before using it in the future.
class AiStudioParser(ParserInterface):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("AI Studio API key cannot be empty.")
        
        # CORRECTED: Instantiate a client object instead of using a global configuration.
        # This is a much better pattern.
        self._client = genai.Client(api_key=api_key)
        
        # We define the system instruction once. This is cleaner than putting it in every prompt.
        self._system_instruction = """
You are an expert data extraction bot. Your task is to analyze the raw HTML content of an e-commerce product page and extract two pieces of information: the product's primary name and its main model number or product identifier.

Combine these two pieces of information into a single string with a hyphen separator in the format: item_name-product_identifier.
- Replace spaces in the item name with underscores.
- The model number should be the official manufacturer part number, not a vendor-specific SKU if possible.

Examples:
- For "NVIDIA GeForce RTX 4090 GPU" with model "GA102-300-A1", you should return: NVIDIA_GeForce_RTX_4090_GPU-GA102-300-A1
- For "Arduino Uno Rev3" with model "A000066", you should return: Arduino_Uno_Rev3-A000066

If you cannot confidently determine both the name and the identifier, you MUST return the exact string: ERROR_CANNOT_PARSE
"""
        print("AiStudioParser initialized with new client model.")

    async def parse(self, content_path_or_html: str) -> str:
        html = content_path_or_html
        try:
            print("Sending HTML to Gemini 2.0 Flash for parsing...")
            
            # CORRECTED: Use the client to call the model and pass the system instruction in the config.
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=html, # The HTML is now the direct 'contents'
                config=types.GenerateContentConfig(
                    system_instruction=self._system_instruction
                )
            )

            # --- START OF CHECK ---
            # Handle the potential for an empty or non-existent text response.
            if response.text is None:
                print("LLM returned no text. Parsing failed.")
                return "ERROR_LLM_NO_RESPONSE"
            # --- END OF CHECK ---
            
            # The response object itself might have changed, but .text is usually a safe bet.
            # .strip() remains essential for cleaning whitespace.
            parsed_data = response.text.strip()
            
            print(f"LLM returned: '{parsed_data}'")
            return parsed_data
            
        except Exception as e:
            print(f"An error occurred while calling the Gemini API: {e}")
            return "ERROR_API_CALL_FAILED"

class GeminiImageParser(ParserInterface):
    """
    A parser that takes a file path to an image, sends it to a multimodal
    LLM, and parses the response.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("AI Studio API key cannot be empty.")
        self._client = genai.Client(api_key=api_key)
        self._system_instruction = """
You are an expert visual data extraction bot. Your first and most important task is to determine if the provided screenshot is a CAPTCHA page, a "prove you are human" challenge, a "click to continue" button, or any other form of interstitial that is blocking the main product content.

- If you detect any such blocker, you MUST return the exact string: ERROR_CAPTCHA_DETECTED
- Otherwise, your task is to analyze the e-commerce product page screenshot and extract two pieces of information: the product's primary name and its main model number.

Combine these two pieces of information into a single string with a hyphen separator in the format: item_name-product_identifier.
- Replace spaces in the item name with underscores.
- The model number should be the official manufacturer part number, not a vendor-specific SKU.

Examples:
- For "NVIDIA GeForce RTX 4090 GPU" with model "GA102-300-A1", you should return: NVIDIA_GeForce_RTX_4090_GPU-GA102-300-A1
- For "Arduino Uno Rev3" with model "A000066", you should return: Arduino_Uno_Rev3-A000066
- For "XL6019E1 DC-DC Step-Up Boost Converter Performance Booster Circuit Board (Made In India).", you should return: DC-DC_Step-Up_Boost_Converter_Circuit_Board-XL6019E1
- For "LM2596S-ADJ/NOPB - 40V 3A Step-Down Regulator SIMPLE SWITCHER 5Pin TO-263", you should return: 40V_3A_Step-Down_Regulator_5Pin_TO-263-LM2596S-ADJ/NOPB

If you cannot confidently determine both the name and the identifier, you MUST return the exact string: ERROR_CANNOT_PARSE
"""
        logger.info("GeminiImageParser initialized with CAPTCHA detection prompt.")

    async def parse(self, content_path_or_html: str) -> str:
        image_path = content_path_or_html
        return await asyncio.to_thread(self._blocking_parse, image_path)

    def _blocking_parse(self, image_path: str) -> str:
        logger.info(f"Parser starting work on {image_path}")
        try:
            img = PIL.Image.open(image_path)
            logger.info(f"Sending {image_path} to Gemini API...")
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[img],
                config=types.GenerateContentConfig(system_instruction=self._system_instruction)
            )
            
            if response.text is None:
                logger.warning("LLM returned no text.")
                return "ERROR_LLM_NO_RESPONSE"
                
            parsed_data = response.text.strip()
            logger.info(f"LLM returned: '{parsed_data}'")
            return parsed_data
        except FileNotFoundError:
            logger.error(f"Parser error: Image file not found at {image_path}")
            return "ERROR_FILE_NOT_FOUND"
        except Exception as e:
            logger.error(f"Gemini API call failed for {image_path}: {e}", exc_info=True)
            return "ERROR_API_CALL_FAILED"
