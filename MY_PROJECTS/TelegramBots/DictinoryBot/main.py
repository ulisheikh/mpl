# -*- coding: utf-8 -*-
"""
KOREAN-O'ZBEK LUG'AT BOT
Yangilangan versiya - 2026
TUZATILGAN: Ko'p qatorli so'zlar parse qilish
"""

# ============================================
# IMPORT QISMI
# ============================================
import telebot
import json
import os
import re
import subprocess
import psutil
import threading
import time
from datetime import datetime
from html import escape

# ============================================
# KONFIGURATSIYA
# ============================================
TOKEN = os.getenv("BOT_TOKEN", "8046756811:AAEsMXNBMkIMkqM3XtVyQ3OzOd4itRfn03M")
DATA_FILE = "dictionary.json"
START_TIME = datetime.now()
ADMIN_ID = 8046330769

bot = telebot.TeleBot(TOKEN)
user_context = {}

# ============================================
# MA'LUMOTLAR BILAN ISHLASH FUNKSIYALARI
# ============================================

def load_data():
    """Lug'at faylini yuklash va eski formatni yangilash"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Eski "Topic-" formatini "Topik-" ga o'zgartirish
            updated = False
            new_data = {}
            for key, value in data.items():
                if key.startswith("Topic-"):
                    new_key = key.replace("Topic-", "Topik-")
                    new_data[new_key] = value
                    updated = True
                else:
                    new_data[key] = value
            
            if updated:
                save_data(new_data)
                return new_data
            
            return data
        except: 
            return {}
    return {}

def save_data(data):
    """Lug'at faylini xavfsiz saqlash"""
    try:
        if os.path.exists(DATA_FILE):
            backup_file = DATA_FILE + ".backup"
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Save error: {e}")

def is_korean(text):
    """Koreyscha matnni aniqlash"""
    return bool(re.search('[\uac00-\ud7af]', text))

def parse_multiline_words(text):
    """
    Ko'p qatorli so'zlarni parse qilish
    
    Format 1 (raqamli):
    33
    가져/오다 olib kelmoq
    uyga/bormoq 집에 가다
    
    Format 2 (raqamsiz):
    가져 오다 olib kelmoq
    uyga bormoq 집에 가다
    """
    words = []
    lines = text.strip().splitlines()  # split("\n") o'rniga splitlines()
    
    for line in lines:
        line = line.strip()
        
        # Bo'sh qatorlar va faqat raqamlarni o'tkazib yuborish
        if not line or line.isdigit():
            continue
        
        # / belgisini bo'sh joyga almashtirish
        line_cleaned = line.replace("/", " ")
        
        # So'zlarni ajratish
        parts = line_cleaned.split()
        
        if len(parts) < 2:
            continue
        
        # Korean va Uzbek so'zlarni aniqlash
        korean_parts = []
        uzbek_parts = []
        
        for part in parts:
            # Agar koreys harflari bo'lsa (Hangul Unicode: \uAC00-\uD7A3)
            if is_korean(part):
                korean_parts.append(part)
            else:
                uzbek_parts.append(part)
        
        if korean_parts and uzbek_parts:
            korean = ' '.join(korean_parts)
            uzbek = ' '.join(uzbek_parts)
            
            words.append({
                'korean': korean,
                'uzbek': uzbek
            })
    
    return words

# ============================================
# PYTHON EXPORT FUNKSIYASI
# ============================================

def json_to_python():
    """JSON ni Python kodiga o'girish"""
    data = load_data()
    
    py_code = "# -*- coding: utf-8 -*-\n"
    py_code += "# LUG'AT MA'LUMOTLARI\n"
    py_code += "# Avtomatik yaratilgan fayl\n\n"
    py_code += "dictionary = {\n"
    
    for topic_key, sections in data.items():
        topic_num = topic_key.replace("Topik-", "")
        py_code += f"    # {topic_num}-TOPIK\n"
        py_code += f'    "{topic_key}": {{\n'
        
        for section_key, questions in sections.items():
            py_code += f'        "{section_key}": {{\n'
            
            for question_key, words in questions.items():
                q_num = question_key.replace("-savol so'zlari", "")
                py_code += f'            # {q_num}-savol\n'
                py_code += f'            "{question_key}": {{\n'
                
                for kr, uz in words.items():
                    py_code += f'                "{kr}": "{uz}",\n'
                
                py_code += '            },\n'
            
            py_code += '        },\n'
        
        py_code += '    },\n'
    
    py_code += '}\n'
    
    return py_code

# ============================================
# TIZIM MONITORING FUNKSIYALARI
# ============================================

def get_uptime():
    """Bot ishlash vaqti"""
    delta = datetime.now() - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def get_battery():
    """Batareya holati (Termux)"""
    try:
        out = subprocess.check_output(["termux-battery-status"], timeout=5).decode()
        return json.loads(out)
    except: 
        return None

