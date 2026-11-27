@echo off
rem Team 2 - pfad.py unter Windows starten. Beim ersten Mal wird ein portables Python 3.12
rem nach Dokumente\DPE-Werkzeuge\python geladen (nichts wird installiert, wie bei cib_starten.cmd).
rem Verantwortlich: Amar
rem Aufruf im cmd-Fenster in diesem Ordner:  pfad start   (in PowerShell:  .\pfad start)
setlocal
for /f "usebackq delims=" %%d in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('MyDocuments')"`) do set "DOKU=%%d"
set "PY=%DOKU%\DPE-Werkzeuge\python"
if not exist "%PY%\python.exe" (
  echo Lade portables Python 3.12 nach %PY% - nur beim ersten Mal ...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; New-Item -ItemType Directory -Force '%PY%' | Out-Null; Invoke-WebRequest -UseBasicParsing 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip' -OutFile '%PY%\py.zip'; Expand-Archive '%PY%\py.zip' '%PY%' -Force; Remove-Item '%PY%\py.zip'"
  if not exist "%PY%\python.exe" (
    echo FEHLER: Python konnte nicht geladen werden. Internet da? Ordner %PY% loeschen und nochmal versuchen.
    exit /b 1
  )
)
"%PY%\python.exe" "%~dp0pfad.py" %*
