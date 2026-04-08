@echo off
setlocal
echo ===================================================
echo   🛡️ AI Reliability & Risk Auditing System
echo ===================================================
echo.

echo [*] Step 1: Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [!] Failed to install dependencies. Please ensure Python and pip are in your PATH.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [*] Step 2: Running Automated Batch Test...
echo.
python batch_eval.py
if %ERRORLEVEL% neq 0 (
    echo [!] Batch test failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [*] Step 3: Starting Interactive UI (Streamlit)...
echo.
echo Launching dashboard in your browser...
python -m streamlit run app.py

pause
