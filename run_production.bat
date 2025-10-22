@echo off
title Employee Data System - Production Mode
color 0B

echo ========================================
echo    PRODUCTION MODE - Samsung EDS
echo ========================================
echo.

echo [1/4] Installing required packages...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Failed to install packages
    pause
    exit /b 1
)
echo ✓ Packages installed successfully

echo.
echo [2/4] Verifying production database...
python production_setup.py verify >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Database verification failed, initializing...
    python production_setup.py >nul 2>&1
) else (
    echo ✓ Production database verified
)

echo.
echo [3/4] Creating backup...
python production_setup.py backup >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Backup creation failed, but continuing...
) else (
    echo ✓ Backup created successfully
)

echo.
echo [4/4] Starting Production Server...
echo.
echo ========================================
echo    PRODUCTION CREDENTIALS
echo ========================================
echo Admin User:
echo   Name: Admin
echo   Code: ADMIN  
echo   Pass: admin123
echo.
echo ⚠️  IMPORTANT: Change admin password after first login!
echo ========================================
echo.
echo 🌐 Server URL: http://127.0.0.1:5000
echo 📊 Database: Persistent (data preserved)
echo 💾 Backups: production_backups/
echo 🔒 Security: Production mode enabled
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py