import asyncio
import sys
import os
from datetime import datetime
from loguru import logger

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.forwarder import forward_message
from app.config import FORWARD_URL, FORWARD_API_KEY

class MockSMPPMessage:
    def __init__(self):
        self.destination = "+447771844911"  # Test UK number
        self.source = "SMPP Test"           # Test sender ID
        self.log_id = "UNIQUEID"
        self.short_message = "This is a static test message"
        self.time = datetime.utcnow()
        self.data_coding = "0"
        self.long_message_tag = None

    def is_receipt(self):
        return False

async def main():
    # Configure logging
    logger.add("logs/test_forwarder.log", rotation="500 MB", level="INFO")
    
    try:
        # Create mock message
        msg = MockSMPPMessage()
        logger.info(f"Testing forwarder with message: {msg.short_message}")
        logger.info(f"Destination: {msg.destination}, Source: {msg.source}")
        
        # Log the exact payload that will be sent
        payload = {
            "did": str(msg.destination),
            "sender_id": str(msg.source),
            "message_id": msg.log_id,
            "message_payload": msg.short_message,
            "timestamp": msg.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data_coding": msg.data_coding,
            "long_message_tag": msg.long_message_tag,
        }
        logger.info(f"Forwarding to URL: {FORWARD_URL}")
        logger.info(f"Using API Key: {FORWARD_API_KEY}")
        logger.info(f"Payload: {payload}")
        
        # Forward the message
        result = await forward_message(msg)
        
        if result:
            logger.info("Message forwarded successfully!")
        else:
            logger.error("Failed to forward message")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 