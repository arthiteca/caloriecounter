#!/usr/bin/env python3
"""
Генератор ключей доступа:
 - 5 безлимитных
 - 20 на 100 изображений
 - 20 на 50 изображений
 - 20 на 20 изображений

Повторный запуск НЕ меняет уже активированные ключи и не трогает существующие.
Скрипт только ДОБАВЛЯЕТ недостающие ключи для достижения целевых количеств.
"""
import asyncio
import sys
import secrets
import string
import aiosqlite
from database import Database
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TARGETS = {
    ('unlimited', None): 5,   # (key_type, image_limit) -> count
    ('limited', 100): 20,
    ('limited', 50): 20,
    ('limited', 20): 20,
}


def generate_key(prefix: str) -> str:
    """Генерирует читаемый ключ PREFIX-XXXX-XXXX (без похожих символов)."""
    alphabet = (string.ascii_uppercase.replace('O', '').replace('I', '') +
                string.digits.replace('0', '').replace('1', ''))
    def seg():
        return ''.join(secrets.choice(alphabet) for _ in range(4))
    return f"{prefix}-{seg()}-{seg()}"


def make_prefix(key_type: str, limit: int | None) -> str:
    if key_type == 'unlimited':
        return 'AILAB-UNLIM'
    if limit == 100:
        return 'AILAB-PRO100'
    if limit == 50:
        return 'AILAB-PLUS50'
    return 'AILAB-BASE20'


async def fetch_existing(db_path: str):
    """Возвращает существующие ключи и их категории."""
    result = {
        ('unlimited', None): [],
        ('limited', 100): [],
        ('limited', 50): [],
        ('limited', 20): [],
    }
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT key_code, key_type, image_limit, activated_by FROM access_keys") as cur:
            async for row in cur:
                key = row['key_code']
                ktype = row['key_type']
                lim = row['image_limit']
                key_tuple = (ktype, lim)
                if key_tuple in result:
                    result[key_tuple].append((key, row['activated_by']))
    return result


async def add_missing_keys(db: Database, existing: dict):
    """Добавляет недостающие ключи согласно TARGETS, не изменяя существующие."""
    # Собираем множество уже занятых кодов для исключения коллизий
    used_codes: set[str] = set()
    for keys in existing.values():
        for code, _ in keys:
            used_codes.add(code)

    # Для каждой категории добиваем до целевого числа
    for (key_type, limit), target in TARGETS.items():
        current = existing[(key_type, limit)]
        need = max(0, target - len(current))
        if need == 0:
            logger.info(f"Категория {key_type}:{limit} уже укомплектована ({len(current)}/{target})")
            continue

        prefix = make_prefix(key_type, limit)
        logger.info(f"Добавляю {need} ключ(ей) для {key_type}:{limit}...")
        for _ in range(need):
            # Генерируем уникальный код
            for _attempt in range(100):
                code = generate_key(prefix)
                if code not in used_codes:
                    break
            used_codes.add(code)
            await db.add_access_key(
                key_code=code,
                key_type=key_type,
                image_limit=limit
            )


async def save_all_keys_to_file(db_path: str, filename: str = 'access_keys.txt'):
    """Сохраняет ВСЕ ключи в файл (с пометкой активированных)."""
    sections = {
        ('unlimited', None): '🔓 БЕЗЛИМИТНЫЕ КЛЮЧИ (5 шт.)',
        ('limited', 100): '💎 КЛЮЧИ НА 100 АНАЛИЗОВ (20 шт.)',
        ('limited', 50): '⭐ КЛЮЧИ НА 50 АНАЛИЗОВ (20 шт.)',
        ('limited', 20): '🔐 КЛЮЧИ НА 20 АНАЛИЗОВ (20 шт.)',
    }
    data = await fetch_existing(db_path)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('КЛЮЧИ ДОСТУПА\n')
        f.write('='*70 + '\n\n')
        for cat in [('unlimited', None), ('limited', 100), ('limited', 50), ('limited', 20)]:
            f.write(sections[cat] + '\n')
            f.write('-'*70 + '\n')
            items = sorted(data[cat], key=lambda x: (x[1] is not None, x[0]))  # активированные вниз/вверх
            for i, (code, activated_by) in enumerate(items, 1):
                mark = ' [ACTIVATED]' if activated_by is not None else ''
                f.write(f"{i:2d}. {code}{mark}\n")
            f.write('\n')


async def main():
    print('=' * 70)
    print('ГЕНЕРАЦИЯ КЛЮЧЕЙ (идемпотентная)')
    print('=' * 70)

    db = Database(config.DATABASE_PATH)
    # Инициализация БД/таблиц
    await db.init_db()

    # Читаем существующие
    existing = await fetch_existing(config.DATABASE_PATH)

    # Добавляем недостающие (уже активированные не трогаем)
    await add_missing_keys(db, existing)

    # Перечитываем и сохраняем весь список в файл
    await save_all_keys_to_file(config.DATABASE_PATH, 'access_keys.txt')

    # Выводим стату
    updated = await fetch_existing(config.DATABASE_PATH)
    print('\n📊 Текущее количество:')
    for (key_type, limit), target in TARGETS.items():
        cnt = len(updated[(key_type, limit)])
        print(f" - {key_type}:{limit} → {cnt}/{target}")

    print('\n✅ ГОТОВО!\n')
    print(f"База данных: {config.DATABASE_PATH}")
    print(f"Файл ключей: access_keys.txt")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  Генерация прервана пользователем')
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
