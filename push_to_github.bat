@echo off
echo ========================================
echo Push to GitHub: ngocsuo/mtview
echo ========================================
echo.

REM Set Git path
set "GIT_PATH=C:\Program Files\Git\bin\git.exe"

REM Check if git is installed
if not exist "%GIT_PATH%" (
    set "GIT_PATH=git.exe"
)

REM Check if git works
"%GIT_PATH%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not found!
    echo Please install Git from: https://git-scm.com/download/win
    echo Or run: install_git.bat
    pause
    exit /b 1
)

echo Git version:
"%GIT_PATH%" --version
echo.

REM Initialize git if needed
if not exist ".git" (
    echo Initializing git repository...
    "%GIT_PATH%" init
    echo.
)

REM Configure git user (change these if needed)
echo Configuring git user...
"%GIT_PATH%" config user.name "ngocsuo"
"%GIT_PATH%" config user.email "ngocsuo@users.noreply.github.com"
echo.

REM Add remote if not exists
"%GIT_PATH%" remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Adding remote origin...
    "%GIT_PATH%" remote add origin https://github.com/ngocsuo/mtview.git
) else (
    echo Updating remote origin...
    "%GIT_PATH%" remote set-url origin https://github.com/ngocsuo/mtview.git
)
echo.

REM Show current branch
echo Current branch:
"%GIT_PATH%" branch
echo.

REM Add all files
echo Adding all files...
"%GIT_PATH%" add .
echo.

REM Show status
echo Git status:
"%GIT_PATH%" status
echo.

REM Commit changes
echo Committing changes...
"%GIT_PATH%" commit -m "Add proxy import feature - support importing proxy list from txt file (socks5/http with optional auth)"
echo.

REM Push to GitHub
echo ========================================
echo Pushing to GitHub...
echo ========================================
echo.
echo You will be asked for GitHub credentials:
echo - Username: ngocsuo
echo - Password: Use Personal Access Token (not your password)
echo.
echo To create a token: https://github.com/settings/tokens
echo.
pause

"%GIT_PATH%" push -u origin master

echo.
echo ========================================
echo Push Complete!
echo ========================================
echo.
echo Check your repository at:
echo https://github.com/ngocsuo/mtview
echo.
pause

