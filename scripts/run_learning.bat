@echo off
REM Run learning cycle - learn from reference IDML/XLSX pairs

echo ========================================
echo REG3 Import-Check - Learning Cycle
echo ========================================
echo.

cd /d "%~dp0\.."

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Using virtual environment
)

REM Run learning
python -m src.main learn --report

echo.
echo Learning complete!
echo.
echo Next steps:
echo   1. Review reports in output\reports\
echo   2. Add more learning pairs if accuracy is low
echo   3. Run 'run_process.bat' to process new IDML files

pause
