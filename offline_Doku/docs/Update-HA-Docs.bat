@echo off
setlocal

set DOCSRC=D:\offline_Doku
set REPO1=D:\GitHub Repositorys\HA-Repo\HA_YAconfigML
set REPO2=D:\GitHub Repositorys\HA-Repo\Themis_Ultra
set DOCTARGET=offline_Doku\docs

set BRANCH_REPO1=Beta-2
set BRANCH_REPO2=main

cd /d "%DOCSRC%"
wget.exe --mirror --convert-links --adjust-extension --page-requisites --no-parent https://www.home-assistant.io/docs/

call :UpdateRepo "%REPO1%" "%BRANCH_REPO1%"
call :UpdateRepo "%REPO2%" "%BRANCH_REPO2%"

echo.
echo Fertig.
pause
exit /b 0


:UpdateRepo
set REPODIR=%~1
set BRANCH=%~2

echo.
echo ================================
echo Update Repo: "%REPODIR%"  Branch: "%BRANCH%"
echo ================================

cd /d "%REPODIR%" || (echo FEHLER: Repo-Pfad nicht gefunden & exit /b 1)

git checkout "%BRANCH%"
git pull --rebase origin "%BRANCH%"
if errorlevel 1 exit /b 1

if not exist "%DOCTARGET%" mkdir "%DOCTARGET%"

robocopy "%DOCSRC%" "%REPODIR%\%DOCTARGET%" /MIR /R:2 /W:2

git add "%DOCTARGET%"

git diff --cached --quiet
if %errorlevel%==0 (
  echo Keine Aenderungen -> kein Commit/Push.
  exit /b 0
)

git commit -m "Update Home Assistant offline docs"
git push origin "%BRANCH%"
if errorlevel 1 exit /b 1

exit /b 0