def get_location_text(uid):
    """Hozirgi joying (%l)"""
    if uid not in user_context:
        return "❌ Hozir hech qayerda emasmiz"
    
    ctx = user_context[uid]
    location = []
    
    if ctx.get("topic"):
        topic_num = ctx["topic"].replace("Topik-", "")
        location.append(f"{topic_num}-topik")
    
    if ctx.get("section"):
        location.append(ctx["section"])
    
    if ctx.get("question"):
        q_info = ctx["question"].replace("-savol so'zlari", "")
        location.append(f"{q_info}-savol")
    
    if not location:
        return "❌ Hozir hech qayerda emasmiz"
    
    return "📍 " + " > ".join(location)

# ============================================
# KLAVIATURALAR
# ============================================

def get_main_keyboard():
    """Asosiy klaviatura"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("/start")
    markup.row("📂 BO'LIMLAR")
    markup.row("📥 JSON", "🐍 PYTHON")
    return markup

def get_help_text(lang='uz'):
    # Header qismi (ixcham va buzilmaydigan)
    header = (
        "<b>📚 LUG'AT BOT | ADMIN</b>\n"
        "<b>───────────────────</b>\n\n"
    )
    
    body = (
        "<b>1️⃣ BO'LIM YARATISH</b>\n"
        "👉 <code>>35 r,w,l</code>\n\n"
        
        "<b>2️⃣ SO'Z QO'SHISH</b>\n"
        "👉 <code>1</code> (savol)\n"
        "👉 <code>안녕 salom</code>\n\n"
        
        "<b>3️⃣ O'CHIRISH (rm.)</b>\n"
        "🗑 <code>rm.35r33</code> (savol)\n"
        "🗑 <code>rm.so'z</code> (so'z)\n\n"
        
        "<b>4️⃣ TIKLASH (rs.)</b>\n"
        "🔄 <code>rs.35r33</code>\n"
        "🔄 <code>rs.so'z</code>\n\n"
        
        "<b>5️⃣ QIDIRUV & MANZIL</b>\n"
        "🔍 <code>s.so'z</code> | 📍 <code>%l</code>\n\n"
        
        "<b>⚙️ TIZIM:</b> /status\n"
        "<b>━━━━━━━━━━━━━━━━━━</b>\n"
        "<i>💡 Buyruqni nusxalash uchun ustiga bosing.</i>"
    )
    
    return header + body

# ============================================
# /start VA /status HANDLERLAR
# ============================================

@bot.message_handler(commands=['start'])
def welcome_cmd(message):
    """Start komandasi"""
    bot.send_message(
        message.chat.id, 
        get_help_text(), 
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@bot.message_handler(commands=['status'])
def status_cmd(message):
    """Tizim holati"""
    bat = get_battery()
    ram = psutil.virtual_memory()
    
    msg = "<b>📊 TIZIM HOLATI</b>\n"
    msg += "<b>━━━━━━━━━━━━━━</b>\n\n"
    msg += f"⏱ Ishlash vaqti: {get_uptime()}\n\n"
    
    if bat:
        msg += f"🔋 Batareya: {bat.get('percentage', 0)}%\n"
        msg += f"🌡 Harorat: {bat.get('temperature', 0)}°C\n"
        msg += f"⚡ Holat: {bat.get('status', 'Unknown')}\n\n"
    else:
        msg += "🔋 Batareya: Termux API yo'q\n\n"
    
    msg += f"🧠 RAM: {ram.percent}%\n"
    msg += f"💾 RAM hajmi: {ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB\n\n"
    
    try:
        if os.path.exists(DATA_FILE):
            file_size = os.path.getsize(DATA_FILE)
            if file_size < 1024:
                size_str = f"{file_size}B"
            elif file_size < 1024**2:
                size_str = f"{file_size / 1024:.2f}KB"
            else:
                size_str = f"{file_size / (1024**2):.2f}MB"
            msg += f"📦 Lug'at hajmi: {size_str}"
    except:
        pass
    
    bot.send_message(message.chat.id, msg)

# ============================================
# EXPORT HANDLERLAR (JSON VA PYTHON)
# ============================================

@bot.message_handler(func=lambda m: m.text == "📥 JSON")
def export_json(message):
    """JSON fayl yuklash"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            bot.send_document(
                message.chat.id, 
                f, 
                caption="📥 Lug'at fayli (JSON format)"
            )
    else: 
        bot.send_message(message.chat.id, "❌ Lug'at bo'sh")

@bot.message_handler(func=lambda m: m.text == "🐍 PYTHON")
def export_python(message):
    """Python fayl yaratish va yuklash"""
    data = load_data()
    
    if not data:
        return bot.send_message(message.chat.id, "❌ Lug'at bo'sh")
    
    py_code = json_to_python()
    py_file = "dictionary.py"
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(py_code)
    
    with open(py_file, 'rb') as f:
        bot.send_document(
            message.chat.id,
            f,
            caption="🐍 Lug'at fayli (Python format)"
        )
    
    try:
        os.remove(py_file)
    except:
        pass

# ============================================
# BO'LIMLAR VA TOPIK KO'RISH HANDLERLAR
# ============================================

