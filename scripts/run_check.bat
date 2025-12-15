@echo off
REM Run validation check and generate reports

echo ========================================
echo REG3 Import-Check - Validation Check
echo ========================================
echo.

cd /d "%~dp0\.."

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Using virtual environment
)

REM Run check
python -m src.main check --report

echo.
echo Validation complete!
echo.
echo Reports generated in: output\reports\

pause
