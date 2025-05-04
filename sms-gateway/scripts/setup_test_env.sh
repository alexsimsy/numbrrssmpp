#!/bin/bash

# Create test directories
mkdir -p test/smpp_server
cd test/smpp_server

# Create Python-based SMPP server
cat > smpp_server.py << EOL
import asyncio
from aiosmpplib import ESME, PhoneNumber
from aiosmpplib.log import DEBUG

class TestSMSC:
    async def run(self):
        esme = ESME(
            smsc_host="localhost",
            smsc_port=2775,
            system_id="test",
            password="test",
            log_level=DEBUG,
        )
        
        print("Starting test SMSC server on port 2775...")
        await esme.start()
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down SMSC server...")
            await esme.stop()

if __name__ == "__main__":
    smsc = TestSMSC()
    asyncio.run(smsc.run())
EOL

# Create HTTP server
cd ../http_server

cat > server.py << EOL
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data.decode('utf-8'))
        
        logger.info(f"Received message: {message}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())

def run(server_class=HTTPServer, handler_class=MessageHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f"Starting HTTP server on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
EOL

# Create test .env file
cd ../..
cat > .env.test << EOL
# SMPP Configuration
SMPP_HOST=localhost
SMPP_PORT=2775
SMPP_SYSTEM_ID=test
SMPP_PASSWORD=test

# HTTP Forwarding Configuration
FORWARD_URL=http://localhost:8000/receive
FORWARD_API_KEY=test_key

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FILE=test_sms_gateway.log

# Application Configuration
MAX_RETRIES=3
RETRY_DELAY=5
EOL

echo "Test environment setup complete!"
echo "To start SMPP server: python3 test/smpp_server/smpp_server.py"
echo "To start HTTP server: python3 test/http_server/server.py"
echo "To run the gateway: python3 main.py --env .env.test" 