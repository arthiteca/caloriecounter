#!/usr/bin/env python3
"""
Скрипт для генерации ключей доступа к боту
"""
import asyncio
import sys
from auth_keys import generate_default_keys, save_keys_to_file
from database import Database
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_keys_to_database(keys_data: dict, db: Database):
    """
    Загрузка ключей в базу данных
    
    Args:
        keys_data: Словарь с ключами
        db: Экземпляр Database
    """
    # Инициализация БД
    await db.init_db()
    
    # Добавление безлимитных ключей
    for key_info in keys_data['unlimited_keys']:
        await db.add_access_key(
            key_code=key_info['key'],
            key_type='unlimited',
            image_limit=None
        )
    
    # Добавление ограниченных ключей
    for key_info in keys_data['limited_keys']:
        await db.add_access_key(
            key_code=key_info['key'],
            key_type='limited',
            image_limit=key_info['limit']
        )
    
    logger.info("Все ключи успешно добавлены в базу данных")


async def main():
    """Основная функция"""
    print("=" * 70)
    print("ГЕНЕРАТОР КЛЮЧЕЙ ДОСТУПА")
    print("=" * 70)
    print()
    
    # Генерация ключей
    print("📝 Генерация ключей...")
    keys_data = generate_default_keys()
    
    # Сохранение в файл
    print("💾 Сохранение ключей в файл...")
    save_keys_to_file(keys_data, 'access_keys.txt')
    
    # Загрузка в базу данных
    print("🗄️  Загрузка ключей в базу данных...")
    db = Database(config.DATABASE_PATH)
    await load_keys_to_database(keys_data, db)
    
    print()
    print("=" * 70)
    print("✅ ГОТОВО!")
    print("=" * 70)
    print()
    print(f"📊 Статистика:")
    print(f"   • Безлимитных ключей: {len(keys_data['unlimited_keys'])}")
    print(f"   • Ограниченных ключей: {len(keys_data['limited_keys'])}")
    print()
    print(f"📁 Файлы:")
    print(f"   • Ключи сохранены в: access_keys.txt")
    print(f"   • База данных: {config.DATABASE_PATH}")
    print()
    print("💡 Следующие шаги:")
    print("   1. Раздайте ключи из файла access_keys.txt пользователям")
    print("   2. Запустите бота: python bot.py")
    print("   3. Пользователи должны активировать ключи командой /activate")
    print()
    print("⚠️  ВАЖНО: Храните файл access_keys.txt в безопасности!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Генерация прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
