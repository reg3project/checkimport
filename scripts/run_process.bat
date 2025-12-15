@echo off
REM Process IDML files and generate XLSX output

echo ========================================
echo REG3 Import-Check - Process IDML Files
echo ========================================
echo.

cd /d "%~dp0\.."

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Using virtual environment
)

REM Run processing
python -m src.main process --individual --combined

echo.
echo Processing complete!
echo.
echo Output files in: output\xlsx\
echo.
echo Next steps:
echo   1. Download generated XLSX files
echo   2. Review and validate data
echo   3. Run 'run_check.bat' to compare with references

pause
