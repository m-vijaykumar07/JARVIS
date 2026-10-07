@echo off
title JARVIS Voice Assistant
color 0b
echo ========================================================
echo       INITIALIZING J.A.R.V.I.S. VOICE ASSISTANT
echo ========================================================
echo.
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] JARVIS encountered an issue. Press any key to view details...
    pause
)
