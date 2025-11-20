@echo off
echo Starting YouTube View Bot GUI...
echo.

REM Try different Python commands
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found: python
    python youtube_view_bot.py
    goto :end
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found: python3
    python3 youtube_view_bot.py
    goto :end
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found: py
    py youtube_view_bot.py
    goto :end
)

REM Try direct path
if exist "C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python3.exe" (
    echo Found: Direct path python3.exe
    "C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python3.exe" youtube_view_bot.py
    goto :end
)

echo ERROR: Python not found!
echo Please install Python or add it to PATH
pause
goto :end

:end
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR occurred! Error code: %ERRORLEVEL%
    pause
)

