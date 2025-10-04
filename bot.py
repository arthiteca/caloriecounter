import logging
import asyncio
from io import BytesIO
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

import config
from database import Database
from openai_service import OpenAIService
from payment_buttons import PaymentButtons, PaymentMessages
from payment_handler import PaymentHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CalorieCounterBot:
    """Telegram-бот для подсчета калорий"""
    
    def __init__(self):
        self.db = Database(config.DATABASE_PATH)
        self.openai_service = OpenAIService(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            vision_model=config.OPENAI_VISION_MODEL
        )
        self.payment_handler = PaymentHandler(self.db)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        await self.db.add_user(user.id, user.username, user.first_name)
        
        # Проверяем, активирован ли ключ
        access_info = await self.db.check_user_access(user.id)
        
        if not access_info.get('has_access') and not access_info.get('key_type'):
            welcome_message = f"""👋 Привет, {user.first_name}!

Я помогу тебе считать калории! 🥗

<b>Что я умею:</b>
• 📷 Распознавать еду на фотографиях
• 🔍 Определять калории и БЖУ (белки, жиры, углеводы)
• 📊 Отслеживать дневную норму калорий
• 💡 Давать рекомендации по питанию

🔐 <b>Для начала работы активируйте ключ доступа:</b>
Используйте команду /activate и введите ваш ключ.

💎 <b>Покупка ключей:</b> @unrealartur
📞 <b>Поддержка:</b> @unrealartur

<i>Made by AI LAB</i>

❓ Используй /help для полной справки"""
        else:
            welcome_message = f"""👋 Привет, {user.first_name}!

Я помогу тебе считать калории! 🥗

<b>Что я умею:</b>
• 📷 Распознавать еду на фотографиях
• 🔍 Определять калории и БЖУ (белки, жиры, углеводы)
• 📊 Отслеживать дневную норму калорий
• 💡 Давать рекомендации по питанию

<b>Как пользоваться:</b>
📷 <b>Отправь фото блюда</b> - я проанализирую калории
📊 Используй /stats для просмотра статистики за день
🔑 Используй /key_info для информации о вашем ключе
❓ Используй /help для помощи

<b>⚠️ Важно:</b> Бот работает <b>только с фотографиями!</b>

💎 <b>Покупка ключей:</b> @unrealartur
📞 <b>Обратная связь:</b> @unrealartur

<i>Made by AI LAB</i>

Давай начнём! Отправь мне фото своего блюда! 📸"""
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Новый пользователь: {user.id} ({user.username})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """📚 <b>Помощь</b>

<b>Команды:</b>
/start - Начать работу с ботом
/help - Показать это сообщение
/payment - 💎 Купить ключ доступа
/activate - Активировать ключ доступа
/key_info - Информация о вашем ключе
/stats - Статистика за сегодня
/history - История приёмов пищи за сегодня
/reset - Сбросить счётчик на сегодня

<b>Как использовать:</b>
📷 <b>Отправьте ФОТО вашего блюда</b>

⚠️ <b>Важно:</b> Бот анализирует <b>только фотографии!</b>
• Текстовые сообщения не обрабатываются
• Голосовые сообщения не поддерживаются
• Нужно именно фото еды

<b>💡 Советы для лучшего распознавания:</b>
• Снимайте при хорошем освещении
• Снимайте сверху для лучшего обзора блюда
• Убедитесь, что еда хорошо видна и не размыта
• Можете добавить подпись к фото с уточнениями

<b>Пример использования:</b>
1️⃣ Сфотографируйте ваше блюдо 📸
2️⃣ Отправьте фото мне
3️⃣ Получите анализ калорий и БЖУ!

💎 <b>Покупка ключей:</b> @unrealartur
📞 <b>Обратная связь:</b> @unrealartur

<i>Made by AI LAB</i>

Я постараюсь дать максимально точную оценку! 💪"""
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /payment - меню оплаты"""
        user_id = update.effective_user.id
        
        # Проверяем, не активирован ли уже ключ
        access_info = await self.db.check_user_access(user_id)
        if access_info['has_access'] or access_info.get('key_type'):
            await update.message.reply_text(
                f"✅ У вас уже активирован ключ!\n\n"
                f"📊 {access_info['message']}\n\n"
                f"Используйте /key_info для подробной информации.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Показываем меню оплаты с кнопками
        await update.message.reply_text(
            PaymentMessages.get_payment_menu_text(),
            reply_markup=PaymentButtons.get_payment_menu(),
            parse_mode=ParseMode.HTML
        )
    
    async def activate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /activate - активация ключа доступа"""
        user_id = update.effective_user.id
        
        # Проверяем, не активирован ли уже ключ
        access_info = await self.db.check_user_access(user_id)
        if access_info['has_access'] or access_info.get('key_type'):
            await update.message.reply_text(
                f"✅ У вас уже активирован ключ!\n\n"
                f"📊 {access_info['message']}\n\n"
                f"Используйте /key_info для подробной информации.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Просим ввести ключ
        await update.message.reply_text(
            "🔑 <b>Активация ключа доступа</b>\n\n"
            "Введите ваш ключ доступа.\n"
            "Ключ должен быть предоставлен администратором бота.\n\n"
            "Формат: XXXX-XXXX-XXXX-XXXX или слитно\n\n"
            "Отправьте ключ следующим сообщением:",
            parse_mode=ParseMode.HTML
        )
        
        # Устанавливаем ожидание ключа
        context.user_data['awaiting_key'] = True
    
    async def key_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /key_info - информация о ключе"""
        user_id = update.effective_user.id
        
        access_info = await self.db.check_user_access(user_id)
        
        if not access_info.get('has_access') and not access_info.get('key_type'):
            await update.message.reply_text(
                "❌ У вас нет активированного ключа.\n\n"
                "Используйте /activate для активации ключа доступа.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Формирование сообщения с информацией о ключе
        key_type = access_info.get('key_type', 'unknown')
        
        if key_type == 'unlimited':
            info_message = f"""🔓 <b>Информация о вашем ключе</b>

<b>Тип:</b> Безлимитный
<b>Статус:</b> ✅ Активен

<b>Доступ:</b>
• ✅ Анализ фотографий: Безлимитно

Вы можете использовать бота без ограничений! 🎉

📷 <b>Напоминание:</b> Бот работает только с фотографиями!"""
        
        else:  # limited
            images_used = access_info.get('images_used', 0)
            images_left = access_info.get('images_left', 0)
            
            status = "✅ Активен" if access_info['has_access'] else "❌ Лимит исчерпан"
            
            info_message = f"""🔐 <b>Информация о вашем ключе</b>

<b>Тип:</b> Ограниченный
<b>Статус:</b> {status}

<b>Использование:</b>
• Проанализировано фото: {images_used}
• Осталось анализов: {images_left}

<b>Доступ:</b>
• {"✅" if images_left > 0 else "❌"} Анализ фотографий: {images_left} шт.

📷 <b>Напоминание:</b> Бот работает только с фотографиями!"""
            
            if images_left <= 5 and images_left > 0:
                info_message += "\n\n⚠️ У вас осталось мало анализов!"
            elif images_left == 0:
                info_message += "\n\n❌ Лимит анализов исчерпан."
                info_message += "\n\n💎 <b>Покупка нового ключа:</b> @unrealartur"
                info_message += "\n<i>Made by AI LAB</i>"
        
        await update.message.reply_text(info_message, parse_mode=ParseMode.HTML)
    
    async def payment_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback'ов от кнопок оплаты"""
        await self.payment_handler.handle_payment_callback(update, context)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats - показывает статистику за день"""
        user_id = update.effective_user.id
        
        stats = await self.db.get_daily_calories(user_id)
        daily_limit = await self.db.get_user_daily_limit(user_id)
        
        total_calories = stats['total_calories']
        percentage = (total_calories / daily_limit) * 100 if daily_limit > 0 else 0
        
        stats_message = f"""📊 <b>Статистика за сегодня</b>

🔥 <b>Калории:</b> {total_calories:.0f} / {daily_limit} ккал ({percentage:.1f}%)
🍗 <b>Белки:</b> {stats['total_protein']:.1f} г
🥑 <b>Жиры:</b> {stats['total_fat']:.1f} г
🍞 <b>Углеводы:</b> {stats['total_carbs']:.1f} г

🍽 <b>Приёмов пищи:</b> {stats['meal_count']}
"""
        
        if percentage > 100:
            stats_message += "\n⚠️ Дневная норма превышена!"
        elif percentage > 80:
            stats_message += "\n⚡ Близко к дневной норме"
        elif percentage < 50:
            stats_message += "\n✅ Ещё много запаса на сегодня"
        
        await update.message.reply_text(stats_message, parse_mode=ParseMode.HTML)
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /history - показывает историю за день"""
        user_id = update.effective_user.id
        
        meals = await self.db.get_user_meals_today(user_id)
        
        if not meals:
            await update.message.reply_text(
                "📝 Сегодня ещё нет записей о приёмах пищи.\nОтправь фото или описание блюда, чтобы начать!",
                parse_mode=ParseMode.HTML
            )
            return
        
        history_message = "📝 <b>История приёмов пищи за сегодня:</b>\n\n"
        
        for i, meal in enumerate(meals, 1):
            meal_time = meal['meal_time'].split()[1][:5]  # Только время HH:MM
            history_message += f"{i}. <b>{meal['product_name']}</b>\n"
            if meal['weight']:
                history_message += f"   📏 {meal['weight']} г\n"
            history_message += f"   🔥 {meal['calories']:.0f} ккал | "
            history_message += f"Б: {meal['protein']:.1f}г Ж: {meal['fat']:.1f}г У: {meal['carbs']:.1f}г\n"
            history_message += f"   🕐 {meal_time}\n\n"
        
        await update.message.reply_text(history_message, parse_mode=ParseMode.HTML)
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /reset - информация о сбросе (данные не удаляются)"""
        await update.message.reply_text(
            "ℹ️ Все данные хранятся по дням.\n"
            "Каждый новый день счётчик автоматически начинается с нуля.\n"
            "История прошлых дней сохраняется.",
            parse_mode=ParseMode.HTML
        )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Проверка, ожидается ли ввод ключа
        if context.user_data.get('awaiting_key'):
            context.user_data['awaiting_key'] = False
            
            # Очистка ключа от пробелов и дефисов
            key_code = text.replace('-', '').replace(' ', '').strip()
            
            # Активация ключа
            result = await self.db.activate_key(key_code, user_id)
            
            if result['success']:
                key_type = result['key_type']
                limit = result.get('image_limit')
                
                if key_type == 'unlimited':
                    message = f"""✅ <b>Ключ успешно активирован!</b>

🔓 Тип: Безлимитный
✨ Вы получили полный доступ к боту!

Теперь вы можете анализировать неограниченное количество фотографий!

📷 <b>Отправьте фото вашего блюда и начните!</b> 🎉"""
                else:
                    message = f"""✅ <b>Ключ успешно активирован!</b>

🔐 Тип: Ограниченный
📊 Лимит: {limit} анализов фотографий

Теперь вы можете проанализировать {limit} фотографий блюд!

📷 <b>Отправьте фото вашего блюда и начните!</b> 🚀"""
                
                await update.message.reply_text(message, parse_mode=ParseMode.HTML)
                logger.info(f"Пользователь {user_id} активировал ключ типа {key_type}")
            else:
                await update.message.reply_text(
                    f"❌ {result['message']}\n\n"
                    "Пожалуйста, проверьте правильность ключа и попробуйте снова.\n"
                    "Используйте /activate для повторной попытки.",
                    parse_mode=ParseMode.HTML
                )
            
            return
        
        # Проверка доступа - нужен активированный ключ
        access_info = await self.db.check_user_access(user_id)
        if not access_info.get('has_access') and not access_info.get('key_type'):
            await update.message.reply_text(
                "🔒 <b>Для использования бота необходимо активировать ключ доступа.</b>\n\n"
                "Используйте команду /activate и введите ваш ключ.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Бот работает только с фотографиями
        await update.message.reply_text(
            "📷 <b>Пожалуйста, отправьте фото еды</b>\n\n"
            "Этот бот анализирует <b>только изображения</b> продуктов и блюд.\n\n"
            "✅ Что нужно сделать:\n"
            "1. Сфотографируйте вашу еду\n"
            "2. Отправьте фото мне\n"
            "3. Получите анализ калорий и БЖУ\n\n"
            "💡 <b>Советы для лучшего распознавания:</b>\n"
            "• Снимайте при хорошем освещении\n"
            "• Снимайте сверху для лучшего обзора\n"
            "• Убедитесь, что еда хорошо видна\n\n"
            "Жду ваше фото! 📸",
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Пользователь {user_id} отправил текст, перенаправлен на фото")
    
    async def handle_voice_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений и аудио"""
        user_id = update.effective_user.id
        
        # Проверка доступа - нужен активированный ключ
        access_info = await self.db.check_user_access(user_id)
        if not access_info.get('has_access') and not access_info.get('key_type'):
            await update.message.reply_text(
                "🔒 <b>Для использования бота необходимо активировать ключ доступа.</b>\n\n"
                "Используйте команду /activate и введите ваш ключ.",
                parse_mode=ParseMode.HTML
            )
            return
        
        await update.message.reply_text(
            "🎤 <b>Голосовые сообщения не поддерживаются</b>\n\n"
            "Этот бот анализирует <b>только фотографии</b> еды.\n\n"
            "📷 Пожалуйста, отправьте <b>фото</b> вашего блюда!",
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Пользователь {user_id} отправил аудио/голос")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик изображений"""
        user_id = update.effective_user.id
        
        # Проверка доступа
        access_info = await self.db.check_user_access(user_id)
        
        if not access_info.get('has_access'):
            if not access_info.get('key_type'):
                # Ключ не активирован вообще
                await update.message.reply_text(
                    "🔒 Для использования бота необходимо активировать ключ доступа.\n\n"
                    "Используйте команду /activate и введите ваш ключ.",
                    parse_mode=ParseMode.HTML
                )
            else:
                # Лимит исчерпан
                await update.message.reply_text(
                    f"❌ {access_info['message']}\n\n"
                    "Вы исчерпали лимит анализов фотографий.\n\n"
                    "💎 <b>Для покупки нового ключа:</b>\n"
                    "Обратитесь к @unrealartur\n\n"
                    "📞 <b>Поддержка:</b> @unrealartur\n\n"
                    "<i>Made by AI LAB</i>",
                    parse_mode=ParseMode.HTML
                )
            return
        
        # Проверка rate limiting
        if not await self.db.check_rate_limit(user_id, minutes=1, max_requests=config.MAX_REQUESTS_PER_MINUTE):
            await update.message.reply_text(
                "⏰ Слишком много запросов! Пожалуйста, подожди немного.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Логирование запроса
        await self.db.log_request(user_id, "image")
        
        # Отправка сообщения о обработке
        processing_msg = await update.message.reply_text("📸 Анализирую фото...")
        
        try:
            # Получение фото (берём наибольшее качество)
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            # Загрузка изображения
            image_bytes = BytesIO()
            await file.download_to_memory(image_bytes)
            image_bytes.seek(0)
            
            # Получение дополнительного текста (caption)
            caption = update.message.caption
            
            # Анализ изображения через OpenAI Vision
            result = await self.openai_service.analyze_food_image(
                image_bytes.read(),
                user_text=caption
            )
            
            # Получение статистики за день
            daily_stats = await self.db.get_daily_calories(user_id)
            daily_limit = await self.db.get_user_daily_limit(user_id)
            
            # Сохранение в БД
            await self.db.add_meal(
                user_id=user_id,
                product_name=result.get('product_name', 'Продукт с фото'),
                weight=result.get('weight'),
                calories=result.get('calories', 0),
                protein=result.get('protein', 0),
                fat=result.get('fat', 0),
                carbs=result.get('carbs', 0),
                image_processed=True
            )
            
            # Логирование использования ключа (для ограниченных ключей)
            await self.db.log_key_usage(user_id, usage_type='image')
            
            # Форматирование и отправка ответа
            response = self.openai_service.format_response(
                result,
                include_daily_stats=True,
                daily_total=daily_stats['total_calories'],
                daily_limit=daily_limit
            )
            
            # Добавление информации об оставшихся анализах
            access_info = await self.db.check_user_access(user_id)
            if access_info.get('key_type') == 'limited' and access_info.get('images_left') is not None:
                images_left = access_info['images_left']
                response += f"\n\n📊 Осталось анализов изображений: {images_left}"
                if images_left <= 5:
                    response += " ⚠️"
            
            await processing_msg.edit_text(response, parse_mode=ParseMode.HTML)
            logger.info(f"Обработано фото от пользователя {user_id}: {result.get('product_name', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке фото: {e}")
            await processing_msg.edit_text(
                "❌ Не удалось обработать изображение. "
                "Пожалуйста, попробуйте:\n"
                "• Сделать фото при хорошем освещении\n"
                "• Убедиться, что продукт хорошо виден\n"
                "• Добавить описание к фото\n\n"
                "Или просто опишите блюдо текстом!",
                parse_mode=ParseMode.HTML
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😔 Произошла ошибка при обработке запроса. "
                "Попробуйте позже или используйте /help для помощи.",
                parse_mode=ParseMode.HTML
            )
    
    async def post_init(self, application: Application):
        """Инициализация после запуска приложения"""
        await self.db.init_db()
        logger.info("Бот инициализирован и готов к работе")
    
    async def token_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /token_stats - показывает статистику использования токенов"""
        user_id = update.effective_user.id
        
        # Проверка доступа
        access_info = await self.db.check_user_access(user_id)
        if not access_info.get('has_access') and not access_info.get('key_type'):
            await update.message.reply_text(
                "🔒 Для просмотра статистики необходимо активировать ключ доступа.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Получаем статистику токенов
        stats = self.openai_service.get_token_stats()
        
        stats_message = f"""📊 <b>Статистика использования токенов</b>

🔥 <b>Общее количество токенов:</b> {stats['total_tokens_used']:,}
💰 <b>Общая стоимость:</b> ${stats['total_cost']:.6f} ({stats['total_cost_rub']:.2f} ₽)
📈 <b>Запросов выполнено:</b> {stats['requests_count']}
📊 <b>Среднее токенов на запрос:</b> {stats['avg_tokens_per_request']:.1f}
💵 <b>Средняя стоимость запроса:</b> ${stats['avg_cost_per_request']:.6f} ({stats['avg_cost_per_request_rub']:.2f} ₽)

<b>Примечание:</b> Статистика сбрасывается при перезапуске бота."""
        
        await update.message.reply_text(stats_message, parse_mode=ParseMode.HTML)
    
    def run(self):
        """Запуск бота"""
        if not config.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN не установлен!")
            return
        
        if not config.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY не установлен!")
            return
        
        # Создание приложения
        application = (
            Application.builder()
            .token(config.TELEGRAM_BOT_TOKEN)
            .post_init(self.post_init)
            .build()
        )
        
        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("payment", self.payment_command))  # Команда оплаты
        application.add_handler(CommandHandler("activate", self.activate_command))
        application.add_handler(CommandHandler("key_info", self.key_info_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("history", self.history_command))
        application.add_handler(CommandHandler("reset", self.reset_command))
        application.add_handler(CommandHandler("token_stats", self.token_stats_command))  # Команда статистики токенов
        
        # Регистрация обработчиков сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice_audio))
        
        # Регистрация обработчика callback'ов для кнопок оплаты
        from telegram.ext import CallbackQueryHandler
        application.add_handler(CallbackQueryHandler(self.payment_callback_handler))
        
        # Регистрация обработчика ошибок
        application.add_error_handler(self.error_handler)
        
        # Запуск бота
        logger.info("Запуск бота...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Главная функция"""
    bot = CalorieCounterBot()
    bot.run()


if __name__ == "__main__":
    main()
