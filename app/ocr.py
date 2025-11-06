import pytesseract
from PIL import Image
import requests
import io
import re

from app.config import get_logger

logger = get_logger(__name__)

def process_payment_slip(bot, file_id: str) -> dict | None:
    """
    Downloads a payment slip image from Telegram, performs OCR, and extracts details.

    Args:
        bot: The Telegram bot instance.
        file_id: The file_id of the image to process.

    Returns:
        A dictionary containing extracted 'name' and 'amount', or None if processing fails.
    """
    try:
        logger.info(f"Processing payment slip with file_id: {file_id}")
        file = bot.get_file(file_id)
        file_url = file.file_path

        # Download the image
        response = requests.get(file_url)
        response.raise_for_status() # Raise an exception for bad status codes
        image_bytes = io.BytesIO(response.content)
        image = Image.open(image_bytes)

        # Perform OCR
        ocr_text = pytesseract.image_to_string(image, lang='tha+eng')
        logger.debug(f"OCR Raw Text:\n{ocr_text}")

        # Extract information (this is a simplified example, regex might need tuning)
        name = extract_name(ocr_text)
        amount = extract_amount(ocr_text)

        if name and amount:
            logger.info(f"Successfully extracted Name: '{name}', Amount: {amount}")
            return {"name": name, "amount": amount}
        else:
            logger.warning("Could not extract name or amount from OCR text.")
            return None

    except Exception as e:
        logger.error(f"An error occurred during OCR processing: {e}", exc_info=True)
        return None

def extract_name(text: str) -> str | None:
    """Extracts a name from the OCR text."""
    # This regex looks for lines that might contain a name, common in Thai slips.
    # It's a simple example and might need significant improvement.
    match = re.search(r"(ชื่อ|Name|To)[:\s]*(.+)", text, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return None

def extract_amount(text: str) -> float | None:
    """Extracts the transfer amount from the OCR text."""
    # This regex looks for a floating point number, possibly with commas.
    # It targets lines that often contain the total amount.
    match = re.search(r"(จำนวนเงิน|Amount|Total)[:\s]*([\d,]+\.\d{2})", text, re.IGNORECASE)
    if match:
        amount_str = match.group(2).replace(",", "")
        return float(amount_str)
    
    # Fallback for lines that just have the number
    match = re.search(r"([\d,]+\.\d{2})", text)
    if match:
        amount_str = match.group(1).replace(",", "")
        return float(amount_str)
        
    return None
