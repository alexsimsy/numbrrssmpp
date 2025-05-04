# SMPP Gateway

A Python-based SMPP client that receives SMS messages and forwards them to an HTTP endpoint.

## Features

- Asynchronous SMPP client using aiosmpplib
- Message forwarding to HTTP endpoints
- Configurable retry mechanism with exponential backoff
- Comprehensive logging
- Graceful shutdown handling

## Prerequisites

- Python 3.8+
- Access to an SMPP server
- HTTP endpoint to receive forwarded messages

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smpp-gateway
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
- SMPP server details
- HTTP endpoint URL and API key
- Logging preferences
- Application settings

## Usage

Run the SMPP gateway:
```bash
python main.py
```

The application will:
1. Connect to the configured SMPP server
2. Listen for incoming SMS messages
3. Forward received messages to the configured HTTP endpoint
4. Handle reconnections and retries automatically

## Logging

Logs are written to both console and file (if configured). The log level can be adjusted in the `.env` file.

## Error Handling

The application includes:
- Automatic reconnection to SMPP server
- Retry mechanism for failed HTTP requests
- Graceful shutdown on signals (SIGTERM, SIGINT)
- Comprehensive exception handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license] 