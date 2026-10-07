@echo off
title Starting JARVIS Background Service
cd /d "%~dp0"
start "" pythonw jarvis_background_service.pyw
echo JARVIS is now running silently in the background!
echo Say "Hey Jarvis" at any time to wake him up on your desktop.
timeout /t 3 >nul
exit
