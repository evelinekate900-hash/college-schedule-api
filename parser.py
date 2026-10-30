import json
import datetime

# Здесь будет логика скачивания XLSX файла по ссылке на Яндекс.Таблицу
# И поиск ячеек с занятиями для 1-й подгруппы

# Допустим, скрипт нашел и сформировал расписание на сегодня:
schedule_data = {
    "date": str(datetime.date.today()),
    "subgroup": 1,
    "text_for_alice": "Сегодня у первой подгруппы две пары. Первая: Теория электрической связи. Вторая: Практика."
}

# Скрипт сохраняет результат в файл, который потом заберет Алиса
with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(schedule_data, f, ensure_ascii=False, indent=2)
  
