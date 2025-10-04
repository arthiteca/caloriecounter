@echo off
echo Проверка сетевых настроек для СБП...
cd /d "%~dp0"
python check_network.py
pause
