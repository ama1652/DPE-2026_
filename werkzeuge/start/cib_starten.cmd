@echo off
rem Team 2 - startet cib_seven_durchlauf.ps1 ohne PowerShell-Sperre
rem Verantwortlich: Saifudin Mohammadi
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "cib_seven_durchlauf.ps1"
echo.
pause
