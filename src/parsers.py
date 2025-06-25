from abc import ABC, abstractmethod
# The SDK import remains the same, but how we use it changes.
import google.genai as genai
from google.genai import types
import os
import PIL.Image

class ParserInterface(ABC):
    @abstractmethod
    def parse(self, html: str) -> str:
        """Takes HTML content and returns a formatted string 'item_name-product_identifier'."""
        pass

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

    def parse(self, html: str) -> str:
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
You are an expert visual data extraction bot. Your task is to analyze a screenshot of an e-commerce product page and extract two pieces of information: the product's primary name and its main model number or product identifier.

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
        print("GeminiImageParser initialized.")

    def parse(self, image_path: str) -> str:
        # The 'parse' method now receives a file path string.
        print(f"Opening image file: {image_path}")
        try:
            img = PIL.Image.open(image_path)
            
            print("Sending image to Gemini 2.0 Flash for parsing...")
            
            # The 'contents' is now a list containing both the image and a text prompt.
            # We don't need to send the system instruction again if we want to ask follow-up questions,
            # but for a single call, it can be included here as well.
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[img], # Send the image object directly
                config=types.GenerateContentConfig(
                    system_instruction=self._system_instruction
                )
            )
            
            if response.text is None:
                print("LLM returned no text. Parsing failed.")
                return "ERROR_LLM_NO_RESPONSE"
                
            parsed_data = response.text.strip()
            print(f"LLM returned: '{parsed_data}'")
            return parsed_data

        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return "ERROR_FILE_NOT_FOUND"
        except Exception as e:
            print(f"An error occurred during image parsing: {e}")
            return "ERROR_API_CALL_FAILED"
        finally:
            # Clean up the screenshot file after we're done with it.
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Cleaned up {image_path}")

# The LocalLlmParser remains untouched, a testament to our decoupled design.
class LocalLlmParser(ParserInterface):
    def parse(self, html: str) -> str:
        return "Local_LLM_Parser_Result-DUMMY_MODEL"