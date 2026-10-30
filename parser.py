import pandas as pd
import json
import re
import datetime
from zoneinfo import ZoneInfo
import requests
import urllib.parse
import os

# --- НАСТРОЙКИ ---
GROUP_NAME = "КИТ-ИССС-24" # <-- Впиши точное название своей группы из таблицы
SUBGROUP = 1                 # Твоя подгруппа (уже указана)
YANDEX_LINK = "https://docs.360.yandex.ru/view/d/eSjfjNM06Zcyzwqv5124yiPegnqahzm72s0qoIz-cKg6Y1haOWRpYXFSZw"             # <-- Вставь публичную ссылку на Яндекс.Диск (если есть). Если файл обновляешь вручную, оставь пустым.
FILE_NAME = "Расписание.xlsx"
# -----------------

def download_file():
    if not YANDEX_LINK:
        return
    print("Скачивание расписания с Яндекс.Диска...")
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={urllib.parse.quote(YANDEX_LINK)}"
    resp = requests.get(api_url)
    if resp.status_code == 200:
        download_url = resp.json()['href']
        r = requests.get(download_url)
        with open(FILE_NAME, 'wb') as f:
            f.write(r.content)
        print("Файл успешно скачан!")
    else:
        print("Не удалось получить прямую ссылку.")

def get_today_sheet_name():
    # Используем часовой пояс Якутска (СВФУ)
    now = datetime.datetime.now(ZoneInfo("Asia/Yakutsk"))
    return now.strftime("%d%m%y")

def parse_schedule():
    sheet_name = get_today_sheet_name()
    print(f"Ищем лист на сегодня: {sheet_name}")
    
    try:
        df = pd.read_excel(FILE_NAME, sheet_name=sheet_name, header=None)
    except ValueError:
        return "Расписание на сегодня ещё не выложили или сегодня выходной."
    except FileNotFoundError:
        return "Файл расписания не найден."

    # Поиск строки с названием группы
    group_idx = df[df[0].astype(str).str.contains(GROUP_NAME, na=False, case=False)].index
    if len(group_idx) == 0:
        return f"Твоя группа не найдена в расписании на сегодня."
        
    start_idx = group_idx[0]
    # Пары идут со 2-й по 7-ю строку после названия группы
    pairs = df.iloc[start_idx + 2 : start_idx + 8]
    
    alice_text_parts = []
    pair_number = 1
    actual_pairs_count = 0
    
    for _, row in pairs.iterrows():
        time_str = str(row[1]).strip()
        subject = str(row[2]).strip()
        room = str(row[5]).strip()
        
        # Пропуск пустых окон
        if pd.isna(row[1]) or time_str == 'nan' or subject == 'nan' or not subject or subject == ' ':
            pair_number += 1
            continue
            
        # Фильтрация по подгруппе
        skip = False
        subj_lower = subject.lower()
        if SUBGROUP == 1 and ('2пг' in subj_lower or '2 пг' in subj_lower):
            skip = True
        elif SUBGROUP == 2 and ('1пг' in subj_lower or '1 пг' in subj_lower):
            skip = True
            
        if not skip:
            # Очищаем текст от мусора, чтобы Алиса читала красиво
            subj_clean = re.sub(r'[12]\s*пг\*?', '', subject, flags=re.IGNORECASE).strip()
            subj_clean = re.sub(r'с\d{6}до\d{6}', '', subj_clean).strip()
            subj_clean = re.sub(r'до\d{6}', '', subj_clean).strip()
            
            alice_text_parts.append(f"{pair_number}-я пара в {time_str[:5]}: {subj_clean}, аудитория {room}.")
            actual_pairs_count += 1
            
        pair_number += 1

    if actual_pairs_count == 0:
        return "Сегодня пар нет, отдыхай!"
        
    intro = f"У тебя сегодня {actual_pairs_count} "
    if actual_pairs_count == 1: intro += "пара. "
    elif 2 <= actual_pairs_count <= 4: intro += "пары. "
    else: intro += "пар. "
    
    return intro + " ".join(alice_text_parts)

if __name__ == "__main__":
    download_file()
    result_text = parse_schedule()
    print(result_text)
    
    # Сохранение итогового файла для Алисы
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump({"text_for_alice": result_text}, f, ensure_ascii=False, indent=2)
        
