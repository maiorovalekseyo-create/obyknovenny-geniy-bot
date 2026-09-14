# ============================================
# БОТ «ОБЫКНОВЕННЫЙ ГЕНИЙ» — ДИАГНОСТИКА v5.1
# ============================================
# + Комбинированный результат при e=3
# + Позитив при e>=4, стандарт при e<3
# + Google Sheets: одна строка = одна сессия
# + Автосбор контактов после результата
# + Кнопка "Пропустить"
# + Кнопки после чек-листа
# + "О курсе" — информационная вставка с возвратом
# + "Пройти заново" — перезапуск

import asyncio
import json
import os
from datetime import datetime

# === НАСТРОЙКИ ===
TOKEN = "8809452582:AAGEA0KBGB3bL3w55-jQMsUzgIqPzQYs4yw"

DATA_FILE = "users.json"

# ============================================
# GOOGLE SHEETS
# ============================================

import gspread
from oauth2client.service_account import ServiceAccountCredentials

SPREADSHEET_ID = "1J6uwRvn-aRjvQNLgdC9qvR_2bRw7fUeThGngPxcq1iE"
CREDS_FILE = "google_credentials.json"

def get_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.sheet1

def find_user_row(worksheet, telegram_id):
    try:
        all_values = worksheet.get_all_values()
        for i, row in enumerate(all_values):
            if len(row) > 3 and row[3] == str(telegram_id):
                return i + 1
    except Exception as e:
        print(f"Ошибка поиска строки: {e}")
    return None

def save_to_google_sheets(user_data, create_new=False):
    try:
        worksheet = get_google_sheet()
        telegram_id = str(user_data.get('telegram_id', ''))

        row = [
            str(user_data.get('record_id', '')),
            user_data.get('click_date', ''),
            user_data.get('quiz_date', ''),
            telegram_id,
            user_data.get('telegram_username', ''),
            user_data.get('full_name', ''),
            user_data.get('birth_date', ''),
            user_data.get('gender', ''),
            str(user_data.get('age', '')),
            user_data.get('phone', ''),
            user_data.get('answer_1', ''),
            user_data.get('answer_2', ''),
            user_data.get('answer_3', ''),
            user_data.get('answer_4', ''),
            user_data.get('answer_5', ''),
            user_data.get('result', ''),
            user_data.get('status', 'NEW'),
            user_data.get('source', ''),
            user_data.get('utm', ''),
            user_data.get('ip', ''),
            user_data.get('country', ''),
            user_data.get('city', ''),
            user_data.get('notes', '')
        ]

        existing_row = find_user_row(worksheet, telegram_id)

        if existing_row and not create_new:
            worksheet.update(f'A{existing_row}:W{existing_row}', [row])
            print(f"✅ Обновлено строка {existing_row} для {telegram_id}")
        else:
            worksheet.append_row(row)
            print(f"✅ Новая строка для {telegram_id}")

        return True

    except Exception as e:
        print(f"❌ Ошибка Google Sheets: {e}")
        save_local_backup(user_data)
        return False

def save_local_backup(user_data):
    backup_file = "backup_users.json"
    backups = {}
    if os.path.exists(backup_file):
        with open(backup_file, 'r', encoding='utf-8') as f:
            backups = json.load(f)
    backups[str(user_data.get('telegram_id'))] = user_data
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backups, f, ensure_ascii=False, indent=2)
    print(f"💾 Резерв для {user_data.get('telegram_id')}")

# ============================================
# РАБОТА С ДАННЫМИ
# ============================================

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id), {
        "status": "NEW",
        "answers": [],
        "email": None,
        "diagnostic_booked": False,
        "created_at": datetime.now().isoformat()
    })

def update_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

# ============================================
# ВОПРОСЫ (5 ВАРИАНТОВ)
# ============================================

