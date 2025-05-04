import signal
import sys
import os
import argparse
import asyncio
from loguru import logger
from app.smpp_server import run_server
from app.callback import app
import uvicorn
from multiprocessing import Process

def run_fastapi():
    """Run the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def run_smpp_server():
    """Run the SMPP server"""
    await run_server()

async def main_async():
    """Async main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SMPP Gateway')
    parser.add_argument('--env', type=str, help='Path to environment file', default='.env')
    args = parser.parse_args()

    # Load environment file
    if os.path.exists(args.env):
        logger.info(f"Loading environment from {args.env}")
        from dotenv import load_dotenv
        load_dotenv(args.env)
    else:
        logger.warning(f"Environment file {args.env} not found, using default environment")
    
    try:
        # Start FastAPI server in a separate process
        fastapi_process = Process(target=run_fastapi)
        fastapi_process.start()
        
        # Run SMPP server in the main process
        await run_smpp_server()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        if 'fastapi_process' in locals():
            fastapi_process.terminate()
            fastapi_process.join()

def main():
    """Main entry point."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 