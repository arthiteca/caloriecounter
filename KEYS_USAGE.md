# 🔑 Система ключей доступа

## 📋 Описание

Бот использует систему ключей доступа для контроля использования. Есть два типа ключей:

- **🔓 Безлимитный ключ** - неограниченное использование всех функций
- **🔐 Ограниченный ключ** - лимит на анализ изображений (20 изображений)

### Особенности:
- ✅ Текстовые запросы **не ограничены** для всех типов ключей
- 📊 Лимит распространяется **только на анализ изображений**
- 🔒 Один ключ может быть использован только **один раз**
- 👤 Один пользователь может активировать только **один ключ**

---

## 🚀 Быстрый старт

### Шаг 1: Генерация ключей

Запустите скрипт генерации ключей:

```bash
# С активированным виртуальным окружением
.\venv\Scripts\python.exe generate_keys.py
```

Это создаст:
- **1** безлимитный ключ
- **10** ограниченных ключей (по 20 изображений каждый)

### Шаг 2: Получение ключей

После генерации ключи будут сохранены в файл `access_keys.txt` и загружены в базу данных.

### Шаг 3: Раздача ключей

Раздайте ключи из файла `access_keys.txt` пользователям.

---

## 👥 Использование для пользователей

### Активация ключа

1. Запустите бота: `/start`
2. Введите команду: `/activate`
3. Отправьте ваш ключ (можно с дефисами или без)

**Пример:**
```
/activate
VxK3mNp9QwErT2yU8bZaCsDf
```

или

```
/activate
VxK3mN-p9QwEr-T2yU8b-ZaCsDf
```

### Проверка статуса ключа

```
/key_info
```

Покажет:
- Тип ключа (безлимитный/ограниченный)
- Использованные анализы изображений
- Оставшиеся анализы

---

## 📊 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/activate` | Активировать ключ доступа |
| `/key_info` | Информация о вашем ключе |
| `/stats` | Статистика калорий за день |
| `/history` | История приёмов пищи |
| `/help` | Справка |

---

## 🔧 Настройка системы ключей

### Изменение количества ключей

Отредактируйте файл `auth_keys.py`, функцию `generate_default_keys()`:

```python
def generate_default_keys() -> Dict:
    result = {
        'limited_keys': [],
        'unlimited_keys': []
    }
    
    # Измените количество ограниченных ключей (сейчас 10)
    limited = AuthKeyManager.generate_keys(count=10, limit=20)
    result['limited_keys'] = limited
    
    # Измените количество безлимитных ключей (сейчас 1)
    unlimited = AuthKeyManager.generate_keys(count=1, limit=None)
    result['unlimited_keys'] = unlimited
    
    return result
```

### Изменение лимита изображений

В том же файле измените параметр `limit`:

```python
# Было: 20 изображений
limited = AuthKeyManager.generate_keys(count=10, limit=20)

# Стало: 50 изображений
limited = AuthKeyManager.generate_keys(count=10, limit=50)
```

---

## 🗄️ Структура базы данных

### Таблица `access_keys`

Хранит все ключи доступа:

```sql
CREATE TABLE access_keys (
    id INTEGER PRIMARY KEY,
    key_code TEXT UNIQUE,        -- Сам ключ
    key_type TEXT,               -- 'unlimited' или 'limited'
    image_limit INTEGER,         -- Лимит изображений (NULL для безлимитных)
    is_active BOOLEAN,           -- Активен ли ключ
    activated_by INTEGER,        -- ID пользователя, активировавшего ключ
    activated_at TIMESTAMP,      -- Время активации
    created_at TIMESTAMP         -- Время создания
)
```

### Таблица `key_usage`

Отслеживает использование ключей:

```sql
CREATE TABLE key_usage (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,             -- ID пользователя
    key_id INTEGER,              -- ID ключа
    usage_type TEXT,             -- 'image' или 'text'
    used_at TIMESTAMP            -- Время использования
)
```

---

## 📈 Мониторинг использования

### Просмотр активированных ключей

