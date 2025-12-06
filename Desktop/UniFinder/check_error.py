import requests

# --- ВСТАВЬТЕ КЛЮЧ СЮДА ---
API_KEY = "AIzaSyAvO5d12Qqe07oVqNzGV1vS_tjix_Bb5Ho" 

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [{"parts": [{"text": "Hello"}]}]
}

print(f"🔍 Проверяем ключ: {API_KEY[:5]}...{API_KEY[-5:]}")
print(f"Длина ключа: {len(API_KEY)} символов (должно быть 39)")

try:
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    
    print(f"\nСтатус ответа: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ УРА! КЛЮЧ РАБОТАЕТ!")
        print("Ответ:", response.json()['candidates'][0]['content']['parts'][0]['text'])
    else:
        print("❌ ОШИБКА!")
        print("Google говорит:", response.text)

except Exception as e:
    print("Ошибка соединения:", e)
