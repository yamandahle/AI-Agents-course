# Run 3 fast experiments for EX06 submission.
# Requires: ollama serve running, uv sync done, credentials.json for Exp 1 Gmail.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

New-Item -ItemType Directory -Force -Path results | Out-Null

Write-Host "`n=== Exp 2: small grid, blind cop (0,2) ===" -ForegroundColor Cyan
uv run python src/main.py --config experiments/exp2_small_blind_cop.json --headless `
    2>&1 | Tee-Object -FilePath results/exp2_small_blind_cop.log

Write-Host "`n=== Exp 3: small grid, full vision (2,2) ===" -ForegroundColor Cyan
uv run python src/main.py --config experiments/exp3_small_full_vision.json --headless `
    2>&1 | Tee-Object -FilePath results/exp3_small_full_vision.log

Write-Host "`n=== Exp 1: full 5x5 official run + Gmail ===" -ForegroundColor Cyan
Write-Host "Add --gui if you want the live board window." -ForegroundColor Yellow
uv run python src/main.py --config experiments/exp1_full_5x5.json --headless `
    2>&1 | Tee-Object -FilePath results/exp1_full_5x5.log

Write-Host "`nDone. Check results/*/result.json and fill README experiment table." -ForegroundColor Green
