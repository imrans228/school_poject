# test_key.py
import google.generativeai as genai

# ВСТАВЬТЕ СЮДА ВАШ КЛЮЧ
MY_KEY = "AIzaSy..." 

try:
    genai.configure(api_key=MY_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Привет, ты работаешь?")
    print("✅ УСПЕХ! Ответ от AI:", response.text)
except Exception as e:
    print("❌ ОШИБКА КЛЮЧА:", e)
