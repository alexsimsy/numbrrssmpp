import asyncio
from aiosmpplib import ESME, PhoneNumber, SubmitSm
from loguru import logger

async def send_test_message():
    """Send a test message through the SMPP gateway"""
    logger.info("Connecting to SMPP gateway...")
    
    # Create ESME instance
    esme = ESME(
        smsc_host="127.0.0.1",
        smsc_port=2775,
        system_id="test",
        password="test"
    )
    
    try:
        # Connect to SMSC
        await esme.start()
        logger.info("Connected to SMPP gateway")
        
        # Create and send test message
        message = SubmitSm(
            source=PhoneNumber("1234"),
            destination=PhoneNumber("5678"),
            short_message="Hello, this is a test message!"
        )
        
        # Send the message
        response = await esme.submit(message)
        logger.info(f"Message sent! Message ID: {response.message_id}")
        
        # Wait a bit for any response
        await asyncio.sleep(2)
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise
    finally:
        await esme.stop()
        logger.info("Disconnected from SMPP gateway")

if __name__ == "__main__":
    asyncio.run(send_test_message()) 