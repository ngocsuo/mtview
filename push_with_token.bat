@echo off
echo ========================================
echo Push to GitHub: ngocsuo/mtview
echo ========================================
echo.

REM Set Git path
set "GIT_PATH=C:\Program Files\Git\bin\git.exe"
if not exist "%GIT_PATH%" set "GIT_PATH=git.exe"

REM Check git
"%GIT_PATH%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found! Please install Git first.
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
    "%GIT_PATH%" config user.name "ngocsuo"
    "%GIT_PATH%" config user.email "ngocsuo@users.noreply.github.com"
    echo.
)

REM Add remote
"%GIT_PATH%" remote get-url origin >nul 2>&1
if errorlevel 1 (
    "%GIT_PATH%" remote add origin https://github.com/ngocsuo/mtview.git
) else (
    "%GIT_PATH%" remote set-url origin https://github.com/ngocsuo/mtview.git
)

REM Add and commit
echo Adding files...
"%GIT_PATH%" add .
echo.

echo Committing...
"%GIT_PATH%" commit -m "Add proxy import feature - support importing proxy list from txt file (socks5/http with optional auth)"
echo.

REM Ask for token securely
echo ========================================
echo IMPORTANT: You need a GitHub Personal Access Token
echo ========================================
echo.
echo If you don't have one, create it at:
echo https://github.com/settings/tokens/new
echo.
echo Required permissions: repo (all)
echo.
set /p TOKEN="Enter your GitHub Personal Access Token: "
echo.

REM Push using token
echo Pushing to GitHub...
"%GIT_PATH%" push https://ngocsuo:%TOKEN%@github.com/ngocsuo/mtview.git master

if errorlevel 1 (
    echo.
    echo ========================================
    echo Push FAILED!
    echo ========================================
    echo.
    echo Possible reasons:
    echo - Invalid token
    echo - Token doesn't have 'repo' permission
    echo - Network issue
    echo.
) else (
    echo.
    echo ========================================
    echo Push SUCCESS!
    echo ========================================
    echo.
    echo Check your repository at:
    echo https://github.com/ngocsuo/mtview
    echo.
)

REM Clear token from memory
set TOKEN=

pause

