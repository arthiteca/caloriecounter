import openai
import base64
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)


class OpenAIService:
    """Класс для работы с OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", vision_model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.vision_model = vision_model
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    async def analyze_text_food(self, text: str) -> Dict:
        """
        Анализ текстового описания продукта/блюда
        
        Args:
            text: Описание продукта от пользователя
            
        Returns:
            Dict с информацией о калориях и БЖУ
        """
        try:
            system_prompt = """Ты - профессиональный диетолог и нутрициолог. 
Твоя задача - анализировать описания продуктов и блюд, предоставляя точную информацию о калориях и БЖУ.
Отвечай ТОЛЬКО в формате JSON со следующей структурой:
{
    "product_name": "название продукта",
    "weight": вес в граммах (число),
    "calories": калории (число),
    "protein": белки в граммах (число),
    "fat": жиры в граммах (число),
    "carbs": углеводы в граммах (число),
    "comparison": "сравнение с другими продуктами",
    "recommendations": "рекомендации по употреблению",
    "benefits": "польза продукта",
    "warnings": "предупреждения (если есть)"
}

Если вес не указан, используй стандартную порцию. Будь точным в расчетах."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Проанализируй этот продукт/блюдо: {text}"}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Анализ текста выполнен: {result.get('product_name', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {e}")
            raise
    
    async def analyze_food_image(self, image_bytes: bytes, user_text: Optional[str] = None) -> Dict:
        """
        Анализ изображения продукта/блюда с использованием Vision API
        
        Args:
            image_bytes: Байты изображения
            user_text: Дополнительный текст от пользователя (опционально)
            
        Returns:
            Dict с информацией о калориях и БЖУ
        """
        try:
            # Конвертируем изображение в base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            system_prompt = """Ты - профессиональный диетолог и нутрициолог с экспертизой в визуальной оценке продуктов.
Твоя задача - анализировать изображения продуктов и блюд, оценивая их состав, вес и пищевую ценность.

Отвечай ТОЛЬКО в формате JSON со следующей структурой:
{
    "product_name": "название продукта/блюда",
    "weight": примерный вес в граммах (число),
    "calories": калории (число),
    "protein": белки в граммах (число),
    "fat": жиры в граммах (число),
    "carbs": углеводы в граммах (число),
    "comparison": "сравнение с другими продуктами (например: эквивалентно 2 яблокам)",
    "recommendations": "рекомендации по употреблению (время дня, с чем сочетается)",
    "benefits": "польза продукта",
    "warnings": "предупреждения о высокой калорийности, сахаре и т.д.",
    "quality_warning": "предупреждение если фото плохого качества или продукт не распознан"
}

Внимательно оцени размер порции и состав блюда. Если изображение нечёткое или темное, укажи это в quality_warning."""

            user_message = "Проанализируй это изображение продукта/блюда и определи его калорийность и БЖУ."
            if user_text:
                user_message += f"\n\nДополнительная информация от пользователя: {user_text}"
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_message},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Анализ изображения выполнен: {result.get('product_name', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе изображения: {e}")
            raise
    
    def format_response(self, data: Dict, include_daily_stats: bool = False, 
                       daily_total: float = 0, daily_limit: int = 2000) -> str:
        """
        Форматирование ответа для пользователя
        
        Args:
            data: Данные от OpenAI
            include_daily_stats: Включить ли статистику за день
            daily_total: Общая калорийность за день
            daily_limit: Дневная норма
            
        Returns:
            Отформатированное текстовое сообщение
        """
        try:
            product_name = data.get('product_name', 'Продукт')
            weight = data.get('weight', 0)
            calories = data.get('calories', 0)
            protein = data.get('protein', 0)
            fat = data.get('fat', 0)
            carbs = data.get('carbs', 0)
            
            # Основная информация
            response = f"🍽 <b>Продукт:</b> {product_name}"
            if weight:
                response += f" ({weight} г)"
            response += f"\n\n📊 <b>Калории:</b> {calories} ккал\n"
            response += f"<b>Белки:</b> {protein} г | <b>Жиры:</b> {fat} г | <b>Углеводы:</b> {carbs} г\n"
            
            # Сравнение
            if data.get('comparison'):
                response += f"\n💡 <b>Сравнение:</b> {data['comparison']}\n"
            
            # Комментарий
            comment_parts = []
            if data.get('benefits'):
                comment_parts.append(data['benefits'])
            if data.get('recommendations'):
                comment_parts.append(data['recommendations'])
            if data.get('warnings'):
                comment_parts.append(f"⚠️ {data['warnings']}")
            
            if comment_parts:
                response += f"\n💬 <b>Комментарий:</b> {' '.join(comment_parts)}"
            
            # Предупреждение о качестве изображения
            if data.get('quality_warning'):
                response += f"\n\n⚠️ {data['quality_warning']}"
            
            # Статистика за день
            if include_daily_stats:
                daily_total += calories
                percentage = (daily_total / daily_limit) * 100
                response += f"\n\n📈 <b>За сегодня:</b> {daily_total:.0f} / {daily_limit} ккал ({percentage:.1f}%)"
                
                if percentage > 100:
                    response += "\n⚠️ Дневная норма превышена!"
                elif percentage > 80:
                    response += "\n⚡ Близко к дневной норме"
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при форматировании ответа: {e}")
            return "❌ Произошла ошибка при обработке данных"
