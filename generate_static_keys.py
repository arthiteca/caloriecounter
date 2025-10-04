#!/usr/bin/env python3
"""
Генератор статичных ключей доступа с разными уровнями
"""
import asyncio
import sys
import random
import string
from database import Database
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_random_segment(length: int = 4) -> str:
    """
    Генерирует случайный сегмент ключа из букв и цифр
    Исключает похожие символы: 0/O, 1/I/l для удобства ввода
    """
    chars = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')
    return ''.join(random.choice(chars) for _ in range(length))


def generate_key(prefix: str, suffix_length: int = 8) -> str:
    """
    Генерирует случайный ключ с заданным префиксом
    
    Args:
        prefix: Префикс ключа (например, 'AILAB-UNLIM')
        suffix_length: Длина случайной части (по умолчанию 8 символов)
    
    Returns:
        Сгенерированный ключ в формате PREFIX-XXXX-XXXX
    """
    # Разбиваем случайную часть на сегменты по 4 символа для читаемости
    segments = [generate_random_segment(4) for _ in range(suffix_length // 4)]
    random_part = '-'.join(segments)
    return f"{prefix}-{random_part}"


# СТАТИЧНЫЕ КЛЮЧИ С РАЗНЫМИ УРОВНЯМИ ДОСТУПА
# Генерируем случайные, но статичные ключи с фиксированным seed
random.seed(42)  # Фиксированный seed для воспроизводимости

STATIC_KEYS = {
    # 5 безлимитных ключей
    'unlimited': [
        generate_key('AILAB-UNLIM') for _ in range(5)
    ],
    
    # 20 ключей на 100 анализов
    'limit_100': [
        generate_key('AILAB-PRO100') for _ in range(20)
    ],
    
    # 20 ключей на 50 анализов
    'limit_50': [
        generate_key('AILAB-PLUS50') for _ in range(20)
    ],
    
    # 20 ключей на 20 анализов
    'limit_20': [
        generate_key('AILAB-BASE20') for _ in range(20)
    ]
}


def format_key_display(key: str) -> str:
    """Форматирование ключа для отображения"""
    # Разбиваем по дефисам
    parts = key.split('-')
    return '-'.join(parts)


async def load_keys_to_database(db: Database):
    """
    Загрузка статичных ключей в базу данных
    
    Args:
        db: Экземпляр Database
    """
    # Инициализация БД
    await db.init_db()
    
    total_added = 0
    
    # Добавление безлимитных ключей
    logger.info("Добавление безлимитных ключей...")
    for key in STATIC_KEYS['unlimited']:
        await db.add_access_key(
            key_code=key,
            key_type='unlimited',
            image_limit=None
        )
        total_added += 1
    
    # Добавление ключей на 100 анализов
    logger.info("Добавление ключей на 100 анализов...")
    for key in STATIC_KEYS['limit_100']:
        await db.add_access_key(
            key_code=key,
            key_type='limited',
            image_limit=100
        )
        total_added += 1
    
    # Добавление ключей на 50 анализов
    logger.info("Добавление ключей на 50 анализов...")
    for key in STATIC_KEYS['limit_50']:
        await db.add_access_key(
            key_code=key,
            key_type='limited',
            image_limit=50
        )
        total_added += 1
    
    # Добавление ключей на 20 анализов
    logger.info("Добавление ключей на 20 анализов...")
    for key in STATIC_KEYS['limit_20']:
        await db.add_access_key(
            key_code=key,
            key_type='limited',
            image_limit=20
        )
        total_added += 1
    
    logger.info(f"Всего добавлено ключей: {total_added}")


def save_keys_to_file(filename: str = 'КЛЮЧИ_ДОСТУПА.txt'):
    """Сохранение ключей в текстовый файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("              КЛЮЧИ ДОСТУПА К БОТУ ДЛЯ ПОДСЧЁТА КАЛОРИЙ\n")
        f.write("                        Made by AI LAB\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("📞 Контакты:\n")
        f.write("   • Telegram: @unrealartur (https://t.me/unrealartur)\n")
        f.write("   • Для покупки новых ключей обращайтесь в Telegram\n")
        f.write("   • Для технической поддержки: @unrealartur\n\n")
        
        f.write("=" * 80 + "\n\n")
        
        # Безлимитные ключи
        f.write("🔓 БЕЗЛИМИТНЫЕ КЛЮЧИ (5 шт.) - Неограниченное количество анализов\n")
        f.write("-" * 80 + "\n")
        for idx, key in enumerate(STATIC_KEYS['unlimited'], 1):
            f.write(f"{idx}. {key}\n")
        f.write("\n")
        
        # Ключи на 100 анализов
        f.write("💎 КЛЮЧИ НА 100 АНАЛИЗОВ (20 шт.)\n")
        f.write("-" * 80 + "\n")
        for idx, key in enumerate(STATIC_KEYS['limit_100'], 1):
            f.write(f"{idx:2d}. {key}\n")
        f.write("\n")
        
        # Ключи на 50 анализов
        f.write("⭐ КЛЮЧИ НА 50 АНАЛИЗОВ (20 шт.)\n")
        f.write("-" * 80 + "\n")
        for idx, key in enumerate(STATIC_KEYS['limit_50'], 1):
            f.write(f"{idx:2d}. {key}\n")
        f.write("\n")
        
        # Ключи на 20 анализов
        f.write("🔐 КЛЮЧИ НА 20 АНАЛИЗОВ (20 шт.)\n")
        f.write("-" * 80 + "\n")
        for idx, key in enumerate(STATIC_KEYS['limit_20'], 1):
            f.write(f"{idx:2d}. {key}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("ИНСТРУКЦИЯ ПО АКТИВАЦИИ:\n")
        f.write("-" * 80 + "\n")
        f.write("1. Запустите бота в Telegram\n")
        f.write("2. Отправьте команду: /activate\n")
        f.write("3. Введите один из ключей выше\n")
        f.write("4. Начните использовать бота!\n\n")
        
        f.write("⚠️  ВАЖНО:\n")
        f.write("• Один ключ можно активировать только один раз\n")
        f.write("• После активации ключ привязывается к вашему Telegram ID\n")
        f.write("• Для покупки новых ключей: @unrealartur\n")
        f.write("=" * 80 + "\n")
    
    logger.info(f"Ключи сохранены в файл: {filename}")


async def main():
    """Основная функция"""
    print("=" * 80)
    print("         ГЕНЕРАТОР СТАТИЧНЫХ КЛЮЧЕЙ ДОСТУПА")
    print("                   Made by AI LAB")
    print("=" * 80)
    print()
    
    # Сохранение в файл
    print("💾 Сохранение ключей в файл...")
    save_keys_to_file()
    
    # Загрузка в базу данных
    print("🗄️  Загрузка ключей в базу данных...")
    db = Database(config.DATABASE_PATH)
    await load_keys_to_database(db)
    
    print()
    print("=" * 80)
    print("✅ ГОТОВО!")
    print("=" * 80)
    print()
    print("📊 Статистика:")
    print(f"   • Безлимитных ключей: {len(STATIC_KEYS['unlimited'])}")
    print(f"   • Ключей на 100 анализов: {len(STATIC_KEYS['limit_100'])}")
    print(f"   • Ключей на 50 анализов: {len(STATIC_KEYS['limit_50'])}")
    print(f"   • Ключей на 20 анализов: {len(STATIC_KEYS['limit_20'])}")
    print(f"   • ВСЕГО: {sum(len(v) for v in STATIC_KEYS.values())}")
    print()
    print("📁 Файлы:")
    print("   • Ключи сохранены в: КЛЮЧИ_ДОСТУПА.txt")
    print(f"   • База данных: {config.DATABASE_PATH}")
    print()
    print("💡 Следующие шаги:")
    print("   1. Раздайте ключи из файла КЛЮЧИ_ДОСТУПА.txt")
    print("   2. Запустите бота: python bot.py")
    print("   3. Пользователи активируют ключи: /activate")
    print()
    print("📞 Контакты: @unrealartur (https://t.me/unrealartur)")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Генерация прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
