import google.generativeai as genai

# === ВСТАВЬТЕ СВОЙ КЛЮЧ СЮДА ===
MY_KEY = "AIzaSyCZ_C9WIYSMtPkdsZJpXd-IR_c0DjcuPIQ" 

print(f"🔑 Проверяем ключ: {MY_KEY[:10]}...")

try:
    genai.configure(api_key=MY_KEY)
    
    # 1. Проверяем доступные модели
    print("\n📡 Запрашиваем список доступных моделей...")
    models = list(genai.list_models())
    found_flash = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            if 'flash' in m.name:
                found_flash = True

    # 2. Пробуем отправить запрос
    print("\n💬 Пробуем отправить 'Привет'...")
    
    # Если Flash найдена в списке, используем её, иначе Pro
    model_name = 'gemini-1.5-flash' if found_flash else 'gemini-pro'
    print(f"👉 Используем модель: {model_name}")
    
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Привет! Ты работаешь?")
    
    print(f"\n✅ УСПЕХ! Ответ AI: {response.text}")

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
