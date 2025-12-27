@echo off
echo ===============================================
echo Starting CLARA Streamlit Dashboard
echo ===============================================
echo.

cd /d "%~dp0"

echo Using virtual environment Python...
.venv\Scripts\python.exe -m streamlit run src\ui\app.py

pause
