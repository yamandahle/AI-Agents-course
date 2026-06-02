@echo off
title Push HW2 to GitHub
cd /d "%~dp0"

echo.
echo ========================================
echo   PUSH HW2 TO GITHUB
echo ========================================
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH.
    pause
    exit /b 1
)

echo [1/7] Current folder:
cd
echo.

echo [2/7] Switch to branch yamandahle-hw2...
git checkout yamandahle-hw2 2>nul
if errorlevel 1 (
    echo Creating branch yamandahle-hw2...
    git checkout -b yamandahle-hw2
)
echo.

echo [3/7] Stage files (except .env secrets)...
git add -A
git reset HEAD hw2/debate_agents/.env 2>nul
echo.

echo [4/7] What will be committed:
git status -sb
echo.
echo IMPORTANT: You should NOT see .env in the list above.
echo.
pause

echo [5/7] Commit...
git commit -m "HW2: debate system, docs, and README structure"
if errorlevel 1 (
    echo Note: Maybe nothing new to commit - continuing to push...
)
echo.

echo [6/7] Push to GitHub...
git push -u origin yamandahle-hw2
if errorlevel 1 (
    echo.
    echo PUSH FAILED. Common fixes:
    echo   - Run: gh auth login   OR   git login
    echo   - Check internet
    echo   - Ask partner to add you to the repo
    pause
    exit /b 1
)
echo.

echo [7/7] Pull request...
gh --version >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI ^(gh^) not found. Push OK - create PR in browser:
    echo https://github.com/yamandahle/AI-Agents-course/compare/main...yamandahle-hw2
    pause
    exit /b 0
)

gh pr list --head yamandahle-hw2 --json url -q ".[0].url" 2>nul | findstr http >nul
if errorlevel 1 (
    echo Creating new PR...
    gh pr create --base main --head yamandahle-hw2 --title "HW2: AI Debate System" --body "See hw2/README.md for summary and test plan."
) else (
    echo PR already exists.
    gh pr view yamandahle-hw2 --web 2>nul
)

echo.
echo Merge into main? Press Y to merge, N to merge later on GitHub.
choice /C YN /M "Merge PR now"
if errorlevel 2 goto done
if errorlevel 1 (
    gh pr merge --merge
)

:done
echo.
echo ========================================
echo   DONE
echo   Repo: https://github.com/yamandahle/AI-Agents-course
echo   Branch: yamandahle-hw2
echo ========================================
pause
