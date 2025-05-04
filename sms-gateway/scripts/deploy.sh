#!/bin/bash

# Exit on error
set -e

# Configuration
WORK_DIR="/home/ubuntu/sms-gateway"
VENV_DIR="$WORK_DIR/venv"
SERVICE_NAME="smpp-gateway"

echo "Starting deployment..."

# Create working directory if it doesn't exist
if [ ! -d "$WORK_DIR" ]; then
    echo "Creating working directory..."
    sudo mkdir -p "$WORK_DIR"
    sudo chown ubuntu:ubuntu "$WORK_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

# Copy systemd service file
echo "Configuring systemd service..."
sudo cp smpp-gateway.service /etc/systemd/system/

# Reload systemd and enable service
echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Deployment complete!"
echo "Service status:"
sudo systemctl status "$SERVICE_NAME" 