QUESTIONS = [
    {
        "text": "🔍 Вопрос 1/5\n\nВаше утро обычно начинается с...",
        "options": [
            ("Тревоги и мыслей «опять день»", "a"),
            ("Неопределённости, живу по инерции", "b"),
            ("Самокритики «вчера ничего не сделал»", "c"),
            ("Мыслей о деньгах и долгах", "d"),
            ("Радости. Есть план. Чувствую себя", "e"),
        ]
    },
    {
        "text": "🔍 Вопрос 2/5\n\nКогда думаете о себе — что приходит?",
        "options": [
            ("Не чувствую себя. Тело чужое", "a"),
            ("Не знаю кто я. Живу чужой жизнью", "b"),
            ("Я неправильный. Себя ругать — норма", "c"),
            ("Не справляюсь. Денег мало", "d"),
            ("Я на своём месте. Знаю чего хочу", "e"),
        ]
    },
    {
        "text": "🔍 Вопрос 3/5\n\nВаше тело сейчас — это...",
        "options": [
            ("Боли и усталость. Не слушаю", "a"),
            ("Не знаю. Не чувствую", "b"),
            ("Источник стыда. Не принимаю", "c"),
            ("Инструмент для работы", "d"),
            ("Друг. Слышу и благодарю", "e"),
        ]
    },
    {
        "text": "🔍 Вопрос 4/5\n\nВ отношениях вы чаще...",
        "options": [
            ("Не чувствую границ. Все требуют", "a"),
            ("Подстраиваюсь. Не говорю «нет»", "b"),
            ("Закрываюсь. Боюсь быть уязвимым", "c"),
            ("Конфликтую или молчу", "d"),
            ("Говорю честно. Есть близость", "e"),
        ]
    },
    {
        "text": "🔍 Вопрос 5/5\n\nЕсли заглянуть внутрь — что там?",
        "options": [
            ("Пустота. Усталость", "a"),
            ("Туман. Не понимаю куда иду", "b"),
            ("Критик. «Ты не такой»", "c"),
            ("Страх. Денег не хватит", "d"),
            ("Спокойствие. Ресурс. Счастье", "e"),
        ]
    },
]

# ============================================
# ДАННЫЕ ДЛЯ РЕЗУЛЬТАТОВ
# ============================================

QUESTION_TO_RESULT = {
    0: {"a": "Тело отключено", "b": "Живу чужую жизнь", "c": "Внутренний критик", "d": "Деньги и отношения — тупик"},
    1: {"a": "Тело отключено", "b": "Живу чужую жизнь", "c": "Внутренний критик", "d": "Деньги и отношения — тупик"},
    2: {"a": "Тело отключено", "b": "Живу чужую жизнь", "c": "Внутренний критик", "d": "Деньги и отношения — тупик"},
    3: {"a": "Тело отключено", "b": "Живу чужую жизнь", "c": "Внутренний критик", "d": "Деньги и отношения — тупик"},
    4: {"a": "Тело отключено", "b": "Живу чужую жизнь", "c": "Внутренний критик", "d": "Деньги и отношения — тупик"},
}

QUESTION_TEXTS = [
    "Ваше утро обычно начинается с...",
    "Когда думаете о себе — что приходит?",
    "Ваше тело сейчас — это...",
    "В отношениях вы чаще...",
    "Если заглянуть внутрь — что там?",
]

ANSWER_DESCRIPTIONS = {
    0: {"a": "тревоги и мыслей «опять день»", "b": "неопределённости, живёте по инерции", "c": "самокритики «вчера ничего не сделал»", "d": "мыслей о деньгах и долгах"},
    1: {"a": "не чувствуете себя, а тело — как чужое", "b": "не знаете, кто вы, живёте чужой жизнью", "c": "считаете себя неправильным, а ругать себя — норма", "d": "чувствуете, что не справляетесь, денег мало"},
    2: {"a": "боли и усталость, которую не слушаете", "b": "не знаете, не чувствуете", "c": "источник стыда, которое не принимаете", "d": "инструмент для работы"},
    3: {"a": "не чувствуете границ, все требуют", "b": "подстраиваетесь, не говорите «нет»", "c": "закрываетесь, боитесь быть уязвимым", "d": "конфликтуете или молчите"},
    4: {"a": "пустота и усталость", "b": "туман, не понимаете куда идёте", "c": "критик, который говорит «ты не такой»", "d": "страх, что денег не хватит"},
}

