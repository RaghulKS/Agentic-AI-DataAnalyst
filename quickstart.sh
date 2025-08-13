#!/bin/bash

echo "================================"
echo "AutoAnalyst Quick Start Script"
echo "================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Setting up AutoAnalyst..."
echo

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if secrets.py exists
if [ ! -f "secrets.py" ]; then
    echo
    echo "Creating secrets.py from template..."
    cp secrets.example secrets.py
    echo
    echo "IMPORTANT: Please edit secrets.py and add your OpenAI API key!"
    echo
fi

echo
echo "================================"
echo "Setup Complete!"
echo "================================"
echo
echo "To run AutoAnalyst:"
echo "  python main.py datasets/sample_sales_data.csv"
echo
echo "To see more options:"
echo "  python main.py --help"
echo