@echo off
REM ########################################################
REM LinkHub Bot - Windows Installation Script
REM ########################################################

setlocal enabledelayedexpansion

echo ================================================
echo      LinkHub Bot Installation Script
echo      Automated Setup for Windows
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Python found!
python --version

REM Get installation directory
set "INSTALL_DIR=%cd%"
echo.
echo [2/6] Installation directory: %INSTALL_DIR%
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist "venv\" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/6] Installing Python packages...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo Python packages installed!
echo.

REM Configuration
echo [5/6] Configuration Setup
echo.

if exist ".env" (
    echo .env file already exists!
    set /p RECONFIG="Do you want to reconfigure? (y/n): "
    if /i not "!RECONFIG!"=="y" (
        echo Skipping configuration...
        goto skip_config
    )
)

echo Please provide the following information:
echo.

REM Bot Token
:get_token
set /p BOT_TOKEN="Enter your Telegram Bot Token (from @BotFather): "
if "!BOT_TOKEN!"=="" (
    echo Bot token cannot be empty!
    goto get_token
)

REM Domain
set /p DEFAULT_DOMAIN="Enter your domain (e.g., jhopan.id) [default: jhopan.id]: "
if "!DEFAULT_DOMAIN!"=="" set DEFAULT_DOMAIN=jhopan.id

REM Subdomain
set /p DEFAULT_SUBDOMAIN="Enter your subdomain prefix (e.g., s) [default: s]: "
if "!DEFAULT_SUBDOMAIN!"=="" set DEFAULT_SUBDOMAIN=s

REM Port
set /p WEB_PORT="Enter web server port [default: 5000]: "
if "!WEB_PORT!"=="" set WEB_PORT=5000

REM TinyURL (optional)
set /p TINYURL_KEY="Enter TinyURL API Key (optional, press Enter to skip): "

REM Create .env file
(
echo # Telegram Bot Configuration
echo BOT_TOKEN=!BOT_TOKEN!
echo.
echo # Web Server Configuration
echo WEB_SERVER_HOST=0.0.0.0
echo WEB_SERVER_PORT=!WEB_PORT!
echo.
echo # Default Domain for Short Link
echo DEFAULT_DOMAIN=!DEFAULT_DOMAIN!
echo DEFAULT_SUBDOMAIN=!DEFAULT_SUBDOMAIN!
echo.
echo # TinyURL API Key (Optional^)
echo TINYURL_API_KEY=!TINYURL_KEY!
echo.
echo # Database
echo DATABASE_URL=sqlite:///shortlink.db
) > .env

echo .env file created!
echo.

:skip_config

REM Initialize database
echo [6/6] Initializing database...
python -c "from database.db_manager import DatabaseManager; db = DatabaseManager('shortlink.db'); print('Database initialized!')"

echo.
echo ================================================
echo      Installation Complete!
echo ================================================
echo.

echo Configuration Summary:
echo   Install Directory: %INSTALL_DIR%
echo   Domain: !DEFAULT_SUBDOMAIN!.!DEFAULT_DOMAIN!
echo   Web Port: !WEB_PORT!
echo   Database: %INSTALL_DIR%\shortlink.db
echo.

echo Next Steps:
echo.
echo 1. Start the bot (open 2 terminals):
echo    Terminal 1: python web\server.py
echo    Terminal 2: python run.py
echo.
echo 2. Test your bot:
echo    Open Telegram and search for your bot
echo    Send /start to begin
echo.
echo 3. Access web interface:
echo    http://localhost:!WEB_PORT!
echo.
echo For production deployment on Linux, see SETUP_GUIDE.md
echo.

pause
