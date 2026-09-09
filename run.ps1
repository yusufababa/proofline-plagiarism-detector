$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    throw 'The project is not set up. Run .\setup.ps1 first.'
}

if (Test-Path -LiteralPath '.env') {
    foreach ($line in Get-Content -LiteralPath '.env') {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
        $parts = $trimmed.Split('=', 2)
        if ($parts.Count -eq 2) {
            [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
        }
    }
}

& '.\.venv\Scripts\python.exe' -c 'import fastapi, uvicorn' 2>$null
if ($LASTEXITCODE -ne 0) {
    throw 'Required packages are missing. Run .\setup.ps1 first.'
}

$appHost = if ($env:APP_HOST) { $env:APP_HOST } else { '127.0.0.1' }
$appPort = if ($env:APP_PORT) { $env:APP_PORT } else { '8000' }
Write-Output "Starting at http://${appHost}:${appPort}"
& '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --host $appHost --port $appPort
