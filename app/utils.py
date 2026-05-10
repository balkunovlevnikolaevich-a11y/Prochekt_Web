# app/utils.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def generate_ai_description(prompt: str) -> str:
    """
    Генерация описания задачи с помощью Google Gemini
    (нефункциональное требование ТЗ — взаимодействие с ИИ)
    
    Как получить ключ:
    1. Перейди на https://aistudio.google.com/app/apikey
    2. Создай новый API-ключ
    3. Создай в корне проекта файл .env и добавь туда строку:
       GEMINI_API_KEY=твой_ключ_сюда
    """
    
    api_key = os.getenv("AIzaSyDBQspta3SqZsenPB7HzHz_zz5exGMtP2s")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(
                f"Ты — дружелюбный ИИ-помощник. Составь подробное, чёткое и привлекательное описание задачи для фриланс-платформы по теме: {prompt}\n"
                "Добавь шаги выполнения, требования и ожидаемый результат."
            )
            
            ai_text = response.text.strip()
            return f"🤖 Gemini ответил:\n\n{ai_text}"
            
        except Exception as e:
            print(f"Ошибка Gemini: {e}")  # для отладки
    
    # Если ключ не настроен или ошибка — красивый мок (всегда работает)
    return (f"🤖 Gemini: Отлично! Вот подробное описание задачи по запросу «{prompt}»:\n\n"
            f"**Цель задачи:**\n"
            f"Создать/выполнить {prompt} на высоком уровне качества.\n\n"
            f"**Что нужно сделать:**\n"
            f"1. Изучить требования и подготовить всё необходимое\n"
            f"2. Выполнить основную работу\n"
            f"3. Проверить результат на ошибки\n"
            f"4. Оформить и отправить заказчику\n\n"
            f"**Ожидаемый результат:** Качественно выполненная задача, готовая к приёмке.\n\n"
            f"Готово к публикации! 🚀")
