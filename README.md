# 🥗 Calorie Counter Telegram Bot

Telegram-бот для подсчета калорий с использованием искусственного интеллекта (OpenAI GPT-4 и Vision API). Бот анализирует текстовые описания продуктов и изображения блюд, предоставляя точную информацию о калориях и БЖУ (белках, жирах, углеводах).

## ✨ Возможности

- 📝 **Анализ текстовых описаний** - просто напишите название продукта или блюда
- 📷 **Распознавание еды на фото** - отправьте фото блюда, и бот определит калорийность
- 📊 **Подробный анализ БЖУ** - белки, жиры, углеводы
- 📈 **Отслеживание дневной нормы** - автоматический подсчет потребленных калорий за день
- 💡 **Умные рекомендации** - советы по употреблению, сочетанию продуктов
- 🔄 **История приемов пищи** - сохранение всех записей в базе данных
- ⚡ **Асинхронная обработка** - поддержка множества пользователей одновременно
- 🛡️ **Rate Limiting** - защита от перегрузки API

## 🚀 Быстрый старт

### Требования

- Python 3.9+
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- OpenAI API Key (получить на [platform.openai.com](https://platform.openai.com))

### Установка

1. **Клонируйте репозиторий или создайте проект:**
```bash
git clone <your-repo-url>
cd caloriecounter
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
# Скопируйте пример файла
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Отредактируйте .env файл и добавьте свои токены
```

Файл `.env` должен содержать:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Получение токенов

#### Telegram Bot Token:
1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

#### OpenAI API Key:
1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Перейдите в раздел API Keys
3. Создайте новый ключ
4. Скопируйте ключ в `.env` файл

⚠️ **Важно:** Убедитесь, что у вас есть доступ к GPT-4 с Vision API и достаточный баланс на аккаунте OpenAI.

### Запуск

```bash
python bot.py
```

После запуска бот будет доступен в Telegram. Найдите его по имени, которое вы указали при создании через BotFather.

## 📱 Использование

### Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/stats` - Статистика за текущий день
- `/history` - История приемов пищи за день
- `/reset` - Информация о сбросе данных

### Примеры использования

**Текстовые запросы:**
```
куриная грудка 150г
яблоко 200г
пицца пепперони
овсянка на молоке с бананом
```

**Отправка фото:**
1. Сфотографируйте блюдо
2. Отправьте фото боту
3. Опционально: добавьте подпись с дополнительной информацией

### Формат ответа

```
🍽 Продукт: Куриная грудка (150 г)

📊 Калории: 165 ккал
Белки: 31 г | Жиры: 3,6 г | Углеводы: 0 г

💡 Сравнение: Эквивалентно 15% дневной нормы калорий

💬 Комментарий: Отличный источник белка с низким содержанием жиров. 
Хорошо подходит для обеда или ужина. Рекомендуется сочетать с 
овощами или сложными углеводами.

📈 За сегодня: 165 / 2000 ккал (8.3%)
```

## 🏗️ Архитектура проекта

```
caloriecounter/
├── bot.py              # Основной файл бота с обработчиками
├── config.py           # Конфигурация и настройки
├── database.py         # Работа с базой данных SQLite
├── openai_service.py   # Интеграция с OpenAI API
├── requirements.txt    # Зависимости проекта
├── .env               # Переменные окружения (не в git)
├── .env.example       # Пример файла .env
├── README.md          # Документация
├── bot.log            # Логи работы бота
└── calorie_counter.db # База данных SQLite
```

## 🔧 Конфигурация

Основные настройки находятся в `config.py`:

- `DATABASE_PATH` - путь к базе данных
- `MAX_REQUESTS_PER_MINUTE` - лимит запросов в минуту
- `DEFAULT_DAILY_CALORIES` - дневная норма калорий по умолчанию
- `LOG_LEVEL` - уровень логирования
- `OPENAI_MODEL` - модель GPT для текста
- `OPENAI_VISION_MODEL` - модель GPT с Vision

## 💾 База данных

Бот использует SQLite для хранения:

- **users** - информация о пользователях
- **meals** - история приемов пищи
- **requests_log** - журнал запросов для rate limiting

Данные автоматически группируются по дням, статистика обновляется в реальном времени.

## 🛠️ Технологии

- **python-telegram-bot** - библиотека для работы с Telegram Bot API
- **OpenAI API** - GPT-4 для анализа текста и Vision API для изображений
- **aiosqlite** - асинхронная работа с SQLite
- **asyncio** - асинхронное выполнение операций
- **Pillow** - обработка изображений
- **python-dotenv** - управление переменными окружения

## 🔒 Безопасность

- Токены хранятся в `.env` файле (не добавляется в git)
- Реализован rate limiting для защиты от спама
- Логирование всех операций для аудита
- Обработка ошибок и валидация входных данных

## 📝 Логирование

Все события логируются в файл `bot.log` и консоль:
- Запросы пользователей
- Ответы от OpenAI
- Ошибки и исключения
- Системные события

## ⚠️ Обработка ошибок

Бот обрабатывает:
- Некачественные изображения (размытые, темные)
- Некорректные данные от пользователя
- Ошибки API (OpenAI, Telegram)
- Превышение лимитов запросов
- Проблемы с базой данных

Все ошибки логируются и пользователю отправляется дружелюбное сообщение.

## 🚀 Развертывание в production

### На сервере (Linux)

1. **Установите зависимости:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

2. **Клонируйте проект и настройте:**
```bash
git clone <your-repo>
cd caloriecounter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Создайте systemd service:**
```bash
sudo nano /etc/systemd/system/calorie-bot.service
```

Содержимое:
```ini
[Unit]
Description=Calorie Counter Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/caloriecounter
Environment="PATH=/path/to/caloriecounter/venv/bin"
ExecStart=/path/to/caloriecounter/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Запустите сервис:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable calorie-bot
sudo systemctl start calorie-bot
sudo systemctl status calorie-bot
```

### Docker (опционально)

Создайте `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Запуск:
```bash
docker build -t calorie-bot .
docker run -d --env-file .env --name calorie-bot calorie-bot
```

## 📊 Мониторинг

- Проверяйте `bot.log` для отслеживания работы
- Используйте `systemctl status calorie-bot` для проверки статуса
- Настройте алерты на критические ошибки в логах

## 🤝 Вклад в проект

Если вы хотите улучшить проект:

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - свободное использование в любых целях.

## 💬 Поддержка

Если у вас возникли вопросы или проблемы:
- Создайте Issue в репозитории
- Проверьте логи в `bot.log`
- Убедитесь, что все токены правильно настроены

## 🎯 Roadmap

Планы на будущее:
- [ ] Персональные настройки дневной нормы калорий
- [ ] Экспорт статистики в Excel/PDF
- [ ] Интеграция с фитнес-трекерами
- [ ] Мультиязычная поддержка
- [ ] Web-интерфейс для просмотра статистики
- [ ] Рецепты и планирование питания
- [ ] Барcode scanner для продуктов

---

**Приятного использования! 🥗💪**
