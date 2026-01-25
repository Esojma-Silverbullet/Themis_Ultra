@echo off
cd /d D:\offline_Doku
wget.exe --mirror --convert-links --adjust-extension --page-requisites --no-parent https://www.home-assistant.io/docs/
pause