RESULTS = {
    "Тело отключено": {
        "title": "🫀 Ваше тело просит внимания",
        "description": "Вы живёте в голове, а тело — как чужое. Энергии нет, боли игнорируются, отдых — роскошь. Это не лень. Это сигнал, который вы не слышите.",
        "recommendation": """Вот 3 шага, которые можно сделать сегодня:

1. Начните с простого: 5 минут в день — просто лежите и дышите. Без телефона. Без задач.

2. Спрашивайте тело 3 раза в день: «Что ты чувствуешь прямо сейчас?» — и слушайте ответ.

3. Скажите «нет» одному делу, которое вы делаете на автомате из долга.""",
        "reviews": """Что получают люди на курсе «Обыкновенный Гений»:

«Наладилась связь с телом. Я чувствую. Я могу понять эмоцию телом.» — Наталья

«Энергия бьёт через край. Спать некогда.» — Елена

«Ушли болевые триггерные точки, где перманентно болело.» — Наталья

«Чувствую своё тело полноценным, оно начало оживать.» — Алена

«Прошла постоянная тянущая боль в правой ноге.» — Ольга""",
    },
    "Живу чужую жизнь": {
        "title": "🌫️ Вы живёте не свою жизнь",
        "description": "Вы знаете, что «где-то глубже» есть другой вы. Но не знаете, как к нему добраться. Живёте по чужим сценариям, подстраиваетесь, не говорите «нет». Это не слабость. Это привычка, которую можно изменить.",
        "recommendation": """Вот 3 шага, которые можно сделать сегодня:

1. Выпишите одно желание — только ваше, не чужое. Не анализируйте. Просто выпишите.

2. Скажите «нет» одному делу сегодня. Маленькому. Без объяснений.

3. 5 минут в тишине утром: не планируйте, просто спросите себя «Чего я хочу?»""",
        "reviews": """Что получают люди на курсе «Обыкновенный Гений»:

«Появились цели, желания. Чётко научилась разграничивать, что хочу, а что нет.» — Елена

«Я вернула себе себя. Без родительских фигур, без самоуничтожения, без чувства вины.» — Анастасия

«Стало легче контактировать. Появилось больше знакомых, встреч, мероприятий.» — Елена

«Я очень-очень счастлива. По-настоящему научилась радоваться жизни.» — Елена

«Живу из состояния счастья. Вокруг меня стало много классных, искренних людей.» — Ирина""",
    },
    "Внутренний критик": {
        "title": "🔥 Внутри слишком много критики",
        "description": "Вы привыкли себя ругать. Считаете, что «во мне что-то не так». Это не правда. Это голос, который вы услышали рано — и приняли за свой. Можно научиться его слышать и не слушаться.",
        "recommendation": """Вот 3 шага, которые можно сделать сегодня:

1. Когда начинаете себя ругать — сделайте паузу. Спросите: «Это мой голос или чужой?»

2. Перед сном назовите 3 вещи, за которые благодарны себе. Не миру. Себе.

3. Выпишите 3 мысли, которые крутятся в голове. Не анализируйте. Просто выпишите — и оставьте на бумаге.""",
        "reviews": """Что получают люди на курсе «Обыкновенный Гений»:

«Саморефлексия даёт понимание своих эмоций. Не проваливаюсь в эмоции. Самочувствие улучшилось.» — Елена

«Полюбила и приняла себя такой, какая я есть.» — Ирина

«Гораздо меньше самоедства. Понимаю природу своей прокрастинации.» — Юлия

«Я достоин всего самого лучшего в этом мире, по праву рождения.» — Алексей

«Я уже есть и этого достаточно. Разрешаю себе зайти в свой максимум.» — Ирина""",
    },
    "Деньги и отношения — тупик": {
        "title": "💰 Деньги и отношения идут через напряжение",
        "description": "Деньги приходят с трудом. Отношения — через контроль или молчание. Всё повторяется по кругу, как у родителей. Это не проклятие. Это программа, которую можно переписать.",
        "recommendation": """Вот 3 шага, которые можно сделать сегодня:

1. Посмотрите на свои финансы: сколько пришло, сколько ушло. Без вины. Просто цифры.

2. В одном разговоре сегодня скажите, что чувствуете. Не обвиняйте. Только «Я чувствую...»

3. Спросите себя: «А что, если деньги могут приходить легче?» — и посмотрите, что ответит тело.""",
        "reviews": """Что получают люди на курсе «Обыкновенный Гений»:

«Доход вырос в 4 раза. Закрыл кредитку. Приобрёл квартиру.» — Евгений

«Пошли лёгкие деньги — когда в радости и в удовольствии.» — Ольга

«Отношения после 10 лет совместной жизни вышли на новый уровень.» — Алена

«Мы учимся заново разговаривать друг с другом. Не воспринимаю его как соперника.» — Ольга

«Подняла стоимость услуг — не встретив ни одного сопротивления.» — Таня""",
    },
    "Вы на пути к себе": {
        "title": "🌟 Вы на пути к себе",
        "description": "Вы уже чувствуете связь с собой. Знаете, чего хотите. Тело слушаете. В отношениях — честность. Это не финальная точка, а хорошее место, из которого можно расти дальше.",
        "recommendation": """Вот 3 шага, чтобы остаться на этом пути:

1. Продолжайте ежедневно спрашивать себя: «Чего я хочу прямо сейчас?» — и слушать ответ.

2. Окружайте себя людьми, которые поддерживают, а не высасывают. Границы — это забота о себе.

3. Празднуйте маленькие победы. То, что у вас уже есть — достойно внимания.""",
        "reviews": """Что говорят те, кто прошёл курс и остался на пути:

«Я очень-очень счастлива. По-настоящему научилась радоваться жизни.» — Елена

«Живу из состояния счастья. Вокруг меня стало много классных, искренних людей.» — Ирина

«Я достоин всего самого лучшего в этом мире, по праву рождения.» — Алексей

«Я уже есть и этого достаточно. Разрешаю себе зайти в свой максимум.» — Ирина

«Чем лучше я отдыхаю, тем больше я зарабатываю. Доход вырос в 2,5 раза.» — Алена""",
    },
}

