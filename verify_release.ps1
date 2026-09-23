$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$pythonPath = if (Test-Path -LiteralPath '.venv\Scripts\python.exe') {
    '.\.venv\Scripts\python.exe'
} else {
    $command = Get-Command py -ErrorAction SilentlyContinue
    if (-not $command) { throw 'Python is required to verify the release.' }
    $command.Source
}

Write-Output '[1/6] Running the automated test suite...'
& '.\test.ps1'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output '[2/6] Checking browser JavaScript syntax...'
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    & $node.Source --check 'app\web\static\app.js'
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Warning 'Node.js is unavailable; JavaScript syntax check was skipped.'
}

Write-Output '[3/6] Checking version consistency...'
$packageVersion = (& $pythonPath -c 'import app; print(app.__version__)').Trim()
$settingsVersion = (& $pythonPath -c 'from app.core.config import Settings; print(Settings.from_environment().app_version)').Trim()
$pyprojectText = Get-Content -LiteralPath 'pyproject.toml' -Raw
$pyprojectVersion = [regex]::Match($pyprojectText, 'version\s*=\s*"([^"]+)"').Groups[1].Value
if (-not $packageVersion -or $packageVersion -ne $settingsVersion -or $packageVersion -ne $pyprojectVersion) {
    throw "Version mismatch: package=$packageVersion settings=$settingsVersion pyproject=$pyprojectVersion"
}
Write-Output "Version $packageVersion is consistent."

Write-Output '[4/6] Validating release metadata...'
$tracker = Get-Content -LiteralPath 'project_tracker.json' -Raw | ConvertFrom-Json
if ($tracker.overall_percent -ne 97) { throw 'project_tracker.json must report 97 percent for this release candidate.' }
if (-not $tracker.objectives -or $tracker.objectives.Count -ne 3) { throw 'Project objective metadata is incomplete.' }

Write-Output '[5/6] Validating the lecturer Word report...'
$reportPath = Join-Path $projectRoot 'lecturer_demo\Proofline Final Project Technical Report.docx'
if (-not (Test-Path -LiteralPath $reportPath)) { throw "Missing report: $reportPath" }
$env:PROOFLINE_REPORT_PATH = $reportPath
& $pythonPath -c "import os, zipfile; p=os.environ['PROOFLINE_REPORT_PATH']; z=zipfile.ZipFile(p); assert 'word/document.xml' in z.namelist(); assert 'word/styles.xml' in z.namelist(); print('Report package valid: {:,} bytes'.format(os.path.getsize(p)))"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output '[6/6] Checking an optional live server...'
try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 3
    if ($health.version -ne $packageVersion) {
        throw "The running server reports version $($health.version), expected $packageVersion. Restart it with .\run.ps1."
    }
    Write-Output "Live health check passed for version $($health.version)."
}
catch [System.Net.WebException] {
    Write-Output 'No local server is running; live health check skipped.'
}

$hash = (Get-FileHash -LiteralPath $reportPath -Algorithm SHA256).Hash
Write-Output "Release candidate verified. Report SHA-256: $hash"
