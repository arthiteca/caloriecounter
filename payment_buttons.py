from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import config

class PaymentButtons:
    """Класс для создания кнопок оплаты в Telegram боте"""
    
    @staticmethod
    def get_payment_menu():
        """Главное меню оплаты"""
        keyboard = [
            [InlineKeyboardButton("💎 Купить ключ доступа", callback_data="buy_key")],
            [InlineKeyboardButton("🔐 Информация о ключе", callback_data="key_info")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_tariff_buttons():
        """Кнопки выбора тарифа"""
        keyboard = [
            [
                InlineKeyboardButton("🔐 10 анализов - 100₽", callback_data="tariff_limited_10"),
                InlineKeyboardButton("🔐 50 анализов - 400₽", callback_data="tariff_limited_50")
            ],
            [
                InlineKeyboardButton("🔐 100 анализов - 700₽", callback_data="tariff_limited_100"),
                InlineKeyboardButton("🔓 Безлимит - 1500₽", callback_data="tariff_unlimited")
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_confirmation(tariff_key):
        """Кнопки подтверждения оплаты"""
        tariff_data = config.PAYMENT_PRICES.get(tariff_key, {})
        price = tariff_data.get("price", 0)
        description = tariff_data.get("description", "")
        
        keyboard = [
            [InlineKeyboardButton(f"💳 Оплатить {price}₽", callback_data=f"confirm_payment_{tariff_key}")],
            [InlineKeyboardButton("🔙 Выбрать другой тариф", callback_data="select_tariff")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel_payment")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_method_buttons(payment_id):
        """Кнопки способов оплаты"""
        keyboard = [
            [InlineKeyboardButton("📱 QR-код", callback_data=f"payment_qr_{payment_id}")],
            [InlineKeyboardButton("🔗 Ссылка", callback_data=f"payment_link_{payment_id}")],
            [InlineKeyboardButton("🔄 Обновить статус", callback_data=f"check_status_{payment_id}")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel_payment")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_status_buttons(payment_id):
        """Кнопки для проверки статуса платежа"""
        keyboard = [
            [InlineKeyboardButton("🔄 Проверить статус", callback_data=f"check_status_{payment_id}")],
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/unrealartur")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button():
        """Простая кнопка "Назад" """
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_support_buttons():
        """Кнопки поддержки"""
        keyboard = [
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/unrealartur")],
            [InlineKeyboardButton("💎 Купить ключ", callback_data="buy_key")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

class PaymentMessages:
    """Класс для сообщений оплаты"""
    
    @staticmethod
    def get_payment_menu_text(current_key_info=""):
        """Текст главного меню оплаты"""
        return f"""{current_key_info}💎 <b>Меню оплаты</b>

Выберите действие:

🔐 <b>Купить ключ доступа</b> - приобрести доступ к боту
📊 <b>Информация о ключе</b> - посмотреть текущий статус
📈 <b>Статистика</b> - ваша статистика использования
❓ <b>Помощь</b> - помощь по оплате

💡 <b>Способы оплаты:</b> СБП, банковские карты
📞 <b>Поддержка:</b> @unrealartur"""

    @staticmethod
    def get_tariff_selection_text():
        """Текст выбора тарифа"""
        return """💎 <b>Выберите тариф</b>

🔐 <b>Ограниченные ключи:</b>
• 10 анализов - 100 ₽
• 50 анализов - 400 ₽  
• 100 анализов - 700 ₽

🔓 <b>Безлимитный ключ:</b>
• Неограниченно - 1500 ₽

💳 <b>Оплата через СБП</b>
⚡ <b>Мгновенная активация</b>
🔒 <b>Безопасно и надежно</b>"""

    @staticmethod
    def get_tariff_info_text(tariff_key):
        """Информация о выбранном тарифе"""
        tariff_data = config.PAYMENT_PRICES.get(tariff_key, {})
        price = tariff_data.get("price", 0)
        description = tariff_data.get("description", "")
        limit = tariff_data.get("limit")
        
        if limit is None:
            limit_text = "Неограниченно"
        else:
            limit_text = f"{limit} анализов"
        
        return f"""💎 <b>Выбранный тариф</b>

📋 <b>Описание:</b> {description}
💰 <b>Цена:</b> {price} ₽
🔢 <b>Лимит:</b> {limit_text}

💳 <b>Способы оплаты:</b>
• СБП (Система быстрых платежей)
• Банковские карты

⚡ <b>После оплаты:</b>
• Ключ активируется автоматически
• Вы получите уведомление в боте
• Можете сразу начать использовать

📞 <b>Поддержка:</b> @unrealartur"""

    @staticmethod
    def get_payment_processing_text(payment_id, amount):
        """Текст обработки платежа"""
        return f"""💳 <b>Обработка платежа</b>

🆔 <b>ID платежа:</b> {payment_id}
💰 <b>Сумма:</b> {amount} ₽

⏳ <b>Создаем платеж...</b>
Пожалуйста, подождите несколько секунд.

📞 <b>Поддержка:</b> @unrealartur"""

    @staticmethod
    def get_payment_success_text(payment_id, amount, key_type):
        """Текст успешной оплаты"""
        return f"""✅ <b>Оплата успешна!</b>

🆔 <b>ID платежа:</b> {payment_id}
💰 <b>Сумма:</b> {amount} ₽
🔑 <b>Тип ключа:</b> {key_type}

🎉 <b>Ваш ключ активирован!</b>
Теперь вы можете использовать все функции бота.

📷 <b>Отправьте фото еды</b> и начните анализ калорий!

📞 <b>Поддержка:</b> @unrealartur"""

    @staticmethod
    def get_payment_failed_text(reason=""):
        """Текст неудачной оплаты"""
        return f"""❌ <b>Ошибка оплаты</b>

{reason if reason else "Не удалось обработать платеж"}

💡 <b>Что можно сделать:</b>
• Проверьте баланс карты/счета
• Попробуйте другой способ оплаты
• Обратитесь в поддержку

📞 <b>Поддержка:</b> @unrealartur"""

    @staticmethod
    def get_payment_timeout_text():
        """Текст таймаута платежа"""
        return """⏰ <b>Время ожидания истекло</b>

Платеж не был завершен в течение 15 минут.

💡 <b>Что можно сделать:</b>
• Проверить статус платежа
• Создать новый платеж
• Обратиться в поддержку

📞 <b>Поддержка:</b> @unrealartur"""
