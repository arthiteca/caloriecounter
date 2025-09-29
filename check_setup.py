#!/usr/bin/env python3
"""
Скрипт для проверки корректности настройки бота перед запуском
"""
import os
import sys


def check_env_file():
    """Проверка наличия .env файла"""
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("   Создайте файл .env на основе env_example.txt")
        return False
    print("✅ Файл .env найден")
    return True


def check_tokens():
    """Проверка наличия токенов в переменных окружения"""
    from dotenv import load_dotenv
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    issues = []
    
    if not telegram_token or telegram_token == "your_telegram_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN не настроен!")
        print("   Получите токен у @BotFather в Telegram")
        issues.append("telegram_token")
    else:
        print(f"✅ TELEGRAM_BOT_TOKEN настроен ({telegram_token[:10]}...)")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY не настроен!")
        print("   Получите ключ на platform.openai.com")
        issues.append("openai_key")
    else:
        print(f"✅ OPENAI_API_KEY настроен ({openai_key[:10]}...)")
    
    return len(issues) == 0


def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = [
        'telegram',
        'openai',
        'aiosqlite',
        'PIL',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'telegram':
                __import__('telegram.ext')
            elif package == 'PIL':
                __import__('PIL')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен!")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Установите недостающие пакеты:")
        print(f"   pip install -r requirements.txt")
        return False
    
    return True


def check_openai_connection():
    """Проверка подключения к OpenAI API"""
    try:
        from dotenv import load_dotenv
        import openai
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "your_openai_api_key_here":
            print("⚠️  Пропуск проверки OpenAI (ключ не настроен)")
            return True
        
        client = openai.OpenAI(api_key=api_key)
        # Простой запрос для проверки
        response = client.models.list()
        
        print("✅ Подключение к OpenAI API работает")
        
        # Проверка доступности моделей GPT-4
        models = [model.id for model in response.data]
        has_gpt4 = any('gpt-4' in model for model in models)
        
        if has_gpt4:
            print("✅ Доступ к моделям GPT-4 есть")
        else:
            print("⚠️  Модели GPT-4 не найдены. Убедитесь, что у вас есть доступ.")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при подключении к OpenAI: {e}")
        return False


def main():
    """Основная функция проверки"""
    print("🔍 Проверка настройки Calorie Counter Bot\n")
    print("=" * 50)
    
    all_checks = []
    
    print("\n📁 Проверка файлов конфигурации:")
    print("-" * 50)
    all_checks.append(check_env_file())
    
    print("\n🔑 Проверка токенов:")
    print("-" * 50)
    all_checks.append(check_tokens())
    
    print("\n📦 Проверка зависимостей:")
    print("-" * 50)
    all_checks.append(check_dependencies())
    
    print("\n🌐 Проверка подключения к OpenAI:")
    print("-" * 50)
    all_checks.append(check_openai_connection())
    
    print("\n" + "=" * 50)
    
    if all(all_checks):
        print("\n✅ Все проверки пройдены! Бот готов к запуску.")
        print("\n🚀 Запустите бота командой: python bot.py")
        return 0
    else:
        print("\n❌ Некоторые проверки не пройдены.")
        print("   Исправьте ошибки и запустите проверку снова.")
        print("\n📖 Инструкции: см. QUICKSTART.md")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
