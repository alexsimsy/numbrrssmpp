# SMPP Worker for Cloudflare

This is a Cloudflare Worker implementation that receives SMS messages via SMPP and forwards them to a Supabase application via HTTP.

## Features

- SMPP message reception
- Message forwarding to Supabase
- Local test endpoint for development
- Logging system
- Environment-based configuration

## Setup

1. Install Wrangler CLI:
```bash
npm install -g wrangler
```

2. Configure your environment variables in `wrangler.toml`:
```toml
[vars]
SMPP_HOST = "your-smpp-host"
SMPP_PORT = "2775"
SMPP_SYSTEM_ID = "your-system-id"
SMPP_PASSWORD = "your-password"
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
```

3. Deploy to Cloudflare:
```bash
wrangler deploy
```

## Development

To run locally:
```bash
wrangler dev
```

The worker will be available at `http://localhost:8787`

### Test Endpoint

A test endpoint is available at `/test` for local development. Send POST requests with JSON payloads to test the message forwarding:

```bash
curl -X POST http://localhost:8787/test \
  -H "Content-Type: application/json" \
  -d '{"source_addr": "1234567890", "destination_addr": "0987654321", "short_message": "Test message"}'
```

## Message Format

Incoming SMPP messages are processed and forwarded with the following structure:

```json
{
  "source": "source_addr",
  "destination": "destination_addr",
  "message": "short_message",
  "timestamp": "ISO-8601 timestamp",
  "message_id": "message_id"
}
```

## Logging

Logs are stored in Cloudflare's logging system. The log level can be configured in `wrangler.toml`:

```toml
[vars]
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Security

- All sensitive configuration is stored in environment variables
- Supabase authentication is handled via API key
- SMPP credentials are securely stored in environment variables

## License

MIT License
