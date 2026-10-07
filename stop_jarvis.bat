@echo off
title Stopping JARVIS
echo Terminating JARVIS background processes...
taskkill /f /im pythonw.exe 2>nul
taskkill /f /im python.exe /fi "WINDOWTITLE eq JARVIS*" 2>nul
echo JARVIS background service stopped.
timeout /t 2 >nul
exit
