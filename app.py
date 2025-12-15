from flask import Flask, render_template, request, jsonify
import json
import os
import sys
import re

# ==========================================
# 1. ИНИЦИАЛИЗАЦИЯ
# ==========================================
app = Flask(__name__)

# ==========================================
# 2. ЗАГРУЗКА ДАННЫХ (Безопасная)
# ==========================================
CITIES = [
    'Все города', 'Алматы', 'Астана', 'Шымкент', 'Караганда', 
    'Актобе', 'Атырау', 'Екибастуз', 'Кызылорда', 'Тараз', 
    'Костанай', 'Павлодар'
]

# Пытаемся загрузить JSON, если не выйдет — используем пустой список, чтобы сайт не упал
universities = []
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'universities.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        universities = json.load(f)
        print(f"✅ Успешно загружено {len(universities)} ВУЗов.")
except Exception as e:
    print(f"⚠️ Ошибка загрузки universities.json: {e}")
    # Данные для теста, если файл не найден
    universities = []

# ==========================================
# 3. НАСТРОЙКА AI (С защитой от сбоев)
# ==========================================
API_KEY = os.environ.get("AIzaSyAeZdXgu7c4vwco8FcW6fUVs3Fh0xfeMoA") # Читаем ТОЛЬКО из Render
MODEL_NAME = 'gemini-2.5-flash'
model = None

# Безопасный импорт библиотеки
try:
    import google.generativeai as genai
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        print("✅ AI подключен.")
    else:
        print("⚠️ API_KEY не найден в переменных окружения.")
except ImportError:
    print("❌ Библиотека google-generativeai не установлена.")
except Exception as e:
    print(f"❌ Ошибка настройки AI: {e}")

# ==========================================
# 4. ФУНКЦИЯ ПОИСКА (Которой не хватало!)
# ==========================================
def get_relevant_universities(query: str, limit: int = 5):
    """Ищет вузы по запросу или баллам."""
    query_lower = query.lower()
    relevant = []
    
    # Поиск балла в тексте (например "у меня 100 баллов")
    score_match = re.search(r'(\d+)', query_lower)
    score = int(score_match.group(1)) if score_match else None
    
    for uni in universities:
        # Если найден балл - фильтруем по проходному баллу
        if score:
            if uni.get('min_unt_score', 0) <= score and uni.get('min_unt_score', 0) > 0:
                relevant.append(uni)
        # Иначе ищем по словам
        else:
            text = f"{uni.get('name')} {uni.get('city')} {uni.get('direction')}".lower()
            if any(word in text for word in query_lower.split()):
                relevant.append(uni)
                
    return relevant[:limit] if relevant else universities[:3]

# ==========================================
# 5. МАРШРУТЫ
# ==========================================
@app.route('/')
def home():
    return render_template('index.html', unis=universities)

@app.route('/catalog')
def catalog():
    search = request.args.get('search', '').lower()
    city = request.args.get('city', '')
    result = universities
    
    if search:
        result = [u for u in result if search in u.get('name', '').lower()]
    if city and city != "Все города":
        result = [u for u in result if u.get('city') == city]

    return render_template('catalog.html', unis=result, cities=CITIES)

@app.route('/detail/<uni_id>')
def detail(uni_id):
    uni = next((u for u in universities if u.get('id') == uni_id), None)
    if not uni: return "Вуз не найден", 404
    return render_template('detail.html', uni=uni)

@app.route('/compare')
def compare():
    ids = request.args.get('ids', '').split(',')
    selected = [u for u in universities if u.get('id') in ids]
    return render_template('compare.html', unis=selected)

@app.route('/ai')
def ai_page():
    return render_template('ai.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not model:
        return jsonify({'response': '⚠️ AI не работает (проверьте API ключ на сервере).'})
    
    try:
        msg = request.json.get('message', '')
        
        # 1. Находим релевантные вузы
        relevant = get_relevant_universities(msg)
        
        # 2. Формируем контекст (только важные данные, чтобы не перегружать)
        context_data = [
            {'name': u['name'], 'city': u['city'], 'score': u.get('min_unt_score'), 'tuition': u.get('tuition')} 
            for u in relevant
        ]
        
        system_prompt = f"""
        Ты консультант UniFinder. Отвечай кратко.
        Если спрашивают про баллы, используй поле 'score' (мин. балл).
        Данные о вузах: {json.dumps(context_data, ensure_ascii=False)}
        Вопрос: {msg}
        """
        
        response = model.generate_content(system_prompt)
        return jsonify({'response': response.text})
        
    except Exception as e:
        print(f"Ошибка AI: {e}")
        return jsonify({'response': 'Произошла ошибка при генерации ответа.'})
