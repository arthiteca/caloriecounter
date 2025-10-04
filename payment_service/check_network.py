import requests
import socket
import subprocess
import sys
from flask import Flask
import threading
import time
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SERVER_IP, SERVER_PORT, WEBHOOK_URL

def check_external_ip():
    """Проверка внешнего IP адреса"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        external_ip = response.text.strip()
        print(f"🌐 Ваш внешний IP: {external_ip}")
        
        if external_ip == SERVER_IP:
            print("✅ Это ваш IP - отлично!")
            return True, external_ip
        else:
            print(f"⚠️ IP отличается от указанного ({SERVER_IP})")
            return True, external_ip
    except Exception as e:
        print(f"❌ Ошибка получения IP: {e}")
        return False, None

def check_port_availability(port=None):
    """Проверка доступности порта"""
    if port is None:
        port = SERVER_PORT
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"❌ Порт {port} уже занят")
            return False
        else:
            print(f"✅ Порт {port} свободен")
            return True
    except Exception as e:
        print(f"❌ Ошибка проверки порта: {e}")
        return False

def start_test_server(port=None):
    """Запуск тестового сервера"""
    if port is None:
        port = SERVER_PORT
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Тестовый сервер СБП</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>✅ Сервер СБП работает!</h1>
            <p>Ваш сервер готов для приема webhook'ов от СБП</p>
            <p>IP: {SERVER_IP}</p>
            <p>Порт: {port}</p>
            <p>Webhook URL: {WEBHOOK_URL}</p>
        </body>
        </html>
        """.format(SERVER_IP, port, WEBHOOK_URL)
    
    @app.route('/webhook/sbp', methods=['POST', 'GET'])
    def webhook_sbp():
        if request.method == 'POST':
            data = request.get_json()
            print(f"📨 Получен webhook от СБП: {data}")
            return {"status": "ok", "message": "Webhook получен"}
        else:
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Webhook СБП</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>🔗 Webhook СБП готов!</h1>
                <p>Этот endpoint готов для получения уведомлений от СБП</p>
                <p>URL: {WEBHOOK_URL}</p>
            </body>
            </html>
            """.format(WEBHOOK_URL)
    
    print(f"🚀 Запуск тестового сервера на порту {port}...")
    print(f"📱 Локальный адрес: http://localhost:{port}")
    print(f"🌐 Внешний адрес: http://{SERVER_IP}:{port}")
    print(f"🔗 Webhook URL: {WEBHOOK_URL}")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    app.run(host='0.0.0.0', port=port, debug=False)

def test_external_access(port=None):
    """Тест доступности сервера извне"""
    if port is None:
        port = SERVER_PORT
    print(f"\n🔍 Тестирование доступности {SERVER_IP}:{port}...")
    
    try:
        response = requests.get(f'http://{SERVER_IP}:{port}', timeout=10)
        if response.status_code == 200:
            print("✅ Сервер доступен из интернета!")
            return True
        else:
            print(f"❌ Сервер недоступен (код: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Сервер недоступен из интернета: {e}")
        print("💡 Возможные причины:")
        print("   - Файрвол блокирует порт")
        print("   - Роутер не настроен на проброс портов")
        print("   - Провайдер блокирует входящие соединения")
        return False

def main():
    print("🔍 Проверка сетевых настроек для СБП")
    print("=" * 50)
    
    # 1. Проверяем IP
    is_white_ip, external_ip = check_external_ip()
    
    # 2. Проверяем доступность порта
    port = SERVER_PORT
    if not check_port_availability(port):
        port = SERVER_PORT + 1
        if not check_port_availability(port):
            print("❌ Нет свободных портов")
            return
    
    print(f"\n🎯 Ваш webhook URL для СБП:")
    print(f"   {WEBHOOK_URL}")
    
    print(f"\n📋 Что нужно сделать:")
    print(f"1. Запустить сервер: python payment_server.py")
    print(f"2. Проверить доступность извне")
    print(f"3. Настроить СБП с этим URL")
    
    # Запускаем тестовый сервер
    try:
        start_test_server(port)
    except KeyboardInterrupt:
        print("\n⏹️  Сервер остановлен")

if __name__ == "__main__":
    main()