def analyze_result(answers):
    counts = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0}
    for ans in answers:
        counts[ans] += 1

    e_count = counts["e"]

    if e_count >= 4:
        return "Вы на пути к себе", "positive", []

    elif e_count == 3:
        non_e = []
        for i, ans in enumerate(answers):
            if ans != "e":
                result_name = QUESTION_TO_RESULT[i][ans]
                description = ANSWER_DESCRIPTIONS[i][ans]
                non_e.append({
                    "question_num": i + 1,
                    "question_text": QUESTION_TEXTS[i],
                    "answer": ans,
                    "description": description,
                    "result_name": result_name
                })
        return "Комбинированный", "mixed", non_e

    else:
        max_count = max(counts.values())
        top_answers = [k for k, v in counts.items() if v == max_count and k != "e"]

        if "a" in top_answers:
            return "Тело отключено", "standard", []
        elif "b" in top_answers:
            return "Живу чужую жизнь", "standard", []
        elif "c" in top_answers:
            return "Внутренний критик", "standard", []
        else:
            return "Деньги и отношения — тупик", "standard", []

def build_mixed_result(non_e_answers):
    unique_results = {}
    for item in non_e_answers:
        name = item["result_name"]
        if name not in unique_results:
            unique_results[name] = []
        unique_results[name].append(item)

    positive_parts = []
    for i in range(5):
        if i not in [item["question_num"] - 1 for item in non_e_answers]:
            if i == 0:
                positive_parts.append("утро начинается с радости и плана")
            elif i == 1:
                positive_parts.append("вы на своём месте и знаете чего хотите")
            elif i == 2:
                positive_parts.append("тело — друг, которого слышите")
            elif i == 3:
                positive_parts.append("в отношениях — честность и близость")
            elif i == 4:
                positive_parts.append("внутри — спокойствие и ресурс")

    positive_text = "Так здорово, что " + ", ".join(positive_parts) + ". Это уже много. Не все к этому приходят."

    investigate_text = "📋 Что ещё можно исследовать\n\n"
    for item in non_e_answers:
        investigate_text += f"**Вопрос {item['question_num']}: «{item['question_text']}»**\n\n"
        investigate_text += f"Вы ответили, что {item['description']}. Это знакомо многим. Мы знаем, каково это. И это можно исследовать — не спеша, с поддержкой.\n\n"

    rec_text = "💡 Вот 3 шага, которые помогут немного изменить ситуацию и позволят расслабиться\n\n"
    for result_name, items in unique_results.items():
        result = RESULTS[result_name]
        rec_text += f"**{result['title']}**\n\n"
        rec_text += result['recommendation'] + "\n\n"

    reviews_text = "✨ Что получают люди, которые прошли этот путь\n\n"
    for result_name, items in unique_results.items():
        result = RESULTS[result_name]
        reviews_text += result['reviews'] + "\n\n"

    full_text = f"🌟 Вы на пути к себе\n\n{positive_text}\n\n{investigate_text}{rec_text}{reviews_text}"
    return full_text
