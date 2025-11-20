@echo off
echo ========================================
echo Installing Python Dependencies
echo ========================================
echo.

REM Install pip if needed
python -m ensurepip --upgrade

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
echo Installing requests...
python -m pip install requests

echo Installing playwright...
python -m pip install playwright

echo Installing beautifulsoup4...
python -m pip install beautifulsoup4

echo.
echo Installing Playwright browsers...
python -m playwright install chromium

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run: python youtube_view_bot.py
echo.
pause

