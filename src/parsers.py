import asyncio
import logging
import PIL.Image
import google.genai as genai
from google.genai import types
from .interfaces import ParserInterface
from .data_models import ProductInfo

logger = logging.getLogger(__name__)

class GeminiImageParser(ParserInterface):
    """
    A parser that takes a file path to an image, sends it to a multimodal
    LLM, and parses the response.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("AI Studio API key cannot be empty.")
        self._client = genai.Client(api_key=api_key)
        # The system instruction now focuses on its role, not the output format.
        self._system_instruction = """You are an expert visual data extraction bot for electronics components and e-commerce websites."""
        logger.info("GeminiImageParser initialized with and structured output and CAPTCHA detection prompt.")

    async def parse(self, content_path_or_html: str, user_message: str) -> ProductInfo:
        """Parses an image and user message, returning a structured ProductInfo object."""
        image_path = content_path_or_html
        return await asyncio.to_thread(self._blocking_parse, image_path, user_message)

    def _blocking_parse(self, image_path: str, user_message: str) -> ProductInfo:
        logger.info(f"Parser starting structured extraction for {image_path}")
        try:
            img = PIL.Image.open(image_path)
            # The prompt now includes the user's message for context.
            prompt = f"""
            Analyze the following e-commerce product page screenshot and the user's message.
            Extract all the fields defined in the provided JSON schema.
            Prioritize detecting if the page is a CAPTCHA.
            If the user's message mentions a quantity (e.g., "we need 5 of these"), extract it.

            User's message: "{user_message}"
            """
            logger.info(f"Sending {image_path} to Gemini API...")
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                # Contents now contains the text prompt AND the image
                contents=[prompt, img],
                # Contents now contains the text prompt AND the image
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ProductInfo,
                }
            )
                
            # The SDK automatically parses the JSON into our Pydantic object.
            parsed_result = response.parsed

            if not isinstance(parsed_result, ProductInfo):
                logger.error(f"LLM did not return the expected ProductInfo object. Got type: {type(parsed_result)}")
                # We still need to return a valid ProductInfo object on failure.
                return ProductInfo(
                    is_captcha=False,
                    processed_timestamp="",
                    requesting_user="",
                    source_url="",
                    item_name="ERROR_INVALID_TYPE",
                    model_number=None,
                    generic_name=None,
                    category=None,
                    price_per_unit=None,
                    is_gst_included=None,
                    total_cost=None,
                    availability=None,
                    estimated_delivery=None,
                    platform=None,
                    quantity_required=None
                )

            parsed_object: ProductInfo = parsed_result
            logger.info(f"LLM returned structured data for {image_path}")
            return parsed_object

        except Exception as e:
            logger.error(f"Structured parsing failed for {image_path}: {e}", exc_info=True)
            # --- PROVIDE ALL REQUIRED FIELDS ---
            return ProductInfo(
                processed_timestamp="",
                requesting_user="",
                source_url="",
                is_captcha=False,
                item_name="ERROR_API_CALL",
                # Provide None for all optional fields
                model_number=None,
                generic_name=None,
                category=None,
                price_per_unit=None,
                is_gst_included=None,
                total_cost=None,
                availability=None,
                estimated_delivery=None,
                platform=None,
                quantity_required=None
            )