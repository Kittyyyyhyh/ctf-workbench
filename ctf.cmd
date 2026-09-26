@echo off
rem ctf-workbench CLI wrapper for cmd.exe / PowerShell.
setlocal
set "PY=python"
where %PY% >nul 2>nul || set "PY=py"
"%PY%" "%~dp0ctfcli\cli.py" %*
exit /b %ERRORLEVEL%
