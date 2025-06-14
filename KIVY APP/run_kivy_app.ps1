# PowerShell script to run the Kivy app with environment setup

# Check if Kivy is installed, if not install it
try {
    python -c "import kivy" 2>$null
} catch {
    Write-Host "Kivy not found, installing..."
    python -m pip install --upgrade pip
    python -m pip install kivy[base] kivy_examples
}

# Note: PowerShell does not support '<' redirection operator for sqlite3
# Please run the following command manually in cmd.exe or Git Bash to initialize the database:
# sqlite3.exe ..\database.db < ..\kivy_database_schema.sql

# Run the Kivy app
python main.py
