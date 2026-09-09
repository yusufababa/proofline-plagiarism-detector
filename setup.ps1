$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
    throw 'Python 3.11 or newer is required. Install Python, then run this script again.'
}

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & $pythonCommand.Source -m venv .venv
}

& '.\.venv\Scripts\python.exe' -m pip install --disable-pip-version-check --progress-bar off --timeout 60 --retries 2 -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw 'Package installation failed. Check the internet connection and run .\setup.ps1 again.'
}

if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}

Write-Output 'Setup complete. Run .\run.ps1 to start the application.'
