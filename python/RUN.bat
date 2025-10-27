@echo off
echo ================================================
echo    RUMBLE ULTIMATE BOT BYPASS - QUICK RUN
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "..\\.venv\\Scripts\\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r python\requirements.txt
    pause
    exit /b 1
)

echo [INFO] Using virtual environment
echo.

REM Menu
echo Select an option:
echo   1. Run ULTIMATE version (with full bypass)
echo   2. Run ORIGINAL version (no bypass)
echo   3. Test stealth capabilities
echo   4. Quick run (1 attempt)
echo   5. Quick run with 3 attempts
echo   6. Quick run with 5 attempts (headless)
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running ULTIMATE version...
    echo.
    "..\\.venv\\Scripts\\python.exe" main_ultimate.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running ORIGINAL version...
    echo.
    "..\\.venv\\Scripts\\python.exe" main.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Testing stealth capabilities...
    echo.
    "..\\.venv\\Scripts\\python.exe" test_stealth.py
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Quick run (1 attempt)...
    echo.
    "..\\.venv\\Scripts\\python.exe" run_quick.py --count 1
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Quick run (3 attempts)...
    echo.
    "..\\.venv\\Scripts\\python.exe" run_quick.py --count 3
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Quick run (5 attempts, headless)...
    echo.
    "..\\.venv\\Scripts\\python.exe" run_quick.py --count 5 --headless
    goto end
)

echo.
echo [ERROR] Invalid choice!
pause
exit /b 1

:end
echo.
echo ================================================
echo            Process completed
echo ================================================
pause
