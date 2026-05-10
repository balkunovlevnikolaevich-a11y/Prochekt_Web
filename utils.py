import requests
def generate_task_description(prompt):
    # Mock для демонстрации + реальный вызов Groq/OpenAI
    # Если есть ключ — раскомментируйте
    # response = requests.post("https://api.groq.com/...", json=...)
    return f"ИИ сгенерировал задачу: {prompt} — подробное описание с шагами."
