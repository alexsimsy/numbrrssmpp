import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SMPP Configuration
SMPP_HOST = os.getenv("SMPP_HOST", "127.0.0.1")
SMPP_PORT = int(os.getenv("SMPP_PORT", "2775"))
SMPP_SYSTEM_ID = os.getenv("SMPP_SYSTEM_ID", "test")
SMPP_PASSWORD = os.getenv("SMPP_PASSWORD", "test")

# HTTP Forwarding Configuration
FORWARD_URL = os.getenv("FORWARD_URL", "https://kzmdngzdrcwdrhbwmvrv.supabase.co/functions/v1/receive-sms")
FORWARD_API_KEY = os.getenv("FORWARD_API_KEY", "n9mb335mpp")

# Callback Configuration
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://localhost:8000/callback")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "sms_gateway.log")

# Application Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))  # seconds 