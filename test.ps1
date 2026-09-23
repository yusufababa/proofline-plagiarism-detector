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
& $pythonPath -c "import ast, pathlib; roots=('app','evaluation','tests'); files=[p for root in roots for p in pathlib.Path(root).rglob('*.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'Python syntax checked: {len(files)} files')"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'All automated checks passed.'