@bot.message_handler(func=lambda m: m.text == "📂 BO'LIMLAR")
def show_sections(message):
    """Barcha topiklar"""
    data = load_data()
    if not data: 
        return bot.send_message(message.chat.id, "❌ Lug'at bo'sh")
    
    msg = "📂 MAVJUD TOPIKLAR:\n\n"
    
    topics = []
    for topic_key in data.keys():
        if topic_key.startswith("Topik-"):
            topic_num = topic_key.replace("Topik-", "")
            if topic_num.isdigit():
                topics.append(int(topic_num))
    
    topics_sorted = sorted(topics)
    
    if not topics_sorted:
        return bot.send_message(message.chat.id, "❌ To'g'ri topiklar yo'q")
    
    for topic_num in topics_sorted:
        msg += f"/Topik{topic_num:02d}\n" if topic_num < 10 else f"/Topik{topic_num}\n"
    
    msg += "\n💡 Topikni tanlash uchun bosing"
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(regexp=r'^/Topik\d+$')
def show_topic_sections(message):
    """Topik ichidagi savol turlar"""
    topic_num_str = message.text.replace("/Topik", "")
    topic_num = int(topic_num_str)
    topic_key = f"Topik-{topic_num}"
    data = load_data()
    
    if topic_key not in data:
        return bot.send_message(
            message.chat.id, 
            f"❌ {topic_num}-topik topilmadi"
        )
    
    msg = f"📌 {topic_num}-TOPIK\n\n"
    
    sections = data[topic_key]
    if not sections:
        return bot.send_message(message.chat.id, f"❌ {topic_num}-topik bo'sh")
    
    if "reading" in sections:
        msg += f"/reading\n"
    if "writing" in sections:
        msg += f"/writing\n"
    if "listening" in sections:
        msg += f"/listening\n"
    
    msg += f"\n💡 Savol turini tanlash uchun bosing"
    
    uid = message.from_user.id
    if uid not in user_context:
        user_context[uid] = {}
    user_context[uid]["viewing_topic"] = topic_key
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['reading', 'writing', 'listening'])
def show_section_words(message):
    """Savol turi ichidagi so'zlar"""
    uid = message.from_user.id
    
    if uid not in user_context or "viewing_topic" not in user_context[uid]:
        return bot.send_message(
            message.chat.id,
            "⚠️ Avval topikni tanlang\n\n"
            "BO'LIMLAR tugmasini bosing"
        )
    
    section_name = message.text[1:]
    topic_key = user_context[uid]["viewing_topic"]
    topic_num = topic_key.replace("Topik-", "")
    
    data = load_data()
    
    if section_name not in data[topic_key]:
        return bot.send_message(
            message.chat.id, 
            f"❌ {section_name} topilmadi"
        )
    
    msg = f"📌 <b>{topic_num}-Topik > {section_name.upper()}</b>\n\n"
    
    questions = data[topic_key][section_name]
    if not questions:
        return bot.send_message(message.chat.id, f"❌ {section_name} bo'sh")
    
    for q_key in sorted(questions.keys(), key=lambda x: int(x.replace("-savol so'zlari", "")) if x.replace("-savol so'zlari", "").isdigit() else 0):
        words = questions[q_key]
        if words:
            q_num = q_key.replace("-savol so'zlari", "")
            msg += f"<code>{q_num}-savol so'zlari</code>\n"
            
            for kr, uz in words.items():
                msg += f"   <b>• {kr}</b> - <i>{uz}</i>\n"
            msg += "\n"
    
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# ============================================
# ASOSIY HANDLER (BARCHA MATNLAR - FULL VERSION)
# ============================================

