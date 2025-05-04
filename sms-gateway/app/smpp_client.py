import asyncio
from loguru import logger
from aiosmpplib import ESME, PhoneNumber, AbstractHook
from aiosmpplib.log import DEBUG
from .forwarder import forward_message
from .config import (
    SMPP_HOST,
    SMPP_PORT,
    SMPP_SYSTEM_ID,
    SMPP_PASSWORD,
    LOG_LEVEL,
    LOG_FILE
)

class SMPPHook(AbstractHook):
    """
    Hook class to handle SMPP events and messages
    """
    async def received(self, smpp_message, pdu, client_id):
        """
        Handle received messages from SMSC
        Only process incoming SMS, not delivery receipts
        """
        if hasattr(smpp_message, "is_receipt") and not smpp_message.is_receipt():
            logger.info(f"Received SMS from {smpp_message.source} to {smpp_message.destination}")
            logger.debug(f"Message content: {smpp_message.short_message}")
            await forward_message(smpp_message)

    async def sending(self, smpp_message, pdu, client_id):
        """Called before sending any message to SMSC"""
        logger.debug(f"Sending message: {smpp_message}")

    async def send_error(self, smpp_message, error, client_id):
        """Handle errors during message sending"""
        logger.error(f"Error sending message: {error}")

async def run_smpp():
    """
    Initialize and run the SMPP client
    """
    # Configure logging
    logger.add(LOG_FILE, rotation="500 MB", level=LOG_LEVEL)

    try:
        # Create hook instance first
        hook = SMPPHook()
        
        # Create ESME instance with hook
        esme = ESME(
            smsc_host=SMPP_HOST,
            smsc_port=SMPP_PORT,
            system_id=SMPP_SYSTEM_ID,
            password=SMPP_PASSWORD,
            log_level=DEBUG,
            hook=hook
        )

        logger.info(f"Connecting to SMSC at {SMPP_HOST}:{SMPP_PORT}")
        await esme.start()
        logger.info("Successfully connected to SMSC")

        # Keep the connection alive
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error in SMPP client: {str(e)}")
        raise
    finally:
        if 'esme' in locals():
            await esme.stop()
            logger.info("SMPP client stopped") 