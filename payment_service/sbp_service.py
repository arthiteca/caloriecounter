import asyncio
import aiohttp
import qrcode
import json
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class SBPService:
    """Сервис для работы с СБП API"""
    
    def __init__(self, merchant_id: str, secret_key: str, api_url: str = "https://sbp.nspk.ru/api/"):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.api_url = api_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _generate_signature(self, data: dict, timestamp: str) -> str:
        """Генерация подписи для запроса согласно документации СБП"""
        # Сортируем данные по ключам
        sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Создаем строку для подписи
        sign_string = f"{sorted_data}{timestamp}{self.secret_key}"
        
        # Генерируем HMAC-SHA256 подпись
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def create_payment_link(self, user_id: int, amount: float, description: str) -> Dict:
        """Создание платежной ссылки СБП"""
        payment_id = str(uuid.uuid4())
        timestamp = str(int(datetime.now().timestamp()))
        
        # Данные для создания платежа
        payment_data = {
            "merchant_id": self.merchant_id,
            "payment_id": payment_id,
            "amount": amount,
            "currency": "RUB",
            "description": description,
            "return_url": f"https://t.me/your_bot?start=payment_{payment_id}",
            "user_id": user_id,
            "timestamp": timestamp
        }
        
        # Добавляем подпись
        payment_data["signature"] = self._generate_signature(payment_data, timestamp)
        
        try:
            async with self.session.post(
                f"{self.api_url}v1/payments",
                json=payment_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Timestamp": timestamp
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Генерируем QR-код для платежной ссылки
                    payment_url = result.get("payment_url", "")
                    qr_code = self._generate_qr_code(payment_url)
                    
                    return {
                        "success": True,
                        "payment_id": payment_id,
                        "payment_url": payment_url,
                        "qr_code": qr_code,
                        "amount": amount,
                        "status": "pending"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get("message", "Ошибка создания платежа")
                    }
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {e}")
            return {
                "success": False,
                "error": "Ошибка соединения с СБП"
            }
    
    def _generate_qr_code(self, data: str) -> str:
        """Генерация QR-кода для платежной ссылки"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Конвертируем в base64 для отправки в Telegram
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    async def check_payment_status(self, payment_id: str) -> Dict:
        """Проверка статуса платежа"""
        timestamp = str(int(datetime.now().timestamp()))
        
        try:
            # Создаем подпись для запроса статуса
            status_data = {
                "merchant_id": self.merchant_id,
                "payment_id": payment_id
            }
            signature = self._generate_signature(status_data, timestamp)
            
            async with self.session.get(
                f"{self.api_url}v1/payments/{payment_id}",
                headers={
                    "X-Timestamp": timestamp,
                    "X-Signature": signature
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "status": result.get("status"),
                        "amount": result.get("amount"),
                        "paid_at": result.get("paid_at")
                    }
                else:
                    return {
                        "success": False,
                        "error": "Ошибка проверки статуса"
                    }
        except Exception as e:
            logger.error(f"Ошибка проверки статуса платежа: {e}")
            return {
                "success": False,
                "error": "Ошибка соединения"
            }
    
    async def process_webhook(self, webhook_data: dict) -> Dict:
        """Обработка webhook от СБП"""
        # Проверяем подпись webhook
        received_signature = webhook_data.pop("signature", "")
        timestamp = webhook_data.get("timestamp", "")
        
        expected_signature = self._generate_signature(webhook_data, timestamp)
        
        if received_signature != expected_signature:
            return {"success": False, "error": "Неверная подпись webhook"}
        
        payment_id = webhook_data.get("payment_id")
        status = webhook_data.get("status")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": status,
            "amount": webhook_data.get("amount"),
            "paid_at": webhook_data.get("paid_at")
        }
