# -*- coding: utf-8 -*-
"""
KOREAN-O'ZBEK LUG'AT BOT
Yangilangan versiya - 2026
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

def get_help_text():
    """Yordam matni"""
    return (
        "╔═══════════════════════╗\n"
        "║    📚 LUG'AT BOT       ║\n"
        "╚═══════════════════════╝\n\n"
        
        "1️⃣ TOPIK + BO'LIM YARATISH\n"
        "   >35 r (reading)\n"
        "   >35 w (writing)\n"
        "   >35 l (listening)\n"
        "   >35 r,w,l (hammasi)\n\n"
        
        "2️⃣ SAVOL + SO'ZLAR\n"
        "   1\n"
        "   안녕 salom\n"
        "   밥을 먹다 ovqat yemoq\n\n"
        
        "3️⃣ TEZKOR KIRISH\n"
        "   >35 r 1 (mavjudga)\n\n"
        
        "4️⃣ KO'RIB CHIQISH\n"
        "   >35. (so'zlarni ko'rish)\n\n"
        
        "5️⃣ HOZIRGI JOYING\n"
        "   %l\n\n"
        
        "6️⃣ SO'ZNI O'ZGARTIRISH\n"
        "   eski.yangi\n\n"
        
        "7️⃣ O'CHIRISH\n"
        "   rm.so'z\n"
        "   rm.35 (topik)\n\n"
        
        "8️⃣ QIDIRISH\n"
        "   s.so'z\n\n"
        
        "9️⃣ TIZIM\n"
        "   /status\n\n"
        "<restore function>\n"
            "rs.topik\n"
            "rs.r,w,l\n"
            "rs.word\n"

        
        
    )

# ============================================
# /start VA /status HANDLERLAR
# ============================================

@bot.message_handler(commands=['start'])
def welcome_cmd(message):
    """Start komandasi"""
    bot.send_message(
        message.chat.id, 
        get_help_text(), 
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['status'])
def status_cmd(message):
    """Tizim holati"""
    bat = get_battery()
    ram = psutil.virtual_memory()
    
    msg = "╔═══════════════════════╗\n"
    msg += "║   📊 TIZIM HOLATI      ║\n"
    msg += "╚═══════════════════════╝\n\n"
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
    
    bot.send_message(message.chat.id, msg,parse_mode="HTML")

# ============================================
# ASOSIY HANDLER (BARCHA MATNLAR)
# ============================================

@bot.message_handler(content_types=['text'])
def handle_all(message):
    """Barcha xabarlarni qayta ishlash"""
    text = message.text.strip()
    
    # Komandalarni ignore qilish
    if text.startswith("/"):
        return
    
    uid = message.from_user.id
    data = load_data()

    # ============================================
    # HOZIRGI JOYING (%l)
    # ============================================
    if text == "%l":
        bot.send_message(message.chat.id, get_location_text(uid))
        return

    # ============================================
    # KO'RIB CHIQISH (>35.)
    # ============================================
    if text.startswith(">") and text.endswith(".") and len(text) > 2:
        topic_num_str = text[1:-1].strip()
        
        try:
            topic_num = int(topic_num_str)
        except:
            return bot.send_message(message.chat.id, "❌ Noto'g'ri topik raqami")
        
        topic_name = f"Topik-{topic_num}"
        
        if topic_name not in data:
            return bot.send_message(
                message.chat.id,
                f"❌ {topic_num}-topik topilmadi"
            )
        
        sections = data[topic_name]
        if not sections:
            return bot.send_message(message.chat.id, f"❌ {topic_num}-topik bo'sh")
        
        msg = f"📌 {topic_num}-TOPIK\n\n"
        
        if "reading" in sections:
            msg += f"/reading\n"
        if "writing" in sections:
            msg += f"/writing\n"
        if "listening" in sections:
            msg += f"/listening\n"
        
        msg += f"\n💡 Savol turini tanlash uchun bosing"
        
        if uid not in user_context:
            user_context[uid] = {}
        user_context[uid]["viewing_topic"] = topic_name
        
        bot.send_message(message.chat.id, msg)
        return

    # ============================================
    # TOPIK + BO'LIM YARATISH (>35 r)
    # YOKI TEZKOR KIRISH (>35 r 1)
    # ============================================
    if text.startswith(">"):
        parts = text[1:].strip().split()
        
        if len(parts) < 2:
            return bot.send_message(
                message.chat.id,
                "❌ Format: >35 r yoki >35 r 1"
            )
        
        # Topik raqami
        try:
            topic_num = int(parts[0])
        except:
            return bot.send_message(message.chat.id, "❌ Noto'g'ri topik raqami")
        
        topic_key = f"Topik-{topic_num}"
        
        # Bo'limlar
        section_codes = parts[1].split(',')
        section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
        sections = []
        
        for code in section_codes:
            code = code.strip().lower()
            if code in section_map:
                sections.append(section_map[code])
            else:
                return bot.send_message(
                    message.chat.id,
                    "❌ Noto'g'ri bo'lim kodi (r, w, l)"
                )
        
        # TEZKOR KIRISH (>35 r 1)
        if len(parts) == 3:
            question_num = parts[2]
            
            if not question_num.isdigit():
                return bot.send_message(
                    message.chat.id,
                    "❌ Savol raqami noto'g'ri"
                )
            
            # Tekshirish
            if topic_key not in data:
                return bot.send_message(
                    message.chat.id,
                    f"❌ {topic_num}-topik topilmadi"
                )
            
            section_name = sections[0]  # Birinchi bo'lim
            
            if section_name not in data[topic_key]:
                return bot.send_message(
                    message.chat.id,
                    f"❌ {section_name} topilmadi"
                )
            
            q_key = f"{question_num}-savol so'zlari"
            
            if q_key not in data[topic_key][section_name]:
                return bot.send_message(
                    message.chat.id,
                    f"❌ {question_num}-savol topilmadi"
                )
            
            # Context o'rnatish
            if uid not in user_context:
                user_context[uid] = {}
            
            user_context[uid]["topic"] = topic_key
            user_context[uid]["section"] = section_name
            user_context[uid]["question"] = q_key
            
            bot.send_message(
                message.chat.id,
                f"✅ {topic_num}-topik > {section_name} > {question_num}-savol so'zlari tanlandi\n"
                f"Yangi so'zni qo'shing:"
            )
            return
        
        # ODDIY YARATISH (>35 r)
        # Topik yaratish
        if topic_key not in data:
            data[topic_key] = {}
        
        # Bo'limlarni yaratish
        created_sections = []
        for section_name in sections:
            if section_name not in data[topic_key]:
                data[topic_key][section_name] = {}
                created_sections.append(section_name)
        
        save_data(data)
        
        # Context o'rnatish
        if uid not in user_context:
            user_context[uid] = {}
        
        user_context[uid]["topic"] = topic_key
        user_context[uid]["section"] = sections[0]  # Birinchi bo'lim
        user_context[uid]["question"] = None
        
        section_names = ", ".join(created_sections) if created_sections else ", ".join(sections)
        
        bot.send_message(
            message.chat.id,
            f"✅ {topic_num}-topik > {section_names} bo'limi yaratildi\n"
            f"Endi savol raqami va so'zlarni kiriting:"
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
        
        # So'zni tiklash (rs.so'z)
        word_to_restore = target
        backup_file = f"backup_word_{word_to_restore}.json"
        
        if not os.path.exists(backup_file):
            return bot.send_message(
                message.chat.id,
                f"❌ '{word_to_restore}' uchun backup topilmadi"
            )
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                word_backup = json.load(f)
            
            # Asl joyiga qaytarish
            topic_key = word_backup['topic']
            section_key = word_backup['section']
            question_key = word_backup['question']
            korean = word_backup['korean']
            uzbek = word_backup['uzbek']
            
            if topic_key not in data:
                data[topic_key] = {}
            if section_key not in data[topic_key]:
                data[topic_key][section_key] = {}
            if question_key not in data[topic_key][section_key]:
                data[topic_key][section_key][question_key] = {}
            
            data[topic_key][section_key][question_key][korean] = uzbek
            save_data(data)
            
            os.remove(backup_file)
            
            bot.send_message(
                message.chat.id,
                f"✅ So'z tiklandi: {korean} → {uzbek}"
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Xatolik: {e}")
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
        
        # So'zni o'chirish
        word_to_rm = target.lower()
        found = False
        backup_info = None
        
        for t in data:
            for s in data[t]:
                for q in data[t][s]:
                    # Korean kalit bo'yicha qidirish
                    to_del = [k for k in data[t][s][q] if k.lower() == word_to_rm]
                    for k in to_del:
                        # Backup yaratish
                        backup_info = {
                            'topic': t,
                            'section': s,
                            'question': q,
                            'korean': k,
                            'uzbek': data[t][s][q][k]
                        }
                        backup_file = f"backup_word_{word_to_rm}.json"
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            json.dump(backup_info, f, ensure_ascii=False, indent=4)
                        
                        del data[t][s][q][k]
                        found = True
                        break
                    
                    if found:
                        break
                    
                    # O'zbek qiymat bo'yicha qidirish
                    to_del_v = [k for k, v in data[t][s][q].items() if v.lower() == word_to_rm]
                    for k in to_del_v:
                        # Backup yaratish
                        backup_info = {
                            'topic': t,
                            'section': s,
                            'question': q,
                            'korean': k,
                            'uzbek': data[t][s][q][k]
                        }
                        backup_file = f"backup_word_{word_to_rm}.json"
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            json.dump(backup_info, f, ensure_ascii=False, indent=4)
                        
                        del data[t][s][q][k]
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
                f"🗑 O'chirildi: {word_to_rm}\n\n"
                f"💡 Qaytarish: rs.{word_to_rm}"
            )
        else: 
            bot.send_message(message.chat.id, "❌ Topilmadi")
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
    # SAVOL RAQAMI VA SO'ZLAR (ko'p qatorli)
    # ============================================
    # Format:
    # 1
    # 안녕 salom
    # 밥을/먹다 ovqat yemoq
    
    lines = text.split("\n")
    
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
        
        # So'zlarni qo'shish (2-qatordan boshlab)
        added = 0
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # / belgisini bo'sh joyga almashtirish
            line_cleaned = line.replace("/", " ")
            
            # Korean va O'zbek so'zlarni ajratish
            korean_part = ""
            uzbek_part = ""
            
            words = line_cleaned.split()
            for word in words:
                if is_korean(word):
                    korean_part += word + " "
                else:
                    uzbek_part += word + " "
            
            korean_part = korean_part.strip()
            uzbek_part = uzbek_part.strip()
            
            # Ikkala til ham bo'lishi kerak
            if not korean_part or not uzbek_part:
                continue
            
            data[topic_key][section_key][q_key][korean_part] = uzbek_part
            added += 1
        
        if added > 0:
            save_data(data)
            bot.send_message(
                message.chat.id,
                f"✅ {topic_num}-topik > {section_key} > {q_num}-savol so'zlari saqlandi"
            )
        else:
            bot.send_message(message.chat.id,parsemode="HTML" "❌ Hech qanday so'z qo'shilmadi")
        
        return

    # ============================================
    # SO'Z QO'SHISH (oddiy)
    # ============================================
    if uid in user_context and user_context[uid].get("topic") and user_context[uid].get("section") and user_context[uid].get("question"):
        t_k = user_context[uid]["topic"]
        s_k = user_context[uid]["section"]
        q_k = user_context[uid]["question"]
        
        # / belgisini bo'sh joyga almashtirish
        text_cleaned = text.replace("/", " ")
        
        # Korean va O'zbek so'zlarni ajratish
        korean_part = ""
        uzbek_part = ""
        
        words = text_cleaned.split()
        for word in words:
            if is_korean(word):
                korean_part += word + " "
            else:
                uzbek_part += word + " "
        
        korean_part = korean_part.strip()
        uzbek_part = uzbek_part.strip()
        
        # Tekshirish
        if not korean_part or not uzbek_part:
            return bot.send_message(
                message.chat.id,
                "❌ Korean va O'zbek so'zlar bo'lishi kerak\n\n"
                "To'g'ri:\n"
                "안녕 salom\n"
                "밥을/먹다 ovqatni yemoq\n"
                "ovqatni/yemoq 밥을/먹다"
            )
        
        # Saqlash
        data[t_k][s_k][q_k][korean_part] = uzbek_part
        save_data(data)
        
        bot.send_message(message.chat.id, f"✅ 1 ta so'z saqlandi")
    else:
        # Context yo'q - xabar berish
        current = get_location_text(uid)
        msg = f"{current}\n\n"
        
        if uid not in user_context or not user_context[uid].get("topic"):
            msg += "❌ Siz topik kiritmadingiz\n"
        if uid not in user_context or not user_context[uid].get("section"):
            msg += "❌ Siz savol turini kiritmadingiz\n"
        if uid not in user_context or not user_context[uid].get("question"):
            msg += "❌ Siz savol raqamini kiritmadingiz\n"
        
        bot.send_message(message.chat.id, msg)

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