```python
import asyncio
from database import Database
import config

async def view_keys():
    db = Database(config.DATABASE_PATH)
    async with aiosqlite.connect(db.db_path) as conn:
        async with conn.execute("""
            SELECT key_code, key_type, activated_by, activated_at 
            FROM access_keys 
            WHERE activated_by IS NOT NULL
        """) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                print(f"Ключ: {row[0][:8]}... | Тип: {row[1]} | User: {row[2]} | Активирован: {row[3]}")

asyncio.run(view_keys())
```

### Статистика использования

```sql
SELECT 
    ak.key_type,
    ak.image_limit,
    COUNT(ku.id) as usages,
    u.username
FROM access_keys ak
LEFT JOIN key_usage ku ON ak.id = ku.key_id
LEFT JOIN users u ON ak.activated_by = u.user_id
WHERE ak.activated_by IS NOT NULL
GROUP BY ak.id
```

---

## 🎯 Примеры использования

### Пример 1: Пользователь с ограниченным ключом

```
Пользователь: /activate
Бот: 🔑 Введите ваш ключ доступа...

Пользователь: VxK3mNp9QwErT2yU8bZaCsDf
Бот: ✅ Ключ успешно активирован!
     🔐 Тип: Ограниченный
     📊 Лимит изображений: 20 шт.

Пользователь: [отправляет фото блюда]
Бот: 🍽 Продукт: Салат Цезарь (300 г)
     📊 Калории: 420 ккал
     ...
     📊 Осталось анализов изображений: 19

Пользователь: /key_info
Бот: 🔐 Информация о вашем ключе
     Тип: Ограниченный
     Использовано: 1
     Осталось: 19
```

### Пример 2: Исчерпан лимит

```
Пользователь: [отправляет 21-е фото]
Бот: ❌ Лимит исчерпан (20/20)
     Вы можете продолжать использовать текстовые запросы.

Пользователь: куриная грудка 200г
Бот: 🍽 Продукт: Куриная грудка (200 г)
     📊 Калории: 220 ккал
     ... [работает нормально]
```

### Пример 3: Безлимитный ключ

```
Пользователь: /activate
Бот: 🔑 Введите ваш ключ доступа...

Пользователь: YnP7kQwMxZe4rVbC2hUgTaLs
Бот: ✅ Ключ успешно активирован!
     🔓 Тип: Безлимитный
     ✨ Вы получили полный доступ!

Пользователь: /key_info
Бот: 🔓 Информация о вашем ключе
     Тип: Безлимитный
     Анализ изображений: Безлимитно
     Текстовые запросы: Безлимитно
```

---

## ⚠️ Важные замечания

### Безопасность

1. **Не делитесь файлом `access_keys.txt` публично**
2. **Храните резервные копии базы данных**
3. **Регулярно проверяйте использование ключей**
4. **Удаляйте файл `access_keys.txt` после раздачи ключей**

### Ограничения

- Один пользователь = один ключ
- Один ключ = одна активация
- Лимит только на изображения
- Текст всегда без лимита

### Расширение

Если нужно больше ключей:
1. Запустите `generate_keys.py` снова
2. Новые ключи будут добавлены в базу
3. Раздайте новые ключи пользователям

---

## 🛠️ Генерация дополнительных ключей

Создайте свой скрипт:

```python
import asyncio
from auth_keys import AuthKeyManager, save_keys_to_file
from database import Database
import config

async def generate_more_keys():
    db = Database(config.DATABASE_PATH)
    await db.init_db()
    
    # Генерация 5 ограниченных ключей по 30 изображений
    for _ in range(5):
        key = AuthKeyManager.generate_key()
        await db.add_access_key(key, 'limited', 30)
        print(f"Создан ключ: {key}")

asyncio.run(generate_more_keys())
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `bot.log`
2. Проверьте базу данных: `calorie_counter.db`
3. Убедитесь, что ключи сгенерированы: `access_keys.txt`

---

**Готово! Система ключей настроена и готова к использованию! 🎉**
