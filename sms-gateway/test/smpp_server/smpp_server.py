import asyncio
import socket
from aiosmpplib import ESME, PhoneNumber
from aiosmpplib.log import DEBUG
from loguru import logger

class TestSMSC:
    async def run(self):
        # Configure logging
        logger.add("test/smpp_server/smpp_server.log", rotation="500 MB", level="DEBUG")
        
        # Create a socket server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', 2775))
        server.listen(1)
        
        logger.info("Starting test SMSC server on port 2775...")
        
        try:
            while True:
                client_socket, address = server.accept()
                logger.info(f"Accepted connection from {address}")
                
                # Create ESME instance for this connection
                esme = ESME(
                    smsc_host="localhost",
                    smsc_port=2775,
                    system_id="test",
                    password="test",
                    log_level=DEBUG,
                )
                
                try:
                    logger.info("Starting ESME...")
                    await esme.start()
                    logger.info("ESME started successfully")
                    
                    # Add message handler
                    async def handle_message(smpp_message, pdu, client_id):
                        logger.info(f"Received message: {smpp_message}")
                        if hasattr(smpp_message, "short_message"):
                            logger.info(f"Message content: {smpp_message.short_message}")
                    
                    esme.hook = type('Hook', (object,), {
                        'received': handle_message
                    })()
                    
                    logger.info("Message handler set up")
                    
                    # Keep the connection alive
                    while True:
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error in ESME: {str(e)}")
                    raise
                finally:
                    await esme.stop()
                    logger.info("ESME stopped")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down SMSC server...")
            server.close()
            logger.info("SMSC server stopped")

if __name__ == "__main__":
    smsc = TestSMSC()
    asyncio.run(smsc.run())
