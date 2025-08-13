@echo off
echo ================================
echo AutoAnalyst Quick Start Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

echo Setting up AutoAnalyst...
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if secrets.py exists
if not exist secrets.py (
    echo.
    echo Creating secrets.py from template...
    copy secrets.example secrets.py
    echo.
    echo IMPORTANT: Please edit secrets.py and add your OpenAI API key!
    echo.
    pause
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To run AutoAnalyst:
echo   python main.py datasets/sample_sales_data.csv
echo.
echo To see more options:
echo   python main.py --help
echo.
pause