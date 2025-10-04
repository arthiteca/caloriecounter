@echo off
chcp 65001 >nul
title Генерация статичных ключей доступа
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║         ГЕНЕРАТОР СТАТИЧНЫХ КЛЮЧЕЙ ДОСТУПА - AI LAB                 ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

REM Проверка существования виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo ❌ ОШИБКА: Виртуальное окружение не найдено!
    echo.
    pause
    exit /b 1
)

echo 🔑 Запуск генератора статичных ключей...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Активация виртуального окружения и запуск генератора
call venv\Scripts\activate.bat
python generate_static_keys.py

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ Готово!
echo.
echo 📁 Файлы:
echo    • КЛЮЧИ_ДОСТУПА.txt - список всех ключей
echo    • calorie_counter.db - база данных
echo.
echo 📞 Контакты: @unrealartur
echo 💡 Made by AI LAB
echo.
pause
