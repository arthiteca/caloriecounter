import secrets
import string
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class AuthKeyManager:
    """Управление ключами авторизации"""
    
    KEY_LENGTH = 24
    
    @staticmethod
    def generate_key() -> str:
        """Генерация случайного ключа"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(AuthKeyManager.KEY_LENGTH))
    
    @staticmethod
    def generate_keys(count: int, limit: Optional[int] = None) -> list:
        """
        Генерация множества ключей
        
        Args:
            count: Количество ключей
            limit: Лимит использований (None = безлимитный)
            
        Returns:
            Список словарей с информацией о ключах
        """
        keys = []
        for i in range(count):
            key = AuthKeyManager.generate_key()
            keys.append({
                'key': key,
                'limit': limit,
                'key_type': 'unlimited' if limit is None else 'limited'
            })
        return keys
    
    @staticmethod
    def format_key_for_display(key: str) -> str:
        """Форматирование ключа для отображения (xxxx-xxxx-xxxx-xxxx)"""
        # Разбиваем ключ на группы по 6 символов
        parts = [key[i:i+6] for i in range(0, len(key), 6)]
        return '-'.join(parts)


def generate_default_keys() -> Dict:
    """
    Генерация набора ключей по умолчанию:
    - 5 безлимитных ключей
    - 20 ключей с лимитом 100 изображений
    - 20 ключей с лимитом 50 изображений
    - 20 ключей с лимитом 10 изображений
    
    Returns:
        Словарь с типами ключей
    """
    result = {
        'limited_keys': [],
        'unlimited_keys': []
    }
    
    # Генерация 5 безлимитных ключей
    unlimited = AuthKeyManager.generate_keys(count=5, limit=None)
    result['unlimited_keys'] = unlimited
    
    # Генерация 20 ключей с лимитом 100 изображений
    limited_100 = AuthKeyManager.generate_keys(count=20, limit=100)
    result['limited_keys'].extend(limited_100)
    
    # Генерация 20 ключей с лимитом 50 изображений
    limited_50 = AuthKeyManager.generate_keys(count=20, limit=50)
    result['limited_keys'].extend(limited_50)
    
    # Генерация 20 ключей с лимитом 10 изображений
    limited_10 = AuthKeyManager.generate_keys(count=20, limit=10)
    result['limited_keys'].extend(limited_10)
    
    logger.info(f"Сгенерировано {len(result['limited_keys'])} ограниченных и {len(result['unlimited_keys'])} безлимитных ключей")
    logger.info(f"  - 20 ключей на 100 анализов")
    logger.info(f"  - 20 ключей на 50 анализов") 
    logger.info(f"  - 20 ключей на 10 анализов")
    
    return result


def save_keys_to_file(keys_data: Dict, filename: str = 'access_keys.txt'):
    """
    Сохранение ключей в текстовый файл
    
    Args:
        keys_data: Словарь с ключами
        filename: Имя файла для сохранения
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("КЛЮЧИ ДОСТУПА К TELEGRAM-БОТУ ДЛЯ ПОДСЧЁТА КАЛОРИЙ\n")
        f.write("=" * 70 + "\n\n")
        
        # Безлимитные ключи
        if keys_data['unlimited_keys']:
            f.write("🔓 БЕЗЛИМИТНЫЙ КЛЮЧ (неограниченное использование):\n")
            f.write("-" * 70 + "\n")
            for idx, key_info in enumerate(keys_data['unlimited_keys'], 1):
                key = key_info['key']
                formatted = AuthKeyManager.format_key_for_display(key)
                f.write(f"{idx}. {key}\n")
                f.write(f"   Формат: {formatted}\n")
                f.write(f"   Лимит: Безлимитный\n\n")
        
        # Ограниченные ключи
        if keys_data['limited_keys']:
            f.write("\n🔐 КЛЮЧИ С ЛИМИТОМ:\n")
            f.write("-" * 70 + "\n")
            
            # Группируем ключи по лимитам
            limits = {}
            for key_info in keys_data['limited_keys']:
                limit = key_info['limit']
                if limit not in limits:
                    limits[limit] = []
                limits[limit].append(key_info)
            
            # Выводим ключи по группам
            for limit in sorted(limits.keys(), reverse=True):
                keys_with_limit = limits[limit]
                f.write(f"\n📊 КЛЮЧИ НА {limit} АНАЛИЗОВ ИЗОБРАЖЕНИЙ ({len(keys_with_limit)} шт.):\n")
                f.write("-" * 50 + "\n")
                for idx, key_info in enumerate(keys_with_limit, 1):
                    key = key_info['key']
                    formatted = AuthKeyManager.format_key_for_display(key)
                    f.write(f"{idx}. {key}\n")
                    f.write(f"   Формат: {formatted}\n")
                    f.write(f"   Лимит: {limit} изображений\n\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("КАК ИСПОЛЬЗОВАТЬ:\n")
        f.write("-" * 70 + "\n")
        f.write("1. Запустите бота в Telegram\n")
        f.write("2. Отправьте команду: /activate\n")
        f.write("3. Введите один из ключей выше\n")
        f.write("4. Начните использовать бота!\n\n")
        f.write("ВАЖНО:\n")
        f.write("• Один ключ может использоваться только один раз\n")
        f.write("• Ограниченные ключи имеют лимит только на АНАЛИЗ ИЗОБРАЖЕНИЙ\n")
        f.write("• Текстовые запросы не учитываются в лимите\n")
        f.write("• После активации ключ привязывается к вашему Telegram ID\n")
        f.write("• Доступны ключи: 5 безлимитных, 20 на 100, 20 на 50, 20 на 10 анализов\n")
        f.write("=" * 70 + "\n")
    
    logger.info(f"Ключи сохранены в файл: {filename}")


if __name__ == "__main__":
    # Тестовая генерация ключей
    logging.basicConfig(level=logging.INFO)
    
    print("Генерация ключей доступа...")
    keys = generate_default_keys()
    
    save_keys_to_file(keys)
    
    print("\n✅ Ключи успешно сгенерированы и сохранены в access_keys.txt")
    print(f"   • Безлимитных ключей: {len(keys['unlimited_keys'])}")
    print(f"   • Ограниченных ключей: {len(keys['limited_keys'])}")
    
    # Подсчет по типам ограниченных ключей
    limits = {}
    for key_info in keys['limited_keys']:
        limit = key_info['limit']
        limits[limit] = limits.get(limit, 0) + 1
    
    for limit in sorted(limits.keys(), reverse=True):
        print(f"     - {limits[limit]} ключей на {limit} анализов")
