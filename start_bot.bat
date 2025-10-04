@echo off
chcp 65001 >nul
title Calorie Counter Bot
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║         TELEGRAM-БОТ ДЛЯ ПОДСЧЁТА КАЛОРИЙ - ЗАПУСК                  ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

REM Проверка существования виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo ❌ ОШИБКА: Виртуальное окружение не найдено!
    echo.
    echo Создайте виртуальное окружение командой:
    echo    python -m venv venv
    echo.
    echo Затем установите зависимости:
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Проверка существования файла .env
if not exist ".env" (
    echo ⚠️  ПРЕДУПРЕЖДЕНИЕ: Файл .env не найден!
    echo.
    echo Создайте файл .env с токенами:
    echo    TELEGRAM_BOT_TOKEN=ваш_токен
    echo    OPENAI_API_KEY=ваш_ключ
    echo.
    echo Или запустите: python create_env.py
    echo.
    pause
    exit /b 1
)

echo ✅ Проверка завершена
echo.
echo 🚀 Запуск бота...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Активация виртуального окружения и запуск бота
call venv\Scripts\activate.bat
python bot.py

REM Если бот упал с ошибкой, окно останется открытым
if errorlevel 1 (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo ❌ Бот завершился с ошибкой!
    echo.
    echo 📝 Проверьте логи в файле: bot.log
    echo 🔧 Запустите проверку: python check_setup.py
    echo.
    pause
)
