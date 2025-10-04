@echo off
echo Запуск СБП Payment Server...
cd /d "%~dp0"
python payment_server.py
pause