# ============================================
# ОСНОВНОЙ КОД БОТА
# ============================================

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy="http://proxy.server:3128")
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# --- КЛАВИАТУРЫ ---

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, начать", callback_data="quiz_start")],
        [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_start")]
    ])

def get_question_keyboard(q_num):
    buttons = []
    for text, callback in QUESTIONS[q_num]["options"]:
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"q{q_num}_{callback}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура ШАГА 5 (Результат)
def get_result_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Получить чек-лист", callback_data="download_checklist")],
        [InlineKeyboardButton(text="📅 Записаться на диагностику", callback_data="start_contact_collection")],
        [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_result")]
    ])

# Клавиатура ШАГА 6 (Чек-лист)
def get_checklist_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться на диагностику", callback_data="start_contact_collection")],
        [InlineKeyboardButton(text="💬 Написать Ларисе напрямую", url="https://t.me/Laracoach_1")],
        [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_checklist")],
        [InlineKeyboardButton(text="🔄 Пройти квиз заново", callback_data="restart_quiz")]
    ])

# Клавиатура ШАГА 7Б (Пропуск)
def get_skip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться к Ларисе", url="https://t.me/Laracoach_1")],
        [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_skip")],
        [InlineKeyboardButton(text="🔄 Пройти квиз заново", callback_data="restart_quiz")]
    ])

# Клавиатура ШАГА 8А (Финал)
def get_final_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Написать Ларисе", url="https://t.me/Laracoach_1")],
        [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_final")],
        [InlineKeyboardButton(text="🔄 Пройти квиз заново", callback_data="restart_quiz")]
    ])

