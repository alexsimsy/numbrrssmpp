import asyncio
from loguru import logger
from aiosmpplib import SMSCServer, PhoneNumber, AbstractHook

class SMSCHook(AbstractHook):
    """Hook for handling SMSC events"""
    async def received(self, smpp_message, pdu, client_id):
        """Handle received messages"""
        logger.info(f"SMSC received message: {smpp_message.short_message}")
        # Echo the message back
        response = smpp_message.clone()
        response.source, response.destination = response.destination, response.source
        response.short_message = f"Echo: {response.short_message}"
        return response

async def run_test_smsc():
    """Run a test SMSC server"""
    logger.info("Starting test SMSC server...")
    
    # Create SMSC server
    smsc = SMSCServer(
        host="127.0.0.1",
        port=2775,
        system_id="test",
        password="test",
        hook=SMSCHook()
    )
    
    try:
        await smsc.start()
        logger.info("SMSC server started on port 2775")
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"SMSC server error: {str(e)}")
        raise
    finally:
        await smsc.stop()
        logger.info("SMSC server stopped")

if __name__ == "__main__":
    asyncio.run(run_test_smsc()) 