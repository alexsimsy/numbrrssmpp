#!/bin/bash

# Exit on error
set -e

# Configuration
REMOTE_USER="ubuntu"  # Default Lightsail user
REMOTE_HOST="$1"      # Pass Lightsail instance IP as first argument
SSH_KEY="$2"          # Pass path to SSH key as second argument
LOCAL_DIR="$(dirname "$(dirname "$0")")"  # Get the project root directory
REMOTE_DIR="/tmp/sms-gateway-deploy"

if [ -z "$REMOTE_HOST" ] || [ -z "$SSH_KEY" ]; then
    echo "Usage: $0 <lightsail-instance-ip> <path-to-ssh-key>"
    exit 1
fi

# Create deployment archive
echo "Creating deployment archive..."
tar -czf /tmp/sms-gateway.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env*' \
    -C "$LOCAL_DIR" .

# Copy files to remote server
echo "Copying files to remote server..."
scp -i "$SSH_KEY" /tmp/sms-gateway.tar.gz "$REMOTE_USER@$REMOTE_HOST:/tmp/"
scp -i "$SSH_KEY" "$LOCAL_DIR/scripts/deploy.sh" "$REMOTE_USER@$REMOTE_HOST:/tmp/"

# Execute deployment on remote server
echo "Executing deployment on remote server..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
    # Extract deployment files
    sudo rm -rf /tmp/sms-gateway
    mkdir -p /tmp/sms-gateway
    tar -xzf /tmp/sms-gateway.tar.gz -C /tmp/sms-gateway

    # Make deploy script executable and run it
    chmod +x /tmp/deploy.sh
    sudo /tmp/deploy.sh

    # Clean up
    rm -f /tmp/sms-gateway.tar.gz
    rm -rf /tmp/sms-gateway
EOF

echo "Deployment to Lightsail complete!"
echo "Remember to:"
echo "1. Copy your .env file to the server: scp -i $SSH_KEY .env $REMOTE_USER@$REMOTE_HOST:/opt/sms-gateway/.env"
echo "2. Start the service: ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'sudo systemctl start sms-gateway'"
echo "3. Check the status: ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST 'sudo systemctl status sms-gateway'" 