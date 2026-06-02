# Push HW2 to GitHub and open/merge PR into main
# Run from repo root:  powershell -ExecutionPolicy Bypass -File scripts\push_hw2_to_github.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== AI-Agents-course: push HW2 ===" -ForegroundColor Cyan

# Safety: never commit secrets
if (Test-Path "hw2\debate_agents\.env") {
    git check-ignore -q "hw2/debate_agents/.env"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: hw2/debate_agents/.env is not gitignored. Fix .gitignore before pushing." -ForegroundColor Red
        exit 1
    }
}

$branch = "yamandahle-hw2"
git fetch origin
git checkout $branch 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout -b $branch
}

git add -A
git reset HEAD hw2/debate_agents/.env 2>$null
git reset HEAD "**/.env" 2>$null

$status = git status --porcelain
if (-not $status) {
    Write-Host "Nothing to commit." -ForegroundColor Yellow
} else {
    git commit -m @"
HW2: AI debate system — stages 1-3, docs, and clear READMEs

- Python debate agents (PRO, CON, Father) with SDK, Gatekeeper, tests
- README structure with evidence links (transcripts, sample run, test report)
- Terminal output improvements and auto-save sample_debate.txt
"@
}

git push -u origin $branch

Write-Host "`n=== Pull request ===" -ForegroundColor Cyan
$pr = gh pr list --head $branch --json number,url --jq ".[0]" 2>$null
if ($pr) {
    $url = ($pr | ConvertFrom-Json).url
    Write-Host "Existing PR: $url"
} else {
    gh pr create --base main --head $branch --title "HW2: AI Debate System" --body @"
## Summary
- Three-agent debate on remote work vs office work (PRO, CON, Father)
- Stage 1 manual transcript, Stage 2 Claude CLI commands, Stage 3 Python app
- 161 tests, ~86% coverage; evidence in results/ and stage1/

## Test plan
- [ ] ``cd hw2/debate_agents && uv sync && uv run pytest tests/``
- [ ] ``uv run ruff check .``
- [ ] Read ``hw2/debate_agents/results/sample_debate.txt``
"@
}

Write-Host "`nTo merge when checks pass:" -ForegroundColor Green
Write-Host "  gh pr merge --merge"
Write-Host "Or merge on GitHub: https://github.com/yamandahle/AI-Agents-course/pulls"
