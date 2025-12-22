from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai
import json
import os

app = Flask(__name__)
# Секретный ключ для работы сессий
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_default_12345")

# --- 1. ЗАГРУЗКА БАЗЫ ВУЗОВ ---
CITIES = ['Все города', 'Алматы', 'Астана', 'Шымкент', 'Караганда', 'Актобе', 'Костанай']
universities = []

try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'universities.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        universities = json.load(f)
except Exception as e:
    print(f"⚠️ Ошибка базы данных: {e}")
    universities = []

# --- 2. AI НАСТРОЙКИ ---
API_KEY = os.environ.get("API_KEY")
model = None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except: pass

# --- 3. ПОЛЕЗНЫЕ ФУНКЦИИ ---
def get_user():
    """Безопасно получает текущего пользователя"""
    return session.get('user')

def get_relevant_universities(query):
    q = query.lower()
    return [u for u in universities if q in u.get('name', '').lower()][:5]

# --- 4. МАРШРУТЫ (СТРАНИЦЫ) ---

@app.route('/')
def home():
    return render_template('index.html', unis=universities, user=get_user())

@app.route('/catalog')
def catalog():
    search = request.args.get('search', '').lower().strip()
    city = request.args.get('city', 'Все города')
    
    result = universities

    if city and city != "Все города":
        result = [u for u in result if u.get('city') == city]
    
    if search:
        result = [u for u in result if search in u.get('name', '').lower()]

    return render_template('catalog.html', unis=result, cities=CITIES, current_city=city, user=get_user())

@app.route('/detail/<uni_id>')
def detail(uni_id):
    uni = next((u for u in universities if u.get('id') == uni_id), None)
    if not uni: return "Вуз не найден", 404
    return render_template('detail.html', uni=uni, user=get_user())

# --- ВОТ ЗДЕСЬ БЫЛА ОШИБКА, ТЕПЕРЬ ИСПРАВЛЕНО ---
@app.route('/compare')
def compare():
    try:
        ids_str = request.args.get('ids', '')
        selected = []
        
        if ids_str:
            ids = ids_str.split(',')
            # Ищем вузы, ID которых есть в списке
            selected = [u for u in universities if str(u.get('id')) in ids]
            
        return render_template('compare.html', unis=selected, user=get_user())
    except Exception as e:
        return f"Ошибка сервера на странице сравнения: {e}", 500

@app.route('/ai')
def ai_page():
    return render_template('ai.html', user=get_user())

# --- ЛОГИН / ВЫХОД ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['user'] = username
            return redirect(url_for('home'))
    return render_template('login.html', user=get_user())

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# --- API AI ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not model: return jsonify({'response': '⚠️ Ключ AI не настроен.'})
    try:
        msg = request.json.get('message', '')
        found = get_relevant_universities(msg)
        context = json.dumps([{'name': u['name'], 'city': u['city']} for u in found], ensure_ascii=False)
        response = model.generate_content(f"Контекст: {context}. Вопрос: {msg}")
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
