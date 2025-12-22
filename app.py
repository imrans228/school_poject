from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai
import json
import os
import re

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_school_project' # Нужен для "регистрации"

# --- ЗАГРУЗКА БАЗЫ ---
universities = []
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'universities.json'), 'r', encoding='utf-8') as f:
        universities = json.load(f)
except:
    universities = []

CITIES = ['Все города', 'Алматы', 'Астана', 'Шымкент', 'Караганда', 'Актобе', 'Костанай']

# --- AI НАСТРОЙКА ---
API_KEY = os.environ.get("API_KEY")
model = None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except: pass

# --- ФУНКЦИЯ ПОИСКА ---
def get_relevant_universities(query):
    query = query.lower()
    return [u for u in universities if query in u['name'].lower() or query in u['desc'].lower()][:5]

# --- РОУТЫ ---

@app.route('/')
def home():
    user = session.get('user') # Проверяем, вошел ли человек
    return render_template('index.html', unis=universities, user=user)

@app.route('/catalog')
def catalog():
    # 1. Получаем данные из фильтра
    search = request.args.get('search', '').strip().lower()
    city = request.args.get('city', 'Все города')
    
    filtered_unis = universities

    # 2. Фильтруем по городу
    if city and city != "Все города":
        filtered_unis = [u for u in filtered_unis if u.get('city') == city]

    # 3. Фильтруем по поиску (имя или описание)
    if search:
        filtered_unis = [u for u in filtered_unis if search in u.get('name', '').lower() or search in u.get('fullName', '').lower()]

    user = session.get('user')
    return render_template('catalog.html', unis=filtered_unis, cities=CITIES, current_city=city, user=user)

@app.route('/detail/<uni_id>')
def detail(uni_id):
    uni = next((u for u in universities if u.get('id') == uni_id), None)
    return render_template('detail.html', uni=uni, user=session.get('user'))

@app.route('/compare')
def compare():
    # Получаем список ID из ссылки (например: ?ids=nu,kaznu)
    ids = request.args.get('ids', '').split(',')
    selected = [u for u in universities if u.get('id') in ids]
    return render_template('compare.html', unis=selected, user=session.get('user'))

@app.route('/ai')
def ai_page():
    return render_template('ai.html', user=session.get('user'))

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not model: return jsonify({'response': '⚠️ AI ключ не найден.'})
    try:
        msg = request.json.get('message', '')
        found = get_relevant_universities(msg)
        context = json.dumps([{'name': u['name'], 'city': u['city'], 'score': u['min_unt_score']} for u in found], ensure_ascii=False)
        response = model.generate_content(f"Ты консультант по вузам Казахстана. Вот подходящие вузы: {context}. Вопрос клиента: {msg}")
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': f"Ошибка: {e}"})

# --- ЛОГИН / РЕГИСТРАЦИЯ (ФЕЙК) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Просто берем имя, которое ввел пользователь
        username = request.form.get('username')
        if username:
            session['user'] = username # Запоминаем его
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None) # Забываем пользователя
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
