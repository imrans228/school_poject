from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import os
import re

# ==========================================
# 1. ИНИЦИАЛИЗАЦИЯ И ДАННЫЕ (УПРОЩЕНО ДЛЯ RENDER)
# ==========================================

app = Flask(__name__)

# Чтение данных прямо в app.py (чтобы избежать проблем с импортом data.py на хостинге)
CITIES = [
    'Все города', 'Алматы', 'Астана', 'Шымкент', 'Караганда', 
    'Актобе', 'Атырау', 'Екибастуз', 'Кызылорда', 'Тараз', 
    'Костанай', 'Павлодар'
]

universities = []
try:
    # Пытаемся читать JSON файл (он должен быть в корне проекта)
    with open('universities.json', 'r', encoding='utf-8') as f:
        universities = json.load(f)
        print(f"✅ Успешно загружено {len(universities)} ВУЗов из universities.json.")
except Exception as e:
    print(f"❌ ОШИБКА: Не удалось загрузить universities.json. Приложение будет работать без данных. {e}")


# ==========================================
# 2. НАСТРОЙКА GEMINI (Для Render)
# ==========================================

# Ключ берется ИСКЛЮЧИТЕЛЬНО из переменной окружения, настроенной на Render
API_KEY = os.environ.get("AIzaSyAeZdXgu7c4vwco8FcW6fUVs3Fh0xfeMoA") 
MODEL_NAME = 'gemini-2.5-flash'

if not API_KEY:
    print("❌ AI: Переменная окружения 'API_KEY' не найдена. AI-ассистент отключен.")
    model = None
else:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        print(f"🤖 AI: Модель {MODEL_NAME} успешно настроена и готова к работе.")
    except Exception as e:
        print(f"❌ AI: Ошибка настройки Google GenAI. Проверьте правильность ключа: {e}")
        model = None


# ==========================================
# 3. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ RAG и АНАЛИЗА БАЛЛОВ
# ==========================================

def get_relevant_universities(query: str, limit: int = 5):
    """
    Ищет в базе данных ВУЗы, релевантные запросу.
    """
    query_lower = query.lower()
    relevant_unis = []
    
    # 1. Попытка извлечь балл из запроса
    score = None
    score_match = re.search(r'(\d+)\s*(балл|ент|ұбт)', query_lower)
    if score_match:
        try:
            score = int(score_match.group(1))
        except ValueError:
            score = None
    
    # 2. Основной поиск и фильтрация
    for uni in universities:
        # Если балл указан, фильтруем по нему
        if score is not None:
            min_score = uni.get('min_unt_score', 0)
            if min_score > 0 and min_score <= score:
                relevant_unis.append(uni)
            continue
        
        # Если балл не указан, ищем по ключевым словам
        uni_text = f"{uni.get('name', '')} {uni.get('fullName', '')} {uni.get('city', '')} {uni.get('direction', '')} {uni.get('desc', '')}".lower()
        if any(keyword in uni_text for keyword in query_lower.split()):
            relevant_unis.append(uni)

    # 3. Если релевантных нет, берем 5 первых ВУЗов
    if not relevant_unis:
        return universities[:limit]
        
    return relevant_unis[:limit] # Ограничиваем количество


# ==========================================
# 4. РОУТЫ ПРИЛОЖЕНИЯ
# ==========================================

@app.route('/')
def home():
    # Передаем университеты на главную страницу (если нужно)
    return render_template('index.html', unis=universities) 

@app.route('/catalog')
def catalog():
    search = request.args.get('search', '').lower()
    city = request.args.get('city', '')
    
    result = universities
    
    if search:
        result = [u for u in result if search in u.get('name', '').lower() or search in u.get('fullName', '').lower()]
    
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
        return jsonify({'response': '⚠️ AI-ассистент не работает. Установите переменную окружения API_KEY на Render.'})
    
    try:
        msg = request.json.get('message', '')
        
        # --- ФИЛЬТРАЦИЯ ДАННЫХ ДЛЯ AI (RAG) ---
        relevant_unis = get_relevant_universities(msg)
        
        # Передаем только нужные поля, чтобы не превышать лимит токенов
        uni_data_lite = [{'id': u.get('id'), 'name': u.get('name'), 'city': u.get('city'), 'direction': u.get('direction'), 'tuition': u.get('tuition'), 'min_unt_score': u.get('min_unt_score')} for u in relevant_unis]
        
        uni_data_for_context = json.dumps(uni_data_lite, ensure_ascii=False, indent=2)

        # --- СИСТЕМНАЯ ИНСТРУКЦИЯ ДЛЯ AI ---
        context = f"""
        Ты — UniFinder KZ, умный ассистент по подбору университетов Казахстана. 
        Твоя главная задача:
        1. Если пользователь указывает балл ЕНТ, рекомендуй только те ВУЗы, где 'min_unt_score' меньше или равен этому баллу.
        2. Подбирать ВУЗы, основываясь на других параметрах ('city', 'direction', 'tuition').
        3. Отвечай дружелюбно, кратко и по существу, используя предоставленную базу. Не придумывай информацию.
        
        База данных релевантных университетов (JSON, всего {len(uni_data_lite)} ВУЗов):
        {uni_data_for_context}
        
        ---
        Запрос пользователя:
        """
        
        response = model.generate_content([context, msg])
        
        return jsonify({'response': response.text})

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА В API ЧАТА: {e}", file=sys.stderr)
        return jsonify({'response': '⚠️ Произошла ошибка на сервере при обработке запроса AI. (Проверьте логи Render!)'})
