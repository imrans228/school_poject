from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import os
import sys

# ==========================================
# 1. МАГИЯ ПУТЕЙ (Исправляет TemplateNotFound)
# ==========================================

# Определяем точную папку, где лежит этот файл app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

print("-" * 50)
print(f"📂 Рабочая папка: {BASE_DIR}")
print("🧐 Проверяю наличие HTML файлов в этой папке...")

# Проверяем, видит ли питон ваши файлы
files_in_folder = os.listdir(BASE_DIR)
required_files = ['index.html', 'catalog.html', 'detail.html', 'compare.html', 'base.html']
missing_files = []

for f in required_files:
    if f in files_in_folder:
        print(f"   ✅ Вижу файл: {f}")
    else:
        print(f"   ❌ НЕ ВИЖУ файл: {f}")
        missing_files.append(f)

print("-" * 50)

if missing_files:
    print("⚠️  ВНИМАНИЕ: Python не видит ваши HTML файлы!")
    print(f"   Положите файлы {missing_files} в папку: {BASE_DIR}")
    print("   И только потом запускайте программу.")
    # Мы не останавливаем программу, чтобы вы могли увидеть ошибку в браузере,
    # но в консоли вы уже знаете причину.

# Настраиваем Flask искать шаблоны ПРЯМО ЗДЕСЬ
app = Flask(__name__, template_folder=BASE_DIR)


# ==========================================
# 2. НАСТРОЙКИ И ДАННЫЕ
# ==========================================

API_KEY = "AIzaSyCZ_C9WIYSMtPkdsZJpXd-IR_c0DjcuPIQ"
MODEL_NAME = 'gemini-2.5-flash'

CITIES = ['Алматы', 'Астана', 'Шымкент']

# Вшитая база данных (чтобы не зависеть от data.py)
universities = [
    {
        'id': 'kaznu', 'name': 'КазНУ', 'fullName': 'КазНУ им. аль-Фараби', 'city': 'Алматы',
        'type': 'Государственный', 'direction': 'Многопрофильный', 'tuition': 1100000, 'rating': 4.9,
        'desc': 'Главный национальный вуз страны. Лидер в рейтингах QS.',
        'color': 'from-blue-600 to-cyan-500',
        'imageUrl': "https://placehold.co/1200x400/2563eb/ffffff?text=KazNU",
        'stats': {'employment': 92, 'grant': 85, 'students': 25000},
        'features': ['Огромный кампус', 'Международные связи'],
        'contacts': {'phone': '+7 (727) 377-33-33', 'email': 'info@kaznu.kz', 'address': 'г. Алматы, пр. аль-Фараби 71'},
        'mapEmbedUrl': ''
    },
    {
        'id': 'kbtu', 'name': 'КБТУ', 'fullName': 'КБТУ', 'city': 'Алматы',
        'type': 'Частный', 'direction': 'IT и Нефтегаз', 'tuition': 1800000, 'rating': 4.8,
        'desc': 'Топовый технический вуз.',
        'color': 'from-blue-800 to-indigo-900',
        'imageUrl': "https://placehold.co/1200x400/1e3a8a/ffffff?text=KBTU",
        'stats': {'employment': 98, 'grant': 40, 'students': 4000},
        'features': ['Обучение на английском', 'Связи с Shell'],
        'contacts': {'phone': '+7 (727) 357-42-42', 'email': 'info@kbtu.kz', 'address': 'г. Алматы, ул. Толе би 59'},
        'mapEmbedUrl': ''
    },
    {
        'id': 'satbayev', 'name': 'Satbayev', 'fullName': 'Satbayev University', 'city': 'Алматы',
        'type': 'Государственный', 'direction': 'Инженерия', 'tuition': 950000, 'rating': 4.7,
        'desc': 'Легендарный Политех.',
        'color': 'from-green-600 to-teal-600',
        'imageUrl': "https://placehold.co/1200x400/059669/ffffff?text=Satbayev",
        'stats': {'employment': 90, 'grant': 70, 'students': 15000},
        'features': ['Сильная инженерия', 'Общежития'],
        'contacts': {'phone': '+7 (727) 292-60-25', 'email': 'info@satbayev.university', 'address': 'г. Алматы, ул. Сатпаева 22'},
        'mapEmbedUrl': ''
    },
    {
        'id': 'nu', 'name': 'NU', 'fullName': 'Nazarbayev University', 'city': 'Астана',
        'type': 'Назарбаев Университет', 'direction': 'Наука', 'tuition': 0, 'rating': 5.0,
        'desc': 'Вуз мирового уровня.',
        'color': 'from-yellow-500 to-orange-500',
        'imageUrl': "https://placehold.co/1200x400/f59e0b/ffffff?text=NU",
        'stats': {'employment': 94, 'grant': 95, 'students': 6000},
        'features': ['Мировой уровень', 'Наука'],
        'contacts': {'phone': '+7 (7172) 70-66-88', 'email': 'info@nu.edu.kz', 'address': 'г. Астана, пр. Кабанбай батыра 53'},
        'mapEmbedUrl': ''
    },
    {
        'id': 'sku', 'name': 'ЮКУ', 'fullName': 'ЮКУ им. Ауэзова', 'city': 'Шымкент',
        'type': 'Государственный', 'direction': 'Многопрофильный', 'tuition': 600000, 'rating': 4.5,
        'desc': 'Самый большой вуз Юга.',
        'color': 'from-indigo-600 to-violet-600',
        'imageUrl': "https://placehold.co/1200x400/4f46e5/ffffff?text=SKU",
        'stats': {'employment': 82, 'grant': 70, 'students': 30000},
        'features': ['Доступно', 'Большой выбор'],
        'contacts': {'phone': '+7 (7252) 21-01-41', 'email': 'info@auezov.edu.kz', 'address': 'г. Шымкент, пр. Тауке хана 5'},
        'mapEmbedUrl': ''
    }
]

