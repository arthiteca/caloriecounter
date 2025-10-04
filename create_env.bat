@echo off
chcp 65001 >nul
title Создание .env файла
color 0D

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              ИНТЕРАКТИВНОЕ СОЗДАНИЕ .ENV ФАЙЛА                       ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

REM Проверка существования виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo ❌ ОШИБКА: Виртуальное окружение не найдено!
    echo.
    echo Сначала создайте виртуальное окружение:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo 🔧 Запуск мастера настройки...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Активация виртуального окружения и запуск мастера
call venv\Scripts\activate.bat
python create_env.py

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
