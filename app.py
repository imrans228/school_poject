from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import os
import re

app = Flask(__name__)

# --- ЗАГРУЗКА БАЗЫ (ВСТРОЕННАЯ ЗАЩИТА) ---
universities = []
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'universities.json'), 'r', encoding='utf-8') as f:
        universities = json.load(f)
except:
    universities = []

CITIES = ['Все города', 'Алматы', 'Астана', 'Шымкент']

# --- ФУНКЦИЯ ПОИСКА ---
def get_relevant_universities(query):
    # Упрощенная логика поиска для теста
    return universities[:5]

# --- НАСТРОЙКА AI (САМАЯ ПРОСТАЯ) ---
API_KEY = os.environ.get("API_KEY") # Берем ТОЛЬКО из Render
model = None

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ AI подключен!")
    except Exception as e:
        print(f"❌ Ошибка AI: {e}")
else:
    print("⚠️ API_KEY не найден!")

# --- РОУТЫ ---
@app.route('/')
def home(): return render_template('index.html', unis=universities)

@app.route('/catalog')
def catalog(): return render_template('catalog.html', unis=universities, cities=CITIES)

@app.route('/detail/<uni_id>')
def detail(uni_id):
    uni = next((u for u in universities if u.get('id') == uni_id), None)
    return render_template('detail.html', uni=uni) if uni else ("Нет вуза", 404)

@app.route('/ai')
def ai_page(): return render_template('ai.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not model:
        return jsonify({'response': 'Ошибка: Ключ API не найден или неверен.'})
    try:
        msg = request.json.get('message', '')
        response = model.generate_content(f"Ответь кратко про вузы Казахстана. Вопрос: {msg}")
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': f"Ошибка Google: {str(e)}"})
