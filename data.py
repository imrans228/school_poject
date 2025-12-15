import json
import os

# 1. Список городов для фильтра (вручную добавлены все города из базы)
CITIES = [
    'Все города', 
    'Алматы', 
    'Астана', 
    'Шымкент', 
    'Караганда', 
    'Актобе', 
    'Атырау', 
    'Екибастуз', 
    'Кызылорда', 
    'Тараз', 
    'Костанай', 
    'Павлодар'
]

# 2. Полная база данных университетов
# Читаем данные из файла universities.json
try:
    # Определяем путь к JSON файлу относительно текущего скрипта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'universities.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        # ЗАГРУЖАЕМ СПИСОК В ПЕРЕМЕННУЮ UNIVERSITIES
        universities = json.load(f)
        print(f"✅ Успешно загружено {len(universities)} ВУЗов из universities.json.")
        
except FileNotFoundError:
    print("❌ ОШИБКА: Файл 'universities.json' не найден. Убедитесь, что он лежит рядом с data.py и app.py.")
    universities = []
except json.JSONDecodeError:
    # КРИТИЧЕСКАЯ ОШИБКА JSON
    print("❌ ОШИБКА: Ошибка чтения JSON в 'universities.json'. Проверьте форматирование (лишние запятые, скобки).")
    # Мы не можем продолжить без данных
    universities = []
