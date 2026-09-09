$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$pythonPath = if (Test-Path -LiteralPath '.venv\Scripts\python.exe') {
    '.\.venv\Scripts\python.exe'
} else {
    $command = Get-Command py -ErrorAction SilentlyContinue
    if (-not $command) { throw 'Python is required to run the tests.' }
    $command.Source
}

& $pythonPath -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $pythonPath -m compileall -q app tests
Write-Output 'All automated checks passed.'

