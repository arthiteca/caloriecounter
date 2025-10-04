import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TokenTracker:
    """Класс для отслеживания расхода токенов и стоимости OpenAI API"""
    
    def __init__(self):
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.requests_count = 0
    
    def track_usage(self, response) -> Dict:
        """
        Отслеживает использование токенов и стоимость из ответа OpenAI API
        
        Args:
            response: Ответ от OpenAI API
            
        Returns:
            Dict с информацией о токенах и стоимости
        """
        try:
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            # Получаем стоимость из ответа (если доступна)
            # В GPT-4o стоимость может быть в response.usage.total_cost
            if hasattr(usage, 'total_cost') and usage.total_cost is not None:
                request_cost = usage.total_cost
            else:
                # Если стоимость не предоставляется API, рассчитываем приблизительно
                # Цены для GPT-4o
                input_cost = (prompt_tokens / 1000) * 0.005  # $0.005 за 1K входных токенов
                output_cost = (completion_tokens / 1000) * 0.015  # $0.015 за 1K выходных токенов
                request_cost = input_cost + output_cost
            
            # Обновляем счетчики
            self.total_tokens_used += total_tokens
            self.total_cost += request_cost
            self.requests_count += 1
            
            # Логируем информацию
            cost_rub = request_cost * 100.0  # Курс 100 рублей за доллар
            logger.info(f"OpenAI запрос - Токены: {prompt_tokens} входных + {completion_tokens} выходных = {total_tokens} всего. Стоимость: ${request_cost:.6f} ({cost_rub:.2f} ₽)")
            
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "request_cost": request_cost,
                "cost_source": "api" if hasattr(usage, 'total_cost') and usage.total_cost is not None else "calculated"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при отслеживании токенов: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """Получить статистику использования токенов"""
        # Курс доллара к рублю
        USD_TO_RUB_RATE = 100.0
        
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "total_cost_rub": self.total_cost * USD_TO_RUB_RATE,
            "requests_count": self.requests_count,
            "avg_tokens_per_request": self.total_tokens_used / self.requests_count if self.requests_count > 0 else 0,
            "avg_cost_per_request": self.total_cost / self.requests_count if self.requests_count > 0 else 0,
            "avg_cost_per_request_rub": (self.total_cost / self.requests_count * USD_TO_RUB_RATE) if self.requests_count > 0 else 0
        }
    
    def reset(self):
        """Сбросить счетчики"""
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.requests_count = 0
        logger.info("Счетчики токенов сброшены")