# Подключение ИИ
try:
    if API_KEY != "ВСТАВЬТЕ_ВАШ_API_KEY_СЮДА":
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        print("✅ ИИ подключен")
    else:
        model = None
        print("⚠️ ИИ не работает (нет ключа)")
except Exception as e:
    model = None
    print(f"⚠️ Ошибка ИИ: {e}")

# ==========================================
# 3. МАРШРУТЫ
# ==========================================

@app.route('/')
def home():
    return render_template('index.html', unis=universities)

@app.route('/catalog')
def catalog():
    search = request.args.get('search', '').lower().strip()
    city = request.args.get('city', '')
    
    result = universities
    
    if search:
        result = [u for u in result if search in u['name'].lower() or search in u['fullName'].lower()]
    
    if city and city != "Все города":
        result = [u for u in result if u['city'] == city]

    return render_template('catalog.html', unis=result, cities=CITIES)

@app.route('/detail/<uni_id>')
def detail(uni_id):
    uni = next((u for u in universities if u['id'] == uni_id), None)
    if not uni: return "Вуз не найден", 404
    return render_template('detail.html', uni=uni)

@app.route('/compare')
def compare():
    ids = request.args.get('ids', '').split(',')
    selected = [u for u in universities if u['id'] in ids]
    return render_template('compare.html', unis=selected)

@app.route('/ai')
def ai_page():
    return render_template('ai.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not model:
        return jsonify({'response': 'Пожалуйста, вставьте API ключ в код (строка 46)!'})
    
    try:
        msg = request.json.get('message', '')
        context = f"База вузов: {json.dumps(universities, ensure_ascii=False)}. Вопрос: {msg}"
        response = model.generate_content(context)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': f"Ошибка: {str(e)}"})

if __name__ == '__main__':
    print("🚀 Запуск сервера...")
    app.run(debug=True, port=5000)
