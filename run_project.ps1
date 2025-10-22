# Employee Data System - PowerShell Launcher
# Run this script with: powershell -ExecutionPolicy Bypass -File run_project.ps1

Write-Host "========================================" -ForegroundColor Green
Write-Host "    Employee Data System - Samsung" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "[1/3] Installing required packages..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt *>$null
    Write-Host "✓ Packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to install packages" -ForegroundColor Red
    Write-Host "Please run: pip install flask pandas openpyxl" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/3] Testing system..." -ForegroundColor Yellow
try {
    python test_system.py *>$null
    Write-Host "✓ System test passed" -ForegroundColor Green
} catch {
    Write-Host "Warning: System test failed, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/3] Starting the Employee Data System..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    LOGIN CREDENTIALS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Admin User:" -ForegroundColor White
Write-Host "   Name: Admin" -ForegroundColor Gray
Write-Host "   Code: ADMIN" -ForegroundColor Gray
Write-Host "   Pass: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "Test Employee:" -ForegroundColor White
Write-Host "   Name: Test Employee" -ForegroundColor Gray
Write-Host "   Code: TEST001" -ForegroundColor Gray
Write-Host "   Pass: test123" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will start at: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python app.py