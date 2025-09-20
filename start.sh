#!/bin/bash

# Shopify AI Agent Startup Script

echo "Starting Shopify AI Agent..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Please create a .env file with the following variables:"
    echo "SHOPIFY_ACCESS_TOKEN=your_shopify_admin_api_token"
    echo "SHOPIFY_STOREFRONT_TOKEN=your_shopify_storefront_token"
    echo "MYSHOPIFY_DOMAIN=your-store.myshopify.com"
    echo "OPENAI_API_KEY=your_openai_api_key"
    echo "OPENAI_API_BASE=https://api.openai.com/v1"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Start the Flask application
echo "Starting Flask application..."
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python src/main.py

