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
    - 10 ключей с лимитом 20 изображений
    - 1 безлимитный ключ
    
    Returns:
        Словарь с типами ключей
    """
    result = {
        'limited_keys': [],
        'unlimited_keys': []
    }
    
    # Генерация 10 ключей с лимитом
    limited = AuthKeyManager.generate_keys(count=10, limit=20)
    result['limited_keys'] = limited
    
    # Генерация 1 безлимитного ключа
    unlimited = AuthKeyManager.generate_keys(count=1, limit=None)
    result['unlimited_keys'] = unlimited
    
    logger.info(f"Сгенерировано {len(limited)} ограниченных и {len(unlimited)} безлимитных ключей")
    
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
            f.write("\n🔐 КЛЮЧИ С ЛИМИТОМ (20 анализов изображений каждый):\n")
            f.write("-" * 70 + "\n")
            for idx, key_info in enumerate(keys_data['limited_keys'], 1):
                key = key_info['key']
                formatted = AuthKeyManager.format_key_for_display(key)
                limit = key_info['limit']
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
