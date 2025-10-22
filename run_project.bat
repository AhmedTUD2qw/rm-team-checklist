@echo off
title Employee Data System
color 0A

echo ========================================
echo    Employee Data System - Samsung
echo ========================================
echo.

echo [1/3] Installing required packages...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Failed to install packages
    echo Please run: pip install flask pandas openpyxl
    pause
    exit /b 1
)
echo ✓ Packages installed successfully

echo.
echo [2/3] Testing system...
python test_system.py >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: System test failed, but continuing...
) else (
    echo ✓ System test passed
)

echo Testing POP materials...
python test_pop_materials.py >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: POP materials test failed, but continuing...
) else (
    echo ✓ POP materials test passed
)

echo Updating database schema...
python update_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Database update failed, but continuing...
) else (
    echo ✓ Database schema updated
)

echo Updating POP materials for model support...
python update_pop_materials_by_model.py >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: POP materials update failed, but continuing...
) else (
    echo ✓ POP materials updated for model support
)

echo Setting up production environment...
python production_setup.py verify >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Production setup verification failed, but continuing...
) else (
    echo ✓ Production environment verified
)

echo.
echo [3/3] Starting the Employee Data System...
echo.
echo ========================================
echo    LOGIN CREDENTIALS
echo ========================================
echo Admin User:
echo   Name: Admin
echo   Code: ADMIN  
echo   Pass: admin123
echo.
echo Test Employee:
echo   Name: Test Employee
echo   Code: TEST001
echo   Pass: test123
echo ========================================
echo.
echo Server will start at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python app.py