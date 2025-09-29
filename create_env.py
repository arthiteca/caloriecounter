#!/usr/bin/env python3
"""
Интерактивный скрипт для создания .env файла
"""
import os
import sys


def print_header():
    """Вывод заголовка"""
    print("=" * 60)
    print("🔧 Настройка Calorie Counter Bot")
    print("=" * 60)
    print()


def print_section(title):
    """Вывод заголовка секции"""
    print("\n" + "-" * 60)
    print(f"📋 {title}")
    print("-" * 60)


def get_telegram_token():
    """Получение токена Telegram"""
    print_section("Telegram Bot Token")
    print("\nДля получения токена:")
    print("1. Откройте @BotFather в Telegram")
    print("2. Отправьте команду /newbot")
    print("3. Следуйте инструкциям")
    print("4. Скопируйте токен\n")
    
    while True:
        token = input("Введите Telegram Bot Token: ").strip()
        if not token:
            print("❌ Токен не может быть пустым!")
            continue
        if len(token) < 40:
            print("⚠️  Токен кажется слишком коротким. Вы уверены?")
            confirm = input("Продолжить? (y/n): ").lower()
            if confirm != 'y':
                continue
        print(f"✅ Токен принят: {token[:10]}...{token[-5:]}")
        return token


def get_openai_key():
    """Получение ключа OpenAI"""
    print_section("OpenAI API Key")
    print("\nДля получения ключа:")
    print("1. Зайдите на https://platform.openai.com")
    print("2. Перейдите в раздел API Keys")
    print("3. Нажмите 'Create new secret key'")
    print("4. Скопируйте ключ (показывается только один раз!)\n")
    print("⚠️  ВАЖНО: Убедитесь, что:")
    print("   - У вас есть доступ к GPT-4")
    print("   - На аккаунте есть баланс")
    print("   - Ключ начинается с 'sk-'\n")
    
    while True:
        key = input("Введите OpenAI API Key: ").strip()
        if not key:
            print("❌ Ключ не может быть пустым!")
            continue
        if not key.startswith('sk-'):
            print("⚠️  Ключ OpenAI обычно начинается с 'sk-'")
            confirm = input("Продолжить? (y/n): ").lower()
            if confirm != 'y':
                continue
        print(f"✅ Ключ принят: {key[:10]}...{key[-5:]}")
        return key


def create_env_file(telegram_token, openai_key):
    """Создание .env файла"""
    print_section("Создание .env файла")
    
    # Проверка существования файла
    if os.path.exists('.env'):
        print("\n⚠️  Файл .env уже существует!")
        print("Текущее содержимое будет перезаписано.")
        confirm = input("Продолжить? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Операция отменена")
            return False
        # Создаём резервную копию
        import shutil
        shutil.copy('.env', '.env.backup')
        print("✅ Создана резервная копия: .env.backup")
    
    # Создание файла
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={telegram_token}

# OpenAI API Configuration
OPENAI_API_KEY={openai_key}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("\n✅ Файл .env успешно создан!")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка при создании файла: {e}")
        return False


def verify_setup():
    """Проверка настройки"""
    print_section("Проверка настройки")
    print("\n🔍 Запуск проверки конфигурации...\n")
    
    try:
        # Импортируем и запускаем check_setup
        if os.path.exists('check_setup.py'):
            import subprocess
            result = subprocess.run([sys.executable, 'check_setup.py'], 
                                  capture_output=False)
            return result.returncode == 0
        else:
            print("⚠️  Файл check_setup.py не найден")
            print("   Пропуск автоматической проверки")
            return True
    except Exception as e:
        print(f"⚠️  Ошибка при проверке: {e}")
        return True


def print_next_steps():
    """Вывод следующих шагов"""
    print("\n" + "=" * 60)
    print("🎉 Настройка завершена!")
    print("=" * 60)
    print("\n📝 Следующие шаги:\n")
    print("1. Убедитесь, что все зависимости установлены:")
    print("   pip install -r requirements.txt\n")
    print("2. Запустите бота:")
    print("   python bot.py\n")
    print("3. Найдите вашего бота в Telegram и отправьте /start\n")
    print("📚 Документация:")
    print("   - ИНСТРУКЦИЯ.md - Краткое руководство на русском")
    print("   - README.md - Полная документация")
    print("   - QUICKSTART.md - Быстрый старт")
    print("   - TROUBLESHOOTING.md - Решение проблем\n")
    print("💡 Совет: Запустите python check_setup.py для проверки\n")
    print("=" * 60)


def main():
    """Основная функция"""
    try:
        print_header()
        
        print("Этот скрипт поможет вам настроить бота за несколько минут.\n")
        print("Вам понадобятся:")
        print("  ✓ Telegram Bot Token (от @BotFather)")
        print("  ✓ OpenAI API Key (от platform.openai.com)\n")
        
        input("Нажмите Enter для начала настройки...")
        
        # Получение токенов
        telegram_token = get_telegram_token()
        openai_key = get_openai_key()
        
        # Создание .env файла
        if not create_env_file(telegram_token, openai_key):
            print("\n❌ Не удалось создать .env файл")
            return 1
        
        # Проверка настройки
        verify_setup()
        
        # Вывод следующих шагов
        print_next_steps()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Настройка прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
