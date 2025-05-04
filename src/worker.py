from workers import Response, Request
import asyncio
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMPPWorker:
    def __init__(self, env):
        self.env = env
        self.smpp_host = env.SMPP_HOST
        self.smpp_port = int(env.SMPP_PORT)
        self.system_id = env.SMPP_SYSTEM_ID
        self.password = env.SMPP_PASSWORD
        self.supabase_url = env.SUPABASE_URL
        self.supabase_key = env.SUPABASE_KEY
        self.test_endpoint = env.TEST_HTTP_ENDPOINT

    async def handle_smpp_message(self, message):
        """Process incoming SMPP message and forward to HTTP endpoint"""
        try:
            # Log the message receipt
            logger.info(f"Received SMPP message: {message}")
            
            # Prepare the message for forwarding
            payload = {
                "source": message.get("source_addr"),
                "destination": message.get("destination_addr"),
                "message": message.get("short_message"),
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": message.get("message_id")
            }

            # Forward to Supabase
            await self.forward_to_http(payload)
            
            return True
        except Exception as e:
            logger.error(f"Error processing SMPP message: {str(e)}")
            return False

    async def forward_to_http(self, payload):
        """Forward message to configured HTTP endpoint"""
        try:
            # In production, use Supabase endpoint
            endpoint = self.supabase_url if self.env.ENVIRONMENT == "production" else self.test_endpoint
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.supabase_key}"
            }
            
            async with fetch(endpoint, {
                "method": "POST",
                "headers": headers,
                "body": json.dumps(payload)
            }) as response:
                if response.status != 200:
                    logger.error(f"Failed to forward message: {response.status}")
                return response.status == 200
        except Exception as e:
            logger.error(f"Error forwarding message: {str(e)}")
            return False

    async def handle_test_endpoint(self, request):
        """Handle test HTTP endpoint for local testing"""
        if request.method == "POST":
            try:
                data = await request.json()
                logger.info(f"Test endpoint received: {data}")
                return Response.json({"status": "success", "data": data})
            except Exception as e:
                return Response.json({"status": "error", "message": str(e)}, status=400)
        return Response.json({"status": "error", "message": "Method not allowed"}, status=405)

async def on_fetch(request, env):
    worker = SMPPWorker(env)
    
    # Handle test endpoint requests
    if request.url.endswith("/test"):
        return await worker.handle_test_endpoint(request)
    
    # Handle SMPP messages
    if request.method == "POST" and request.headers.get("Content-Type") == "application/json":
        try:
            message = await request.json()
            success = await worker.handle_smpp_message(message)
            return Response.json({"status": "success" if success else "error"})
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return Response.json({"status": "error", "message": str(e)}, status=400)
    
    return Response.json({"status": "error", "message": "Invalid request"}, status=400) 