from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sbp_service import SBPService
from config import (
    SBP_MERCHANT_ID, 
    SBP_SECRET_KEY, 
    SBP_API_URL,
    SERVER_HOST, 
    SERVER_PORT, 
    SERVER_IP,
    WEBHOOK_URL,
    LOG_LEVEL
)

# Настройка логирования
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>СБП Payment Server</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { color: #28a745; font-weight: bold; }
            .info { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>💳 СБП Payment Server</h1>
        <p class="status">✅ Сервер работает</p>
        
        <div class="info">
            <h3>Информация о сервере:</h3>
            <p><strong>IP:</strong> {}</p>
            <p><strong>Порт:</strong> {}</p>
            <p><strong>Webhook URL:</strong> {}</p>
            <p><strong>Статус:</strong> Готов к приему платежей</p>
        </div>
        
        <div class="info">
            <h3>Доступные endpoints:</h3>
            <ul>
                <li><code>GET /</code> - Главная страница</li>
                <li><code>POST /webhook/sbp</code> - Webhook от СБП</li>
                <li><code>GET /webhook/sbp</code> - Информация о webhook</li>
                <li><code>POST /test</code> - Тестирование webhook</li>
            </ul>
        </div>
    </body>
    </html>
    """.format(SERVER_IP, SERVER_PORT, WEBHOOK_URL)

@app.route('/webhook/sbp', methods=['POST', 'GET'])
def webhook_sbp():
    """Обработка webhook от СБП"""
    if request.method == 'GET':
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Webhook СБП</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>🔗 Webhook СБП</h1>
            <p>Endpoint готов для получения уведомлений от СБП</p>
            <p><strong>Метод:</strong> POST</p>
            <p><strong>URL:</strong> {}</p>
            <p><strong>Статус:</strong> ✅ Активен</p>
        </body>
        </html>
        """.format(WEBHOOK_URL)
    
    try:
        # Получаем данные от СБП
        data = request.get_json()
        
        # Логируем получение webhook
        logger.info(f"📨 Получен webhook от СБП: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # Обрабатываем данные платежа
        payment_id = data.get('payment_id', 'unknown')
        status = data.get('status', 'unknown')
        amount = data.get('amount', 0)
        
        # Здесь будет логика обработки платежа
        if status == 'success':
            logger.info(f"✅ Платеж {payment_id} успешен! Сумма: {amount} ₽")
            # TODO: Активировать ключ пользователя
        elif status == 'failed':
            logger.info(f"❌ Платеж {payment_id} не прошел")
        else:
            logger.info(f"⏳ Платеж {payment_id} в статусе: {status}")
        
        # Отвечаем СБП
        response = {
            "status": "ok",
            "message": "Webhook получен",
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test', methods=['POST'])
def test_webhook():
    """Тестирование webhook"""
    test_data = {
        "payment_id": "test_12345",
        "status": "success",
        "amount": 100.0,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info("🧪 Тестовый webhook отправлен")
    return jsonify(test_data)

@app.route('/health')
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SBP Payment Server"
    })

if __name__ == '__main__':
    print("🚀 Запуск СБП сервера...")
    print(f"🌐 Адрес: http://{SERVER_IP}:{SERVER_PORT}")
    print(f"🔗 Webhook: {WEBHOOK_URL}")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)
