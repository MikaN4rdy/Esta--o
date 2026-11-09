@echo off
cd /d "%~dp0"
start "Sync ranking" /min python sync_estacao.py 4
python main.py
pause