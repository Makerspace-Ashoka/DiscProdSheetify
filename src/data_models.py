# src/data_models.py
from typing import Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass

@dataclass
class WorkItem:
    """A dataclass to hold all context for a single job."""
    url: str
    message_content: str
    user_name: str

# MODEL 1: The AI's responsibility. This is the schema we send to Gemini.
class AiProductInfo(BaseModel):
    is_captcha: bool = Field(description="Set to true ONLY if the page is a CAPTCHA or blocker page.")
    item_name: Optional[str] = Field(description="The primary name of the product.")
    model_number: Optional[str] = Field(description="The official manufacturer model number.")
    generic_name: Optional[str] = Field(description="A generic, user-friendly name for the item.")
    category: Optional[str] = Field(description="A high-level category (e.g., 'Sensor', 'Motor').")
    price_per_unit: Optional[float] = Field(description="The price for a single unit.")
    is_gst_included: Optional[bool] = Field(description="True if the price includes GST.")
    total_cost: Optional[float] = Field(description="The total final cost shown on the page.")
    availability: Optional[str] = Field(description="Availability status (e.g., 'In Stock').")
    estimated_delivery: Optional[str] = Field(description="Estimated delivery time.")
    platform: Optional[str] = Field(description="The website name (e.g., 'Amazon.in').")
    quantity_required: Optional[int] = Field(description="The quantity requested by the user.")

# MODEL 2: Our final, enriched record. This is what we write to the sheet.
class EnrichedProductInfo(BaseModel):
    # Data from the AI
    ai_data: AiProductInfo
    # Data from our trusted local context
    processed_timestamp: str
    requesting_user: str
    source_url: str