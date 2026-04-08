@echo off
setlocal

REM === Quellen / Ziele anpassen ===
set DOCSRC=D:\offline_Doku
set REPO1=D:\GitHub Repositorys\HA-Repo\HA_YAconfigML
set REPO2=D:\GitHub Repositorys\HA-Repo\Themis_Ultra
set DOCTARGET=offline_Doku\docs

REM === 1) Offline-Doku aktualisieren ===
cd /d "%DOCSRC%"
wget.exe --mirror --convert-links --adjust-extension --page-requisites --no-parent https://www.home-assistant.io/docs/

REM === Funktion: Doku in ein Repo spiegeln + commit + push ===
call :UpdateRepo "%REPO1%"
call :UpdateRepo "%REPO2%"

echo.
echo Fertig.
pause
exit /b 0


:UpdateRepo
set REPODIR=%~1
echo.
echo ================================
echo Update Repo: "%REPODIR%"
echo ================================

cd /d "%REPODIR%" || (echo FEHLER: Repo-Pfad nicht gefunden & exit /b 1)

REM Branch auf main (falls du andere Branches nutzt, hier anpassen)
git checkout main
git pull origin main

REM Zielordner sicherstellen
if not exist "%DOCTARGET%" mkdir "%DOCTARGET%"

REM Doku spiegeln (exakt, inkl. Loeschungen)
robocopy "%DOCSRC%" "%REPODIR%\%DOCTARGET%" /MIR /R:2 /W:2

REM Nur committen, wenn es Aenderungen gibt
git add "%DOCTARGET%"

git diff --cached --quiet
if %errorlevel%==0 (
  echo Keine Aenderungen -> kein Commit/Push.
  exit /b 0
)

git commit -m "Update Home Assistant offline docs"
git push origin main

exit /b 0
