@echo off
echo ========================================
echo Installing Git for Windows
echo ========================================
echo.

echo Downloading Git installer...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe' -OutFile 'Git-installer.exe'}"

echo.
echo Installing Git...
echo Please follow the installation wizard (use default settings)
echo.

start /wait Git-installer.exe

echo.
echo Cleaning up...
del Git-installer.exe

echo.
echo ========================================
echo Git Installation Complete!
echo ========================================
echo.
echo Please close this window and run: push_to_github.bat
echo.
pause

