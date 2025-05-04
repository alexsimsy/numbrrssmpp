import asyncio
import httpx
from loguru import logger
from .config import FORWARD_URL, FORWARD_API_KEY, MAX_RETRIES, RETRY_DELAY

async def forward_message(smpp_message):
    """
    Forward received SMS message to configured HTTP endpoint.
    Implements retry logic with exponential backoff.
    """
    payload = {
        "did": str(smpp_message.destination),
        "sender_id": str(smpp_message.source),
        "message_id": getattr(smpp_message, "log_id", None),
        "message_payload": smpp_message.short_message,
        "timestamp": smpp_message.time.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(smpp_message, "time") else None,
        "data_coding": getattr(smpp_message, "data_coding", None),
        "long_message_tag": getattr(smpp_message, "long_message_tag", None),
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FORWARD_API_KEY}"
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(FORWARD_URL, json=payload, headers=headers)
                resp.raise_for_status()
                logger.info(f"Successfully forwarded message to {FORWARD_URL}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to forward message (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error("Max retries reached. Message forwarding failed.")
                return False
        except Exception as e:
            logger.error(f"Unexpected error while forwarding message: {str(e)}")
            return False 