# Клавиатура сбора контактов
def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться телефоном", request_contact=True)],
            [KeyboardButton(text="⏭️ Пропустить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    user['telegram_id'] = user_id
    user['telegram_username'] = message.from_user.username or ''
    user['click_date'] = datetime.now().isoformat()
    user['status'] = 'NEW'
    user['record_id'] = f"REC_{user_id}_{int(datetime.now().timestamp())}"
    user['full_name'] = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    user['answers'] = []

    save_to_google_sheets(user, create_new=True)
    update_user(user_id, user)

    await message.answer(
        "👋 Привет.\n\n"
        "Я задам 5 вопросов — не про то, кто вы, а про то, что вы чувствуете.\n\n"
        "В конце получите:\n"
        "• Что происходит сейчас\n"
        "• 3 шага на сегодня\n"
        "• Отзывы тех, кто прошёл курс\n\n"
        "3 минуты. Готовы?",
        reply_markup=get_start_keyboard()
    )

    user["status"] = "QUIZ_STARTED"
    update_user(user_id, user)
    save_to_google_sheets(user)

# Обработчик "О курсе" из ШАГА 0 (Старт)
@dp.callback_query(lambda c: c.data == "view_course_from_start")
async def view_course_from_start(callback: types.CallbackQuery):
    await callback.message.answer(
        "📚 Курс «Обыкновенный Гений»\n\n"
        "9,5 недель трансформации.\n"
        "От глубины к результату.\n\n"
        "• Мышление → Эмоции → Тело → Результат\n"
        "• 9 недель + выездной тренинг «Перерождение»\n"
        "• Онлайн + очные встречи\n"
        "• Индивидуальные разборы\n\n"
        "Пройти диагностику? Бесплатно. 3 минуты.",
        reply_markup=get_start_keyboard()
    )

# Универсальный обработчик "О курсе" — возвращает к кнопкам того шага, откуда пришёл
@dp.callback_query(lambda c: c.data.startswith("view_course_from_"))
async def view_course_universal(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    source = callback.data.replace("view_course_from_", "")

    # Сохраняем, откуда пришёл
    user["view_course_source"] = source
    update_user(user_id, user)

    await callback.message.answer(
        "📚 Курс «Обыкновенный Гений»\n\n"
        "9,5 недель трансформации.\n"
        "От глубины к результату.\n\n"
        "• Мышление → Эмоции → Тело → Результат\n"
        "• 9 недель + выездной тренинг «Перерождение»\n"
        "• Онлайн + очные встречи\n"
        "• Индивидуальные разборы\n\n"
        "Продолжим?",
        reply_markup=get_return_keyboard(source)
    )

def get_return_keyboard(source):
    """Возвращает клавиатуру в зависимости от того, откуда пришёл клиент"""
    if source == "result":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Получить чек-лист", callback_data="download_checklist")],
            [InlineKeyboardButton(text="📅 Записаться на диагностику", callback_data="start_contact_collection")],
            [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_result")]
        ])
    elif source == "checklist":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться на диагностику", callback_data="start_contact_collection")],
            [InlineKeyboardButton(text="💬 Написать Ларисе напрямую", url="https://t.me/Laracoach_1")],
            [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_checklist")],
            [InlineKeyboardButton(text="🔄 Пройти квиз заново", callback_data="restart_quiz")]
        ])
    elif source == "skip":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться к Ларисе", url="https://t.me/Laracoach_1")],
            [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_skip")],
            [InlineKeyboardButton(text="🔄 Пройти квиз заново", callback_data="restart_quiz")]
        ])
    elif source == "final":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📩 Написать Ларисе", url="https://t.me/Laracoach_1")],
            [InlineKeyboardButton(text="📖 О курсе", callback_data="view_course_from_final")],
            [InlineKeyboardButton(text="🔄 Пройти квиз заново", callback_data="restart_quiz")]
        ])
    else:
        return get_start_keyboard()

@dp.callback_query(lambda c: c.data == "quiz_start")
async def quiz_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    user["answers"] = []
    user["status"] = "QUIZ_STARTED"
    update_user(user_id, user)
    save_to_google_sheets(user)

    await callback.message.edit_text(
        QUESTIONS[0]["text"],
        reply_markup=get_question_keyboard(0)
    )

