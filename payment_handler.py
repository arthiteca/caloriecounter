import asyncio
import base64
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from payment_buttons import PaymentButtons, PaymentMessages
from config import PAYMENT_PRICES, WEBHOOK_URL
from database import Database
import config

logger = logging.getLogger(__name__)

class PaymentHandler:
    """Обработчик платежей в Telegram боте"""
    
    def __init__(self, db: Database):
        self.db = db
        self.sbp_service = None
    
    async def handle_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback'ов от кнопок оплаты"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        logger.info(f"Payment callback from user {user_id}: {data}")
        
        if data == "buy_key":
            await self._handle_buy_key(query, context)
        elif data == "select_tariff":
            await self._handle_select_tariff(query, context)
        elif data.startswith("tariff_"):
            tariff_key = data.replace("tariff_", "")
            await self._handle_tariff_selection(query, context, tariff_key)
        elif data.startswith("confirm_payment_"):
            tariff_key = data.replace("confirm_payment_", "")
            await self._handle_payment_confirmation(query, context, tariff_key)
        elif data.startswith("payment_qr_"):
            payment_id = data.replace("payment_qr_", "")
            await self._handle_payment_qr(query, context, payment_id)
        elif data.startswith("payment_link_"):
            payment_id = data.replace("payment_link_", "")
            await self._handle_payment_link(query, context, payment_id)
        elif data.startswith("check_status_"):
            payment_id = data.replace("check_status_", "")
            await self._handle_check_status(query, context, payment_id)
        elif data == "cancel_payment":
            await self._handle_cancel_payment(query, context)
        elif data == "back_to_main":
            await self._handle_back_to_main(query, context)
        elif data == "main_menu":
            await self._handle_main_menu(query, context)
        else:
            await query.edit_message_text("❌ Неизвестная команда")
    
    async def _handle_buy_key(self, query, context):
        """Обработка нажатия 'Купить ключ'"""
        # Проверяем, не активирован ли уже ключ
        access_info = await self.db.check_user_access(query.from_user.id)
        if access_info['has_access'] or access_info.get('key_type'):
            await query.edit_message_text(
                f"✅ У вас уже активирован ключ!\n\n"
                f"📊 {access_info['message']}\n\n"
                f"Используйте кнопку 'Информация о ключе' для подробной информации.",
                reply_markup=PaymentButtons.get_back_button(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Показываем выбор тарифа
        await query.edit_message_text(
            PaymentMessages.get_tariff_selection_text(),
            reply_markup=PaymentButtons.get_tariff_buttons(),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_select_tariff(self, query, context):
        """Обработка выбора тарифа"""
        await query.edit_message_text(
            PaymentMessages.get_tariff_selection_text(),
            reply_markup=PaymentButtons.get_tariff_buttons(),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_tariff_selection(self, query, context, tariff_key):
        """Обработка выбора конкретного тарифа"""
        if tariff_key not in PAYMENT_PRICES:
            await query.edit_message_text("❌ Неверный тариф")
            return
        
        # Показываем информацию о тарифе и кнопку подтверждения
        await query.edit_message_text(
            PaymentMessages.get_tariff_info_text(tariff_key),
            reply_markup=PaymentButtons.get_payment_confirmation(tariff_key),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_payment_confirmation(self, query, context, tariff_key):
        """Обработка подтверждения оплаты"""
        tariff_data = PAYMENT_PRICES.get(tariff_key, {})
        price = tariff_data.get("price", 0)
        description = tariff_data.get("description", "")
        
        # Показываем сообщение о создании платежа
        await query.edit_message_text(
            PaymentMessages.get_payment_processing_text("creating...", price),
            parse_mode=ParseMode.HTML
        )
        
        try:
            # Здесь будет создание платежа через СБП
            # Пока что создаем заглушку
            payment_id = f"test_{query.from_user.id}_{int(asyncio.get_event_loop().time())}"
            
            # Сохраняем платеж в БД (заглушка)
            await self.db.add_sbp_payment(
                user_id=query.from_user.id,
                payment_id=payment_id,
                amount=price,
                description=f"Покупка ключа - {description}",
                payment_url="https://example.com/payment",
                qr_code=""
            )
            
            # Показываем кнопки способов оплаты
            await query.edit_message_text(
                f"""💳 <b>Платеж создан</b>

🆔 <b>ID платежа:</b> {payment_id}
💰 <b>Сумма:</b> {price} ₽
📋 <b>Описание:</b> {description}

<b>Выберите способ оплаты:</b>""",
                reply_markup=PaymentButtons.get_payment_method_buttons(payment_id),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {e}")
            await query.edit_message_text(
                PaymentMessages.get_payment_failed_text("Ошибка создания платежа"),
                reply_markup=PaymentButtons.get_support_buttons(),
                parse_mode=ParseMode.HTML
            )
    
    async def _handle_payment_qr(self, query, context, payment_id):
        """Обработка оплаты по QR-коду"""
        # Здесь будет генерация QR-кода
        await query.edit_message_text(
            f"""📱 <b>Оплата по QR-коду</b>

🆔 <b>ID платежа:</b> {payment_id}

<b>Инструкция:</b>
1. Отсканируйте QR-код в приложении банка
2. Подтвердите оплату
3. Ключ активируется автоматически

⏰ <b>Время ожидания:</b> 15 минут""",
            reply_markup=PaymentButtons.get_payment_status_buttons(payment_id),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_payment_link(self, query, context, payment_id):
        """Обработка оплаты по ссылке"""
        await query.edit_message_text(
            f"""🔗 <b>Оплата по ссылке</b>

🆔 <b>ID платежа:</b> {payment_id}

<b>Инструкция:</b>
1. Перейдите по ссылке: https://example.com/pay/{payment_id}
2. Подтвердите оплату
3. Ключ активируется автоматически

⏰ <b>Время ожидания:</b> 15 минут""",
            reply_markup=PaymentButtons.get_payment_status_buttons(payment_id),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_check_status(self, query, context, payment_id):
        """Проверка статуса платежа"""
        await query.edit_message_text(
            f"""🔄 <b>Проверка статуса</b>

🆔 <b>ID платежа:</b> {payment_id}

⏳ <b>Проверяем статус платежа...</b>

<b>Статус:</b> Обрабатывается
<b>Время:</b> {asyncio.get_event_loop().time():.0f}""",
            reply_markup=PaymentButtons.get_payment_status_buttons(payment_id),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_cancel_payment(self, query, context):
        """Отмена платежа"""
        await query.edit_message_text(
            "❌ <b>Платеж отменен</b>\n\n"
            "Вы можете создать новый платеж в любое время.",
            reply_markup=PaymentButtons.get_back_button(),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_back_to_main(self, query, context):
        """Возврат в главное меню"""
        await query.edit_message_text(
            PaymentMessages.get_payment_menu_text(),
            reply_markup=PaymentButtons.get_payment_menu(),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_main_menu(self, query, context):
        """Возврат в главное меню бота"""
        # Здесь можно добавить логику возврата в главное меню бота
        await query.edit_message_text(
            "🏠 <b>Главное меню</b>\n\n"
            "Выберите действие:",
            reply_markup=PaymentButtons.get_payment_menu(),
            parse_mode=ParseMode.HTML
        )
