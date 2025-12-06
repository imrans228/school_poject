import google.generativeai as genai
import os

# --- НАСТРОЙКИ ---
API_KEY = "AIzaSyCZ_C9WIYSMtPkdsZJpXd-IR_c0DjcuPIQ"

# ИЗМЕНЕНИЕ ЗДЕСЬ: Используем модель из вашего списка диагностики
# gemini-2.5-flash — это быстрая и актуальная версия для вашего доступа
MODEL_NAME = 'gemini-2.5-flash' 

def main():
    if API_KEY == "ВСТАВЬТЕ_ВАШ_API_KEY_СЮДА":
        print("❌ Ошибка: Вы не вставили API ключ.")
        return

    genai.configure(api_key=API_KEY)

    try:
        print(f"🤖 Подключение к модели: {MODEL_NAME}...")
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = "Привет! Напиши одну фразу о будущем ИИ."
        print(f"📤 Отправляю запрос: '{prompt}'\n")
        
        response = model.generate_content(prompt)
        
        print("✅ УСПЕХ! Ответ модели:")
        print("-" * 30)
        print(response.text)
        print("-" * 30)

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")

if __name__ == "__main__":
    main()