@dp.callback_query(lambda c: c.data.startswith("q"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    parts = callback.data.split("_")
    q_num = int(parts[0][1:])
    answer = parts[1]

    user["answers"].append(answer)
    user[f'answer_{q_num + 1}'] = answer
    update_user(user_id, user)
    save_to_google_sheets(user)

    next_q = q_num + 1
    if next_q < len(QUESTIONS):
        await callback.message.edit_text(
            QUESTIONS[next_q]["text"],
            reply_markup=get_question_keyboard(next_q)
        )
    else:
        await show_result(callback, user_id)

async def show_result(callback, user_id):
    user = get_user(user_id)
    result_name, result_type, non_e = analyze_result(user["answers"])

    user["status"] = "QUIZ_FINISHED"
    user["result"] = result_name
    user["quiz_date"] = datetime.now().isoformat()
    update_user(user_id, user)
    save_to_google_sheets(user)

    if result_type == "mixed":
        full_text = build_mixed_result(non_e)
        await callback.message.edit_text(
            full_text,
            reply_markup=get_result_keyboard()
        )
    else:
        result = RESULTS[result_name]
        await callback.message.edit_text(
            f"{result['title']}\n\n"
            f"{result['description']}\n\n"
            f"{result['recommendation']}",
            reply_markup=get_result_keyboard()
        )

@dp.callback_query(lambda c: c.data == "download_checklist")
async def download_checklist(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    result_name = user.get("result", "Тело отключено")

    if result_name == "Комбинированный":
        result = RESULTS["Вы на пути к себе"]
        full_text = f"""📋 ВАШ ЧЕК-ЛИСТ

{result['recommendation']}

{result['reviews']}

---
💡 Хотите так же?
Запишитесь на бесплатную диагностику.
30 минут. Онлайн. Без давления.

Готовы начать путь?"""
    else:
        result = RESULTS[result_name]
        full_text = f"""📋 ВАШ ЧЕК-ЛИСТ

{result['recommendation']}

{result['reviews']}

---
💡 Хотите так же?
Запишитесь на бесплатную диагностику.
30 минут. Онлайн. Без давления.

Готовы начать путь?"""

    user["status"] = "LEADMAGNET"
    update_user(user_id, user)
    save_to_google_sheets(user)

    await callback.message.answer(
        full_text,
        reply_markup=get_checklist_keyboard()
    )

# Перезапуск квиза
@dp.callback_query(lambda c: c.data == "restart_quiz")
async def restart_quiz(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    # Сбрасываем ответы, но сохраняем контакты
    user["answers"] = []
    user["status"] = "NEW"
    user["answer_1"] = ""
    user["answer_2"] = ""
    user["answer_3"] = ""
    user["answer_4"] = ""
    user["answer_5"] = ""
    user["result"] = ""
    user["quiz_date"] = ""
    update_user(user_id, user)
    save_to_google_sheets(user)

    await callback.message.answer(
        "👋 Привет.\n\n"
        "Я задам 5 вопросов — не про то, кто вы, а про то, что вы чувствуете.\n\n"
        "В конце получите:\n"
        "• Что происходит сейчас\n"
        "• 3 шага на сегодня\n"
        "• Отзывы тех, кто прошёл курс\n\n"
        "3 минуты. Готовы?",
        reply_markup=get_start_keyboard()
    )
# ============================================
# СБОР КОНТАКТОВ
# ============================================

@dp.callback_query(lambda c: c.data == "start_contact_collection")
async def start_contact_collection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    user["status"] = "COLLECTING_CONTACTS"
    user["contact_step"] = 0
    update_user(user_id, user)
    save_to_google_sheets(user)

    await callback.message.answer(
        "📋 Для записи на диагностику мне нужны ваши контакты.\n\n"
        "Нажмите кнопку ниже, чтобы поделиться телефоном, или «Пропустить».\n\n"
        "В любом случае вы сможете записаться к Ларисе.",
        reply_markup=get_contact_keyboard()
    )

@dp.message(lambda message: message.contact is not None)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user.get("status") != "COLLECTING_CONTACTS":
        return

    contact = message.contact
    user['phone'] = contact.phone_number
    update_user(user_id, user)
    save_to_google_sheets(user)

    user["contact_step"] = 1
    update_user(user_id, user)

    await message.answer(
        "✅ Телефон сохранён.\n\nВаше ФИО (как к вам обращаться)?",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "⏭️ Пропустить")
async def handle_skip(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    user["status"] = "SKIPPED_CONTACTS"
    update_user(user_id, user)
    save_to_google_sheets(user)

    await message.answer(
        "👌 Понимаю.\n\n"
        "Вы всё равно можете записаться на бесплатную диагностику к Ларисе прямо сейчас.",
        reply_markup=get_skip_keyboard()
    )

@dp.message(lambda message: get_user(message.from_user.id).get("status") == "COLLECTING_CONTACTS")
async def handle_contact_steps(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    step = user.get("contact_step", 0)
    text = message.text.strip()

    if step == 1:
        user['full_name'] = text
        user["contact_step"] = 2
        update_user(user_id, user)
        save_to_google_sheets(user)
        await message.answer("✅ ФИО сохранено.\n\nДата рождения (ДД.ММ.ГГГГ)?")

    elif step == 2:
        user['birth_date'] = text
        user["contact_step"] = 3
        update_user(user_id, user)
        save_to_google_sheets(user)
        await message.answer("✅ Дата рождения сохранена.\n\nПол (М/Ж)?")

    elif step == 3:
        user['gender'] = text
        user["contact_step"] = 4
        update_user(user_id, user)
        save_to_google_sheets(user)
        await message.answer("✅ Пол сохранён.\n\nВозраст (число)?")

    elif step == 4:
        user['age'] = text
        user["status"] = "DIAGNOSTIC_BOOKED"
        update_user(user_id, user)
        save_to_google_sheets(user)

        await message.answer(
            f"✅ Все данные сохранены!\n\n"
            f"📞 Телефон: {user.get('phone', '—')}\n"
            f"📝 ФИО: {user.get('full_name', '—')}\n"
            f"📅 Дата рождения: {user.get('birth_date', '—')}\n"
            f"⚧ Пол: {user.get('gender', '—')}\n"
            f"🎂 Возраст: {user.get('age', '—')}\n\n"
            f"Лариса свяжется с вами в течение дня.\n\n"
            f"Или напишите ей прямо сейчас: @Laracoach_1",
            reply_markup=get_final_keyboard()
        )

# ============================================
# СЛУЖЕБНЫЕ КОМАНДЫ
# ============================================

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    await message.answer(
        "📋 Обновить данные:\n\n"
        "Отправьте через запятую:\n"
        "ФИО, ДД.ММ.ГГГГ, М/Ж, возраст, телефон\n\n"
        "Пример:\n"
        "Иванов Иван, 15.03.1985, М, 39, +79991234567"
    )

@dp.message(Command("mydata"))
async def cmd_mydata(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    data_text = f"""📊 Ваши данные:

🆔 Telegram ID: {user.get('telegram_id', '—')}
👤 Ник: @{user.get('telegram_username', '—')}
📝 ФИО: {user.get('full_name', '—')}
📅 Дата рождения: {user.get('birth_date', '—')}
⚧ Пол: {user.get('gender', '—')}
🎂 Возраст: {user.get('age', '—')}
📱 Телефон: {user.get('phone', '—')}
🎭 Результат: {user.get('result', '—')}
📅 Дата теста: {user.get('quiz_date', '—')}
📊 Статус: {user.get('status', '—')}

Обновить: /profile
"""
    await message.answer(data_text)

@dp.message(lambda message: "," in message.text and len(message.text.split(",")) >= 4 and get_user(message.from_user.id).get("status") not in ["COLLECTING_CONTACTS"])
async def handle_profile_update(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    parts = [p.strip() for p in message.text.split(",")]

    try:
        if len(parts) >= 1:
            user['full_name'] = parts[0]
        if len(parts) >= 2:
            user['birth_date'] = parts[1]
        if len(parts) >= 3:
            user['gender'] = parts[2]
        if len(parts) >= 4:
            user['age'] = parts[3]
        if len(parts) >= 5:
            user['phone'] = parts[4]

        update_user(user_id, user)
        save_to_google_sheets(user)

        await message.answer("✅ Данные обновлены!")
    except Exception as e:
        await message.answer("❌ Ошибка формата. Проверьте: ФИО, ДД.ММ.ГГГГ, М/Ж, возраст, телефон")

# --- ЗАПУСК ---

async def main():
    print("Бот запущен! v5.1")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())