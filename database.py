import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    daily_calorie_limit INTEGER DEFAULT 2000
                )
            """)
            
            # Таблица приёмов пищи
            await db.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    weight REAL,
                    calories REAL NOT NULL,
                    protein REAL,
                    fat REAL,
                    carbs REAL,
                    meal_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    image_processed BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Таблица запросов (для логирования и rate limiting)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS requests_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    request_type TEXT,
                    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Таблица ключей авторизации
            await db.execute("""
                CREATE TABLE IF NOT EXISTS access_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_code TEXT UNIQUE NOT NULL,
                    key_type TEXT NOT NULL,
                    image_limit INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    activated_by INTEGER,
                    activated_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (activated_by) REFERENCES users(user_id)
                )
            """)
            
            # Таблица использования ключей (для отслеживания лимитов)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS key_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key_id INTEGER NOT NULL,
                    usage_type TEXT NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (key_id) REFERENCES access_keys(id)
                )
            """)
            
            await db.commit()
            logger.info("База данных инициализирована")
    
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Добавление нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (user_id, username, first_name))
            await db.commit()
    
    async def add_meal(self, user_id: int, product_name: str, calories: float,
                      weight: Optional[float] = None, protein: Optional[float] = None,
                      fat: Optional[float] = None, carbs: Optional[float] = None,
                      image_processed: bool = False):
        """Добавление приёма пищи"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO meals (user_id, product_name, weight, calories, protein, fat, carbs, image_processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, product_name, weight, calories, protein, fat, carbs, image_processed))
            await db.commit()
            logger.info(f"Добавлен приём пищи для пользователя {user_id}: {product_name}")
    
    async def get_daily_calories(self, user_id: int, date: Optional[str] = None) -> Dict:
        """Получение суммарных калорий за день"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT 
                    COALESCE(SUM(calories), 0) as total_calories,
                    COALESCE(SUM(protein), 0) as total_protein,
                    COALESCE(SUM(fat), 0) as total_fat,
                    COALESCE(SUM(carbs), 0) as total_carbs,
                    COUNT(*) as meal_count
                FROM meals
                WHERE user_id = ? AND DATE(meal_time) = ?
            """, (user_id, date)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'total_calories': row['total_calories'],
                        'total_protein': row['total_protein'],
                        'total_fat': row['total_fat'],
                        'total_carbs': row['total_carbs'],
                        'meal_count': row['meal_count']
                    }
                return {'total_calories': 0, 'total_protein': 0, 'total_fat': 0, 'total_carbs': 0, 'meal_count': 0}
    
    async def get_user_meals_today(self, user_id: int) -> List[Dict]:
        """Получение всех приёмов пищи пользователя за сегодня"""
        date = datetime.now().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM meals
                WHERE user_id = ? AND DATE(meal_time) = ?
                ORDER BY meal_time DESC
            """, (user_id, date)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def log_request(self, user_id: int, request_type: str):
        """Логирование запроса для rate limiting"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO requests_log (user_id, request_type)
                VALUES (?, ?)
            """, (user_id, request_type))
            await db.commit()
    
    async def check_rate_limit(self, user_id: int, minutes: int = 1, max_requests: int = 20) -> bool:
        """Проверка ограничения скорости запросов"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT COUNT(*) as count FROM requests_log
                WHERE user_id = ? AND request_time >= datetime('now', '-' || ? || ' minutes')
            """, (user_id, minutes)) as cursor:
                row = await cursor.fetchone()
                count = row[0] if row else 0
                return count < max_requests
    
    async def get_user_daily_limit(self, user_id: int) -> int:
        """Получение дневной нормы калорий пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT daily_calorie_limit FROM users WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 2000
    
    # ==================== МЕТОДЫ ДЛЯ РАБОТЫ С КЛЮЧАМИ ====================
    
    async def add_access_key(self, key_code: str, key_type: str, image_limit: Optional[int] = None):
        """Добавление ключа доступа в базу данных"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO access_keys (key_code, key_type, image_limit)
                    VALUES (?, ?, ?)
                """, (key_code, key_type, image_limit))
                await db.commit()
                logger.info(f"Ключ добавлен: {key_code[:8]}... (тип: {key_type})")
                return True
            except Exception as e:
                logger.error(f"Ошибка при добавлении ключа: {e}")
                return False
    
    async def activate_key(self, key_code: str, user_id: int) -> Dict:
        """
        Активация ключа пользователем
        
        Returns:
            Dict с результатом активации
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Проверка существования ключа
            async with db.execute("""
                SELECT * FROM access_keys WHERE key_code = ?
            """, (key_code,)) as cursor:
                key_row = await cursor.fetchone()
            
            if not key_row:
                return {'success': False, 'message': 'Ключ не найден'}
            
            # Проверка, не активирован ли ключ
            if key_row['activated_by'] is not None:
                return {'success': False, 'message': 'Ключ уже активирован'}
            
            # Проверка, не активирован ли уже другой ключ этим пользователем
            async with db.execute("""
                SELECT * FROM access_keys WHERE activated_by = ?
            """, (user_id,)) as cursor:
                existing_key = await cursor.fetchone()
            
            if existing_key:
                return {'success': False, 'message': 'У вас уже активирован ключ'}
            
            # Активация ключа
            await db.execute("""
                UPDATE access_keys 
                SET activated_by = ?, activated_at = CURRENT_TIMESTAMP
                WHERE key_code = ?
            """, (user_id, key_code))
            await db.commit()
            
            return {
                'success': True,
                'message': 'Ключ успешно активирован!',
                'key_type': key_row['key_type'],
                'image_limit': key_row['image_limit']
            }
    
    async def check_user_access(self, user_id: int) -> Dict:
        """
        Проверка доступа пользователя
        
        Returns:
            Dict с информацией о доступе
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Получаем ключ пользователя
            async with db.execute("""
                SELECT * FROM access_keys WHERE activated_by = ? AND is_active = 1
            """, (user_id,)) as cursor:
                key_row = await cursor.fetchone()
            
            if not key_row:
                return {
                    'has_access': False,
                    'message': 'Доступ не активирован. Используйте /activate'
                }
            
            key_id = key_row['id']
            key_type = key_row['key_type']
            image_limit = key_row['image_limit']
            
            # Если безлимитный ключ
            if key_type == 'unlimited':
                return {
                    'has_access': True,
                    'key_type': 'unlimited',
                    'images_used': 0,
                    'images_left': None,
                    'message': 'Безлимитный доступ'
                }
            
            # Для ограниченного ключа - подсчитываем использование
            async with db.execute("""
                SELECT COUNT(*) as count FROM key_usage
                WHERE user_id = ? AND key_id = ? AND usage_type = 'image'
            """, (user_id, key_id)) as cursor:
                usage_row = await cursor.fetchone()
                images_used = usage_row['count'] if usage_row else 0
            
            images_left = image_limit - images_used
            
            if images_left <= 0:
                return {
                    'has_access': False,
                    'key_type': 'limited',
                    'images_used': images_used,
                    'images_left': 0,
                    'message': f'Лимит исчерпан ({image_limit}/{image_limit})'
                }
            
            return {
                'has_access': True,
                'key_type': 'limited',
                'images_used': images_used,
                'images_left': images_left,
                'message': f'Доступ активен ({images_used}/{image_limit})'
            }
    
    async def log_key_usage(self, user_id: int, usage_type: str = 'image'):
        """Логирование использования ключа"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем key_id пользователя
            async with db.execute("""
                SELECT id FROM access_keys WHERE activated_by = ? AND is_active = 1
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
            
            if row:
                key_id = row[0]
                await db.execute("""
                    INSERT INTO key_usage (user_id, key_id, usage_type)
                    VALUES (?, ?, ?)
                """, (user_id, key_id, usage_type))
                await db.commit()
                logger.info(f"Использование ключа записано: user={user_id}, type={usage_type}")
    
    async def get_user_key_stats(self, user_id: int) -> Dict:
        """Получение статистики по ключу пользователя"""
        access_info = await self.check_user_access(user_id)
        
        if not access_info.get('has_access') and access_info.get('key_type'):
            # Ключ есть, но лимит исчерпан
            return access_info
        
        return access_info
