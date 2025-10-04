# Настройка СБП Payment Service

## Быстрая настройка

1. **Скопируйте файл конфигурации:**
   ```bash
   # Из корня проекта
   cp ../env_example.txt ../.env
   ```

2. **Отредактируйте `.env` файл в корне проекта:**
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token
   
   # OpenAI API Configuration
   OPENAI_API_KEY=ваш_openai_api_key
   
   # СБП Configuration
   SBP_MERCHANT_ID=ваш_merchant_id
   SBP_SECRET_KEY=ваш_secret_key
   SBP_API_URL=https://sbp.nspk.ru/api/
   
   # Payment Server Configuration
   SERVER_HOST=0.0.0.0
   SERVER_PORT=8000
   SERVER_IP=188.253.16.50
   
   # Logging
   LOG_LEVEL=INFO
   ```

3. **Установите зависимости:**
   ```bash
   # Из корня проекта
   pip install -r ../requirements.txt
   ```

4. **Запустите сервер:**
   ```bash
   python payment_server.py
   ```

## Получение данных СБП

1. **Обратитесь в банк** для подключения СБП
2. **Получите от банка:**
   - Merchant ID
   - Secret Key
   - API URL (если отличается от стандартного)

3. **Обновите `.env` файл в корне проекта** с реальными данными

## Проверка работы

- **Главная страница:** http://SERVER_IP:SERVER_PORT
- **Webhook:** http://SERVER_IP:SERVER_PORT/webhook/sbp
- **Проверка здоровья:** http://SERVER_IP:SERVER_PORT/health

## Интеграция с ботом

Сервис автоматически использует конфигурацию из основного проекта через общий `.env` файл.
