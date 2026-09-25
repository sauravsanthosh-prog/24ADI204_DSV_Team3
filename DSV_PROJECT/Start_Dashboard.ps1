$projectFolder = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectFolder '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host 'First create .venv and install requirements.txt as explained in README.md.'
    exit 1
}
Set-Location -LiteralPath $projectFolder
& $pythonPath -m streamlit run Source_Code/dashboard.py
