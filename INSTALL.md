# Установка и настройка проекта

## Быстрая установка

1. **Клонируйте проект** (если еще не сделали)

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте конфигурацию:**
   ```bash
   # Скопируйте пример конфигурации
   cp env_example.txt .env
   
   # Отредактируйте .env файл с вашими данными
   ```

4. **Запустите бота:**
   ```bash
   python bot.py
   ```

5. **Запустите платежный сервер (опционально):**
   ```bash
   cd payment_service
   python payment_server.py
   ```

## Структура проекта

```
caloriecounter/
├── .env                    # Конфигурация (создать из env_example.txt)
├── env_example.txt         # Пример конфигурации
├── requirements.txt        # Все зависимости проекта
├── config.py              # Основной файл конфигурации
├── bot.py                 # Telegram бот
├── database.py            # База данных
├── openai_service.py      # Сервис OpenAI
├── token_tracker.py       # Отслеживание токенов
├── payment_service/       # Платежный сервис СБП
│   ├── payment_server.py
│   ├── sbp_service.py
│   └── check_network.py
└── INSTALL.md            # Эта инструкция
```

## Настройка .env файла

Отредактируйте `.env` файл и укажите ваши данные:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token

# OpenAI API Configuration
OPENAI_API_KEY=ваш_openai_api_key

# СБП Configuration (для платежей)
SBP_MERCHANT_ID=ваш_merchant_id
SBP_SECRET_KEY=ваш_secret_key
SBP_API_URL=https://sbp.nspk.ru/api/

# Payment Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_IP=ваш_ip_адрес

# Logging
LOG_LEVEL=INFO
```

## Запуск

### Основной бот
```bash
python bot.py
```

### Платежный сервер СБП
```bash
cd payment_service
python payment_server.py
```

### Проверка сети
```bash
cd payment_service
python check_network.py
```

## Получение API ключей

1. **Telegram Bot Token:** @BotFather в Telegram
2. **OpenAI API Key:** https://platform.openai.com/api-keys
3. **СБП данные:** Обратитесь в банк для подключения СБП
