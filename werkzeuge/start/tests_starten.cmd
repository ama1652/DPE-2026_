@echo off
rem Team 2 - startet tests_lokal.ps1 ohne PowerShell-Sperre
rem Verantwortlich: Saifudin Mohammadi
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "tests_lokal.ps1"
echo.
pause