@bot.message_handler(content_types=['text'])
def handle_all(message):
    """Admin buyruqlarini bo'sh joysiz va tezkor ishlashini ta'minlovchi handler"""
    text = message.text.strip().lower()
    
    # Komandalarni ignore qilish
    if text.startswith("/"):
        return
    
    uid = message.from_user.id
    data = load_data()
    
    # Contextni tekshirish
    if uid not in user_context:
        user_context[uid] = {}

    # --------------------------------------------
    # 1. HOZIRGI JOY (%l)
    # --------------------------------------------
    if text == "%l":
        topic = user_context[uid].get("topic", "Tanlanmagan")
        section = user_context[uid].get("section", "Tanlanmagan")
        question = user_context[uid].get("question", "Tanlanmagan")
        
        bot.send_message(
            message.chat.id, 
            f"📍 Hozirgi manzilingiz:\n\n"
            f"📂 Topik: {topic}\n"
            f"📖 Bo'lim: {section}\n"
            f"📑 Savol: {question}"
        )
        return
    # ============================================
    # TIKLASH (rs.35, rs.35r, rs.so'z)
    # ============================================
    if text.lower().startswith("rs."):
        target = text[3:].strip()
        
        # Topikni tiklash (rs.35)
        if target.isdigit():
            topic_num = int(target)
            backup_file = f"backup_topik_{topic_num}.json"
            
            if not os.path.exists(backup_file):
                return bot.send_message(
                    message.chat.id,
                    f"❌ {topic_num}-topik uchun backup topilmadi"
                )
            
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    topic_data = json.load(f)
                
                topic_key = f"Topik-{topic_num}"
                data[topic_key] = topic_data
                save_data(data)
                
                os.remove(backup_file)
                
                bot.send_message(
                    message.chat.id,
                    f"✅ {topic_num}-topik tiklandi!"
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Xatolik: {e}")
            return
        
        # Bo'limni tiklash (rs.35r)
        if len(target) >= 2 and target[:-1].isdigit() and target[-1] in ['r', 'w', 'l']:
            topic_num = int(target[:-1])
            section_code = target[-1]
            section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
            section_name = section_map[section_code]
            
            backup_file = f"backup_{topic_num}_{section_name}.json"
            
            if not os.path.exists(backup_file):
                return bot.send_message(
                    message.chat.id,
                    f"❌ {topic_num}-topik > {section_name} uchun backup topilmadi"
                )
            
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    section_data = json.load(f)
                
                topic_key = f"Topik-{topic_num}"
                if topic_key not in data:
                    data[topic_key] = {}
                
                data[topic_key][section_name] = section_data
                save_data(data)
                
                os.remove(backup_file)
                
                bot.send_message(
                    message.chat.id,
                    f"✅ {topic_num}-topik > {section_name} tiklandi!"
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Xatolik: {e}")
            return
        # Savolni tiklash (rs.35r33)
        if any(c in target for c in ['r', 'w', 'l']) and target[-1].isdigit() and len(target) > 3:
            backup_file = f"backup_q_{target}.json"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        b = json.load(f)
                    
                    t_k, s_k, q_k = b['topic'], b['section'], b['question_key']
                    if t_k not in data: data[t_k] = {}
                    if s_k not in data[t_k]: data[t_k][s_k] = {}
                    
                    # Savolni asl joyiga (o'z kaliti bilan) qaytarish
                    data[t_k][s_k][q_k] = b['content']
                    save_data(data)
                    os.remove(backup_file)
                    bot.send_message(message.chat.id, f"✅ {target} savoli o'z joyiga tiklandi!")
                except Exception as e:
                    bot.send_message(message.chat.id, f"❌ Xato: {e}")
                return
        
        # So'zni tiklash (rs.so'z)
        safe_name = "".join(x for x in target if x.isalnum())
        backup_file = f"backup_word_{safe_name}.json"
        
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    b = json.load(f)
                
                t_k, s_k, q_k = b['topic'], b['section'], b['question']
                kor, uz = b['korean'], b['uzbek']
                
                # Ierarxiya buzilgan bo'lsa tiklab ketish
                if t_k not in data: data[t_k] = {}
                if s_k not in data[t_k]: data[t_k][s_k] = {}
                if q_k not in data[t_k][s_k]: data[t_k][s_k][q_k] = {}
                
                # So'zni o'zining asl joyiga qo'yish
                data[t_k][s_k][q_k][kor] = uz
                save_data(data)
                os.remove(backup_file)
                
                bot.send_message(
                    message.chat.id, 
                    f"✅ So'z o'z joyiga tiklandi!\n\n📍 {t_k} ➔ {s_k} ➔ {q_k}\n🇰🇷 {kor} = 🇺🇿 {uz}"
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Tiklashda xatolik: {e}")
            return

    # ============================================
    # O'CHIRISH (rm.apple yoki rm.35 yoki rm.35r)
    # ============================================
    if text.lower().startswith("rm."):
        target = text[3:].strip()
        
        # Bo'limni o'chirish (rm.35r, rm.35w, rm.35l)
        if len(target) >= 2 and target[:-1].isdigit() and target[-1] in ['r', 'w', 'l']:
            topic_num = int(target[:-1])
            section_code = target[-1]
            topic_key = f"Topik-{topic_num}"
            
            section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
            section_name = section_map[section_code]
            
            if topic_key in data and section_name in data[topic_key]:
                # Backup yaratish
                backup_file = f"backup_{topic_num}_{section_name}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data[topic_key][section_name], f, ensure_ascii=False, indent=4)
                
                del data[topic_key][section_name]
                save_data(data)
                bot.send_message(
                    message.chat.id, 
                    f"🗑 {topic_num}-topik > {section_name} o'chirildi\n\n"
                    f"💡 Qaytarish: rs.{topic_num}{section_code}"
                )
            else:
                bot.send_message(
                    message.chat.id, 
                    f"❌ {topic_num}-topik > {section_name} topilmadi"
                )
            return
        
        # Topikni o'chirish (rm.35)
        if target.isdigit():
            topic_num = int(target)
            topic_key = f"Topik-{topic_num}"
            
            if topic_key in data:
                # Backup yaratish
                backup_file = f"backup_topik_{topic_num}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data[topic_key], f, ensure_ascii=False, indent=4)
                
                del data[topic_key]
                save_data(data)
                bot.send_message(
                    message.chat.id, 
                    f"🗑 {topic_num}-topik o'chirildi\n\n"
                    f"💡 Qaytarish: rs.{topic_num}"
                )
            else:
                bot.send_message(message.chat.id, f"❌ {topic_num}-topik topilmadi")
            return
        # Savolni o'chirish (rm.35r33)
        pattern_q = re.match(r'^(\d+)([rwl])(\d+)$', target)
        if pattern_q:
            topic_num = int(pattern_q.group(1))
            section_code = pattern_q.group(2)
            q_num = pattern_q.group(3)
            
            topic_key = f"Topik-{topic_num}"
            section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
            section_name = section_map[section_code]
            q_key = f"{q_num}-savol so'zlari"
            
            if topic_key in data and section_name in data[topic_key] and q_key in data[topic_key][section_name]:
                # Backup yaratish
                backup_info = {
                    'type': 'question',
                    'topic': topic_key,
                    'section': section_name,
                    'question_key': q_key,
                    'content': data[topic_key][section_name][q_key]
                }
                backup_file = f"backup_q_{target}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_info, f, ensure_ascii=False, indent=4)
                
                del data[topic_key][section_name][q_key]
                save_data(data)
                bot.send_message(message.chat.id, f"🗑 {topic_num}-topik > {section_name} > {q_num}-savol o'chirildi\n\n💡 Qaytarish: rs.{target}")
            else:
                bot.send_message(message.chat.id, "❌ Bunday savol topilmadi")
            return
        
        # So'zni o'chirish (rm.so'z)
        word_to_rm = target.lower()
        found = False
        
        for t in data:
            for s in data[t]:
                for q in data[t][s]:
                    match_key = None
                    if word_to_rm in [k.lower() for k in data[t][s][q].keys()]:
                        match_key = next(k for k in data[t][s][q].keys() if k.lower() == word_to_rm)
                    elif word_to_rm in [v.lower() for v in data[t][s][q].values()]:
                        match_key = next(k for k, v in data[t][s][q].items() if v.lower() == word_to_rm)

                    if match_key:
                        backup_info = {
                            'type': 'word', 'topic': t, 'section': s, 'question': q,
                            'korean': match_key, 'uzbek': data[t][s][q][match_key]
                        }
                        safe_name = "".join(x for x in word_to_rm if x.isalnum())
                        backup_file = f"backup_word_{safe_name}.json"
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            json.dump(backup_info, f, ensure_ascii=False, indent=4)
                        
                        del data[t][s][q][match_key]
                        save_data(data)
                        msg = (f"🗑 So'z o'chirildi: <b>{match_key}</b>\n\n"
                               f"📍 Manzil: {t} ➔ {s} ➔ {q}\n"
                               f"💡 Qaytarish: <code>rs.{word_to_rm}</code>")
                        bot.send_message(message.chat.id, msg, parse_mode="HTML")
                        found = True
                        break
                if found: break
            if found: break
        
        if not found:
            bot.send_message(message.chat.id, "❌ Lug'atda bunday so'z topilmadi")
        return
   # --------------------------------------------
    # 2. ">" BILAN BOSHLANUVCHI BUYRUQLAR 
    # --------------------------------------------
    if text.startswith(">"):
        match = re.match(r">(\d+)([rwl,]+)?(\d+)?(\.)?", text)
        
        if not match:
            return bot.send_message(message.chat.id, "❌ Noto'g'ri format! Masalan: >35r1 yoki >35r1.")
        
        t_num, sec_codes, q_num, view_mode = match.groups()
        topic_key = f"Topik-{t_num}"
        section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
        
        # --- KO'RIB CHIQISH REJIMI (>35. yoki >35r. yoki >35r1.) ---
        if view_mode == ".":
            if topic_key not in data:
                return bot.send_message(message.chat.id, f"❌ {topic_key} bazada yo'q")
            
            if sec_codes and q_num:
                sec_name = section_map.get(sec_codes[0])
                q_key = f"{q_num}-savol so'zlari"
                words = data.get(topic_key, {}).get(sec_name, {}).get(q_key, {})
                if not words: 
                    return bot.send_message(message.chat.id, "⚠️ Bu savolda so'zlar yo'q.")
                res = f"📑 {topic_key} > {sec_name} > {q_num}-savol:\n\n"
                res += "\n".join([f"🇰🇷 {k} - 🇺🇿 {v}" for k, v in words.items()])
                bot.send_message(message.chat.id, res)
            
            elif sec_codes:
                sec_name = section_map.get(sec_codes[0])
                chapters = list(data.get(topic_key, {}).get(sec_name, {}).keys())
                if not chapters: return bot.send_message(message.chat.id, "⚠️ Bo'lim bo'sh.")
                bot.send_message(message.chat.id, f"📂 {topic_key} > {sec_name} savollari:\n\n" + "\n".join(chapters))
            
            else:
                secs = list(data.get(topic_key, {}).keys())
                if not secs: return bot.send_message(message.chat.id, "⚠️ Topik bo'sh.")
                bot.send_message(message.chat.id, f"📚 {topic_key} bo'limlari:\n\n" + "\n".join([f"• {s}" for s in secs]))
            return

        # --- YARATISH VA O'TISH REJIMI (TANLANDI / YARATILDI) ---
        is_new = False
        
        # 1. Topikni tekshirish
        if topic_key not in data:
            data[topic_key] = {}
            is_new = True
        user_context[uid]["topic"] = topic_key
        
        # 2. Bo'limlarni tekshirish
        active_sec = None
        if sec_codes:
            codes = sec_codes.replace(",", "")
            for c in codes:
                s_name = section_map.get(c)
                if s_name:
                    if s_name not in data[topic_key]:
                        data[topic_key][s_name] = {}
                        is_new = True
                    if not active_sec: active_sec = s_name
            user_context[uid]["section"] = active_sec
        
        # 3. Savol raqamini tekshirish
        if q_num:
            q_key = f"{q_num}-savol so'zlari"
            if active_sec:
                if q_key not in data[topic_key][active_sec]:
                    data[topic_key][active_sec][q_key] = {}
                    is_new = True
                user_context[uid]["question"] = q_key
        # Savollarni raqam bo'yicha tartiblash (1, 2, 3... 10, 20)
        if active_sec and topic_key in data and active_sec in data[topic_key]:
            # Savollarni kalitidagi raqamga qarab saralaymiz
            sorted_questions = dict(sorted(
                data[topic_key][active_sec].items(),
                key=lambda x: int(re.search(r'\d+', x[0]).group()) if re.search(r'\d+', x[0]) else 0
            ))
            data[topic_key][active_sec] = sorted_questions
        
        save_data(data)
        
        # Holatga qarab status tanlash
        status = "yaratildi ✨" if is_new else "tanlandi ✅"
        
        # Bildirishnoma
        loc = f"📍 {topic_key}"
        if active_sec: loc += f" > {active_sec}"
        if q_num: loc += f" > {q_num}-savol"
        
        bot.send_message(message.chat.id, f"{loc} {status}")
        return
        # Savol raqamini o'rnatish
        if q_num:
            q_key = f"{q_num}-savol so'zlari"
            if active_sec:
                if q_key not in data[topic_key][active_sec]:
                    data[topic_key][active_sec][q_key] = {}
                user_context[uid]["question"] = q_key
        
        save_data(data)
        
        # Natija haqida bildirishnoma
        loc = f"📍 {topic_key}"
        if active_sec: loc += f" > {active_sec}"
        if q_num: loc += f" > {q_num}-savol"
        bot.send_message(message.chat.id, f"{loc} tanlandi/yaraldi ✅")
        return

    # --------------------------------------------
    # 3. TAHRIRLASH (eski.yangi) VA QIDIRISH (s.so'z)
    # --------------------------------------------
    if "." in text and not text.startswith((">")):
        # QIDIRISH (s.so'z)
        if text.startswith("s."):
            query = text[2:].strip()
            found = False
            res = f"🔍 '{query}' uchun qidiruv natijalari:\n\n"
            
            for t, secs in data.items():
                for s, chapters in secs.items():
                    for ch, words in chapters.items():
                        for k, v in words.items():
                            if query in k or query in v:
                                res += f"📍 {t}>{s}>{ch}\n🇰🇷 {k} - 🇺🇿 {v}\n\n"
                                found = True
            
            if not found:
                bot.send_message(message.chat.id, "❌ Hech narsa topilmadi.")
            else:
                bot.send_message(message.chat.id, res)
            return

        # TAHRIRLASH (eski.yangi)
        parts = text.split(".")
        if len(parts) == 2:
            old_w, new_w = parts[0].strip(), parts[1].strip()
            
            t = user_context[uid].get("topic")
            s = user_context[uid].get("section")
            q = user_context[uid].get("question")
            
            if q and t in data and s in data[t] and q in data[t][s]:
                if old_w in data[t][s][q]:
                    # Qiymatni saqlab qolib, kalitni o'zgartirish (agar yangisi koreyscha bo'lsa)
                    # Yoki faqat tarjimani o'zgartirish. Bu yerda kalitni o'zgartiramiz:
                    val = data[t][s][q].pop(old_w)
                    data[t][s][q][new_w] = val
                    save_data(data)
                    bot.send_message(message.chat.id, f"🔄 Tahrirlandi: {old_w} -> {new_w}")
                else:
                    bot.send_message(message.chat.id, f"❌ '{old_w}' hozirgi savolda topilmadi.")
            else:
                bot.send_message(message.chat.id, "⚠️ Tahrirlash uchun avval savolga kiring.")
            return

    # --------------------------------------------
    # 4. SAVOL RAQAMI (Faqat raqam kiritilsa: 1)
    # --------------------------------------------
    if text.isdigit():
        if user_context[uid].get("section"):
            q_key = f"{text}-savol so'zlari"
            t = user_context[uid]["topic"]
            s = user_context[uid]["section"]
            
            if q_key not in data[t][s]:
                data[t][s][q_key] = {}
                save_data(data)
                
            user_context[uid]["question"] = q_key
            bot.send_message(message.chat.id, f"📝 {text}-savol tanlandi. So'zlarni yuboring:")
        else:
            bot.send_message(message.chat.id, "⚠️ Avval bo'limni tanlang (Masalan: >35r)")
        return

    # --------------------------------------------
    # 5. SO'Z QO'SHISH (QAT'IY NAZORAT VA HISOBOT)
    # --------------------------------------------
    if " " in text and not text.startswith(">") and not text.isdigit() and not text.startswith("s."):
        t = user_context[uid].get("topic")
        s = user_context[uid].get("section")
        q = user_context[uid].get("question")
        
        # 🛑 QAT'IY TEKSHIRUV: Agar manzil to'liq bo'lmasa
        if not t or not s or not q:
            current_loc = get_location_text(uid)
            msg = f"⚠️ **XATO MANZIL!**\n\n"
            msg += f"Siz hozir bu yerdasiz: {current_loc}\n"
            msg += "So'z qo'shish uchun aniq **Topik**, **Bo'lim** va **Savol raqami** tanlangan bo'lishi shart!\n\n"
            msg += "💡 Masalan: `>36r1` buyrug'i orqali hammasini bittada sozlang."
            return bot.send_message(message.chat.id, msg, parse_mode="Markdown")

        lines = message.text.strip().split('\n')
        added_count = 0
        added_words_list = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Tillar almashish nuqtasini qidirish
            split_match = re.search(r'([가-힣])\s+([a-zA-Z])|([a-zA-Z])\s+([가-힣])', line)
            
            if split_match:
                idx = split_match.start(0) + 1
                part1 = line[:idx].strip()
                part2 = line[idx:].strip()
                
                if re.search(r'[가-힣]', part1):
                    kor, uzb = part1, part2
                else:
                    kor, uzb = part2, part1
            else:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    p1, p2 = parts[0].strip(), parts[1].strip()
                    if re.search(r'[가-힣]', p1): kor, uzb = p1, p2
                    else: kor, uzb = p2, p1
                else:
                    continue

            # Bazaga saqlash
            if t not in data: data[t] = {}
            if s not in data[t]: data[t][s] = {}
            if q not in data[t][s]: data[t][s][q] = {}
            
            data[t][s][q][kor] = uzb
            added_words_list.append(f"• {kor} - {uzb}")
            added_count += 1
        
        # ✅ NATIJA VA HISOBOT
        if added_count > 0:
            save_data(data)
            
            # Savol raqamini chiroyli ko'rinishga keltirish (SyntaxError'siz)
            # Savol kalitidagi " so'zlari" qismini olib tashlaymiz
            clean_q = q.replace(" so'zlari", "") 
            
            report = f"✅ **{added_count} ta so'z saqlandi!**\n\n"
            report += "\n".join(added_words_list)
            report += f"\n\n📍 **Manzil:** {t} > {s.upper()} > {clean_q}"
            
            bot.send_message(message.chat.id, report, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Format xato! Koreyscha va O'zbekcha so'zlar topilmadi.")
        return

    # ============================================
    # QIDIRISH (s.apple)
    # ============================================
    if text.lower().startswith("s."):
        query = text[2:].strip().lower()
        results = []
        
        for t, s_dict in data.items():
            topic_num = t.replace("Topik-", "")
            for s, q_dict in s_dict.items():
                for q, w_dict in q_dict.items():
                    q_num = q.replace("-savol so'zlari", "")
                    for kr, uz in w_dict.items():
                        if query in kr.lower() or query in uz.lower():
                            results.append(f"🔍 {topic_num}-topik > {s.upper()} > {q_num}-savol: {kr} → {uz}")
        
        if results:
            msg = "🔍 TOPILDI:\n\n" + "\n\n".join(results)
        else:
            msg = "❌ Topilmadi"
        
        bot.send_message(message.chat.id, msg)
        return

    # ============================================
    # O'ZGARTIRISH (word.new_word)
    # ============================================
    if "." in text and not text.endswith(".") and not text.startswith(".") and not text.startswith("rs.") and not text.startswith("rm.") and not text.startswith("s."):
        parts = text.split(".", 1)
        if len(parts) == 2:
            old_w, new_w = [i.strip() for i in parts]
            found = False
            backup_info = None
            
            for t in data:
                for s in data[t]:
                    for q in data[t][s]:
                        if old_w in data[t][s][q]:
                            # Backup yaratish
                            backup_info = {
                                'topic': t,
                                'section': s,
                                'question': q,
                                'korean': old_w,
                                'uzbek': data[t][s][q][old_w]
                            }
                            backup_file = f"backup_word_{old_w}.json"
                            with open(backup_file, 'w', encoding='utf-8') as f:
                                json.dump(backup_info, f, ensure_ascii=False, indent=4)
                            
                            data[t][s][q][old_w] = new_w
                            found = True
                            break
                        else:
                            for kr, uz in list(data[t][s][q].items()):
                                if uz == old_w:
                                    # Backup yaratish
                                    backup_info = {
                                        'topic': t,
                                        'section': s,
                                        'question': q,
                                        'korean': kr,
                                        'uzbek': uz
                                    }
                                    backup_file = f"backup_word_{old_w}.json"
                                    with open(backup_file, 'w', encoding='utf-8') as f:
                                        json.dump(backup_info, f, ensure_ascii=False, indent=4)
                                    
                                    data[t][s][q].pop(kr)
                                    data[t][s][q][new_w] = uz
                                    found = True
                                    break
                    
                    if found:
                        break
                
                if found:
                    break
            
            if found:
                save_data(data)
                bot.send_message(
                    message.chat.id, 
                    f"✅ Yangilandi\n\n"
                    f"💡 Qaytarish: rs.{old_w}"
                )
            else: 
                bot.send_message(message.chat.id, "❌ Topilmadi")
            return

    # ============================================
    # SAVOL RAQAMI VA SO'ZLAR (ko'p qatorli) - TUZATILGAN!
    # ============================================
    lines = text.splitlines()  # split("\n") o'rniga splitlines()
    
    # Birinchi qator - savol raqami
    first_line = lines[0].strip()
    
    if first_line.isdigit() and len(lines) > 1:
        # Context tekshirish
        if uid not in user_context or not user_context[uid].get("topic") or not user_context[uid].get("section"):
            return bot.send_message(
                message.chat.id,
                "⚠️ Avval topik va bo'lim kiriting\n\n"
                "Misol: >35 r"
            )
        
        q_num = first_line
        q_key = f"{q_num}-savol so'zlari"
        
        topic_key = user_context[uid]["topic"]
        section_key = user_context[uid]["section"]
        topic_num = topic_key.replace("Topik-", "")
        
        # Savol yaratish
        if q_key not in data[topic_key][section_key]:
            data[topic_key][section_key][q_key] = {}
        
        user_context[uid]["question"] = q_key
        
        # So'zlarni qo'shish (parse_multiline_words funksiyasidan foydalanish)
        words_text = "\n".join(lines[1:])  # Birinchi qatordan keyingilar
        parsed_words = parse_multiline_words(words_text)
        
        added = 0
        for word in parsed_words:
            data[topic_key][section_key][q_key][word['korean']] = word['uzbek']
            added += 1
        
        if added > 0:
            save_data(data)
            bot.send_message(
                message.chat.id,
                f"✅ {topic_num}-topik > {section_key} > {q_num}-savol so'zlari saqlandi\n"
                f"📊 {added} ta so'z qo'shildi"
            )
        else:
            bot.send_message(message.chat.id, "❌ Hech qanday so'z qo'shilmadi")
        
        return

# ============================================
# MONITORING (Avtomatik)
# ============================================

def auto_monitor():
    """Avtomatik monitoring"""
    while True:
        try:
            bat = get_battery()
            ram = psutil.virtual_memory()
            
            if bat and ADMIN_ID:
                if bat.get('percentage', 100) <= 10:
                    bot.send_message(ADMIN_ID, "⚠️ Batareya 10%!")
            
            if ram.percent >= 90 and ADMIN_ID:
                bot.send_message(ADMIN_ID, f"⚠️ RAM {ram.percent}%!")
        except: 
            pass
        time.sleep(600)

threading.Thread(target=auto_monitor, daemon=True).start()
#==============================================
# BACKUP FAYLLARNI HAR 12 SOATDA AVTO O'CHIRISH
#==============================================

def clean_old_backups(hours=12):
    """Eski backup fayllarni har 12 soatda avtomatik o'chirish"""
    while True:
        try:
            now = time.time()
            cutoff = now - (hours * 3600)  # 12 soatni soniyaga o'tkazish
            
            files = os.listdir('.')
            deleted_count = 0
            
            for f in files:
                # Faqat backup_ bilan boshlanadigan json fayllarni tekshiramiz
                if f.startswith("backup_") and f.endswith(".json"):
                    file_path = os.path.join('.', f)
                    # Agar fayl yaratilgan vaqt cutoff dan eski bo'lsa
                    if os.path.getmtime(file_path) < cutoff:
                        os.remove(file_path)
                        deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 Tozalash: {deleted_count} ta eski backup fayl o'chirildi.")
                
        except Exception as e:
            print(f"❌ Tozalashda xato: {e}")
            
        # 1 soat kutib qayta tekshiradi (serverni qiynamaslik uchun)
        time.sleep(3600)
if __name__ == "__main__":
    # Tozalash funksiyasini alohida oqimda ishga tushiramiz
    cleanup_thread = threading.Thread(target=clean_old_backups, args=(12,), daemon=True)
    cleanup_thread.start()
    
    # Botni ishga tushirish
    try:
        print("✅ Bot va Avto-tozalash tizimi ishga tushdi!")
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot to'xtadi: {e}")

# ============================================
# ISHGA TUSHIRISH
# ============================================

if __name__ == "__main__":
    try:
        me = bot.get_me()
        print(f"\n{'='*40}")
        print(f"BOT: @{me.username}")
        print(f"STATUS: RUNNING ✅")
        print(f"{'='*40}\n")
        bot.infinity_polling()
    except Exception as e: 
        print(f"ERROR: {e}")