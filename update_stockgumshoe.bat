@echo off
setlocal

:: Define your Miniconda environment's python path
set "PYTHON_PATH=C:\Users\Philip\Miniconda3\envs\Main_3_12_10\python.exe"

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Generate a reliable timestamp using PowerShell for the log file
for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"') do set "TIMESTAMP=%%i"
set "LOGFILE=logs\run_%TIMESTAMP%.log"

echo ======================================================== >> "%LOGFILE%"
echo Stock Gumshoe Auto-Update Started: %date% %time% >> "%LOGFILE%"
echo ======================================================== >> "%LOGFILE%"

:: Step 1: Run the Python scraping script using Miniconda Python
"%PYTHON_PATH%" scrape_stockgumshoe.py >> "%LOGFILE%" 2>&1

:: Check if Python succeeded before committing to Git
if %errorlevel% equ 0 (
    echo. >> "%LOGFILE%"
    echo [SUCCESS] Python script completed successfully at %date% %time% >> "%LOGFILE%"
    
    :: Step 2: Automatically Git Stage, Commit, and Push the updated txt file
    echo [GIT] Staging and pushing updated data to GitHub... >> "%LOGFILE%"
    
    git add stock_gumshoe_2026_11_06.txt >> "%LOGFILE%" 2>&1
    git commit -m "Auto-update Stock Gumshoe scrape data [%date%]" >> "%LOGFILE%" 2>&1
    git push origin main >> "%LOGFILE%" 2>&1
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] Git push completed successfully! Netlify will update shortly. >> "%LOGFILE%"
        echo [SUCCESS] Pipeline complete: Scraped & Synced to Git!
    ) else (
        echo [WARNING] Python scraped successfully, but Git push encountered an issue. Check log. >> "%LOGFILE%"
        echo [WARNING] Scraped successfully, but Git push failed. Check logs.
    )

) else (
    echo. >> "%LOGFILE%"
    echo [ERROR] Python script failed with exit code %errorlevel% at %date% %time% >> "%LOGFILE%"
    echo [ERROR] Python script failed. Git push skipped. Check %LOGFILE% for details.
)

echo ======================================================== >> "%LOGFILE%"
timeout /t 5