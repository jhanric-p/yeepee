@echo off
cd /d "%~dp0"

REM Check if Kivy is installed, if not install it
python -c "import kivy" 2>nul
if errorlevel 1 (
    echo Kivy not found, installing...
    python -m pip install --upgrade pip
    python -m pip install kivy[base] kivy_examples
)

REM Initialize the database using sqlite3 command line tool
REM Note: PowerShell does not support '<' redirection, so use this command in cmd.exe or Git Bash
sqlite3.exe ..\database.db < kivy_database_schema.sql

python main.py
