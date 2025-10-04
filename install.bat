@echo off
chcp 65001 >nul
title Установка Calorie Counter Bot
color 0C

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              УСТАНОВКА CALORIE COUNTER BOT                           ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

echo 📦 Начинаем установку...
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не установлен!
    echo.
    echo Установите Python 3.9+ с https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
python --version
echo.

REM Создание виртуального окружения
echo 📂 Создание виртуального окружения...
if exist "venv" (
    echo ⚠️  Папка venv уже существует. Пропускаем создание.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка при создании виртуального окружения!
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
)
echo.

REM Активация и установка зависимостей
echo 📥 Установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Ошибка при установке зависимостей!
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo.
echo 📝 Следующие шаги:
echo.
echo 1. Создайте .env файл:
echo    - Запустите: create_env.bat
echo    - Или создайте вручную с токенами
echo.
echo 2. Сгенерируйте ключи доступа:
echo    - Запустите: generate_keys.bat
echo.
echo 3. Проверьте настройку:
echo    - Запустите: check_setup.bat
echo.
echo 4. Запустите бота:
echo    - Запустите: start_bot.bat
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
