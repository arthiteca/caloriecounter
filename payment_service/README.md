# СБП Payment Service

Платежный сервис для интеграции с Системой быстрых платежей (СБП).

## Структура проекта

```
payment_service/
├── __init__.py
├── sbp_service.py      # Основной сервис для работы с СБП API
├── payment_server.py   # Веб-сервер для обработки webhook'ов
├── check_network.py    # Скрипт для проверки сетевых настроек
├── README.md          # Документация
└── SETUP.md           # Инструкция по настройке
```

## Установка

1. Установите зависимости:
```bash
# Из корня проекта
pip install -r ../requirements.txt
```

2. Настройте конфигурацию:
```bash
# Скопируйте файл конфигурации из корня проекта
cp ../env_example.txt .env

# Отредактируйте .env и укажите ваши данные:
# SBP_MERCHANT_ID=ваш_merchant_id
# SBP_SECRET_KEY=ваш_secret_key
# SERVER_IP=ваш_ip_адрес
# SERVER_PORT=ваш_порт
```

## Запуск

### Проверка сети
```bash
python check_network.py
```

### Запуск сервера
```bash
python payment_server.py
```

## Webhook URL

Ваш webhook URL для настройки в СБП (настраивается в config.env):
```
http://SERVER_IP:SERVER_PORT/webhook/sbp
```

## Тестирование

1. Откройте: http://SERVER_IP:SERVER_PORT
2. Проверьте webhook: http://SERVER_IP:SERVER_PORT/webhook/sbp
3. Тестовый запрос: POST http://SERVER_IP:SERVER_PORT/test

## Интеграция с ботом

Сервис готов для интеграции с основным Telegram ботом.

## Настройка СБП

1. Обратитесь в банк для получения:
   - Merchant ID
   - Secret Key
   - API URL

2. Настройте webhook в панели СБП:
   - URL: http://SERVER_IP:SERVER_PORT/webhook/sbp
   - Метод: POST

3. Обновите конфигурацию в `.env`
