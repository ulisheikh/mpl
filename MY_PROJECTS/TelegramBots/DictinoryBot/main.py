import telebot
import json
import os
import re
import subprocess
import psutil
import threading
import time
from datetime import datetime
import sys
import subprocess

# --- CONFIGURATION ---
TOKEN = "8046756811:AAEsMXNBMkIMkqM3XtVyQ3OzOd4itRfn03M"
DATA_FILE = "dictionary.json"
START_TIME = datetime.now()

bot = telebot.TeleBot(TOKEN)
user_context = {}
ADMIN_ID = 8046330769 
REPO_DIR = os.path.dirname(os.path.abspath(__file__))



# --- DATA MANAGEMENT ---
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
            
            # Agar o'zgarish bo'lsa, saqlash
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
    return bool(re.search('[\uac00-\ud7af]', text))

def get_uptime():
    delta = datetime.now() - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def get_battery():
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
# --- KEYBOARDS ---
def get_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Har bir tugma alohida qatorda chiqishi uchun row() dan foydalanamiz
    markup.row("▶️ START")
    markup.row("📂 BO'LIMLAR")
    markup.row("📥 DOWNLOAD DICTIONARY")
    markup.row("🔄 UPDATE")  # 4-tugma sifatida qo'shildi
    return markup

def get_help_text():
    return (
        "📚 LUG'AT BOT\n"
        "━━━━━━━━━━━━\n\n"

        "1️⃣ TOPIK TANLASH\n"
        "   >35 yoki >36 yoki >37\n"
        "   >35.  (tezkor kirish)\n\n"

        "2️⃣ SAVOL TURI TANLASH\n"
        "   ?reading\n"
        "   ?writing\n"
        "   ?listening\n\n"

        "3️⃣ SAVOL RAQAMI\n"
        "   1. yoki 2. yoki 3. ... 30.\n\n"  # .1 dan 1. ga o'zgartirildi

        "4️⃣ HOZIRGI JOYINGIZ\n"
        "   %l   — joylashuvni ko‘rish\n\n"

        "5️⃣ SO‘Z QO‘SHISH\n"
        "   학교 maktab   (ikki til)\n\n"

        "6️⃣ SO‘ZNI O‘ZGARTIRISH\n"
        "   eski.yangi\n\n"

        "7️⃣ SO‘ZNI O‘CHIRISH\n"
        "   rm.so‘z\n\n"

        "8️⃣ TOPIKNI O‘CHIRISH\n"
        "   rm.35   (butun topik)\n\n"

        "9️⃣ SO‘Z QIDIRISH\n"
        "   s.so‘z\n\n"

        "🔟 TIZIM HOLATI\n"
        "   /status\n\n"
        
        "GIT PULL QILISH\n"
        "   /update  yoki  🔄 UPDATE tugmasi\n\n"
        
        "💡 >  ?  .  belgilar orqali\n"
        "   yangi topik / savol turi /\n"
        "   savol yaratish mumkin"
    )

# --- UPDATE TUGMASI HANDLERI ---
# Bu qismni handlerlar (content_types=['text']) bo'limiga qo'shishni unutmang:
@bot.message_handler(func=lambda m: m.text == "🔄 UPDATE")
def update_button_handler(message):
    update_bot(message)

# --- HANDLERS ---
@bot.message_handler(commands=['update'])
def update_bot(message):
    bot.send_message(message.chat.id, "🔄 Kod yangilanmoqda...")

    try:
        result = subprocess.check_output(
            ["git", "pull"],
            cwd=REPO_DIR,
            stderr=subprocess.STDOUT
        ).decode()

        bot.send_message(
            message.chat.id,
            f"✅ Git pull bajarildi:\n\n{result}\n\n♻️ Bot qayta ishga tushyapti..."
        )

        # BOTNI TO‘LIQ RESTART
        python = sys.executable
        os.execv(python, [python] + sys.argv)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Update xato:\n{e}")



@bot.message_handler(commands=['start'])
def welcome_cmd(message):
    bot.send_message(message.chat.id, get_help_text(), reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "▶️ START")
def welcome_btn(message):
    bot.send_message(message.chat.id, get_help_text(), reply_markup=get_main_keyboard())

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bat = get_battery()
    ram = psutil.virtual_memory()
    
    msg = "╔═════════╗\n"
    msg += "║ 📊 TIZIM HOLATI  ║\n"
    msg += "╚═════════╝\n\n"
    msg += f"⏱ Ishlash vaqti: {get_uptime()}\n\n"
    
    if bat:
        msg += f"🔋 Batareya: {bat.get('percentage', 0)}%\n"
        msg += f"🌡 Harorat: {bat.get('temperature', 0)}°C\n"
        msg += f"⚡ Holat: {bat.get('status', 'Unknown')}\n\n"
    else:
        msg += "🔋 Batareya: Termux API yo'q\n\n"
    
    msg += f"🧠 RAM: {ram.percent}%\n"
    msg += f"💾 RAM hajmi: {ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB\n\n"
    
    # Bot fayl hajmi
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

@bot.message_handler(func=lambda m: m.text == "📥 DOWNLOAD DICTIONARY")
def export_file(message):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="📥 Lug'at fayli")
    else: 
        bot.send_message(message.chat.id, "❌ Lug'at bo'sh")

@bot.message_handler(func=lambda m: m.text == "📂 BO'LIMLAR")
def show_sections(message):
    data = load_data()
    if not data: 
        return bot.send_message(message.chat.id, "❌ Lug'at bo'sh")
    
    msg = "📂 MAVJUD TOPIKLAR:\n\n"
    
    # Faqat to'g'ri formatdagi topiklar
    topics = []
    for topic_key in data.keys():
        if topic_key.startswith("Topik-"):
            topic_num = topic_key.replace("Topik-", "")
            # Faqat raqamli topiklar (noto'g'ri formatlarni o'tkazib yuborish)
            if topic_num.isdigit():
                topics.append(int(topic_num))
    
    # Raqam bo'yicha saralash
    topics_sorted = sorted(topics)
    
    if not topics_sorted:
        return bot.send_message(message.chat.id, "❌ To'g'ri topiklar yo'q")
    
    for topic_num in topics_sorted:
        msg += f"/Topik{topic_num}\n"
    
    msg += "\n💡 Topikni tanlash uchun bosing"
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(regexp=r'^/Topik\d+$')
def show_topic_sections(message):
    """Topik ichidagi savol turlarini ko'rsatish"""
    # /Topik35 dan 35 ni olish
    topic_num = message.text.replace("/Topik", "")
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
    
    # Context saqlash
    uid = message.from_user.id
    if uid not in user_context:
        user_context[uid] = {}
    user_context[uid]["viewing_topic"] = topic_key
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['reading', 'writing', 'listening'])
def show_section_words(message):
    """Savol turi ichidagi so'zlarni ko'rsatish"""
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
    
    msg = f"📌 {topic_num}-topik > {section_name.upper()}\n\n"
    
    questions = data[topic_key][section_name]
    if not questions:
        return bot.send_message(message.chat.id, f"❌ {section_name} bo'sh")
    
    for q_key in sorted(questions.keys(), key=lambda x: int(x.replace("-savol so'zlari", "")) if x.replace("-savol so'zlari", "").isdigit() else 0):
        words = questions[q_key]
        if words:
            q_num = q_key.replace("-savol so'zlari", "")
            msg += f"{q_num}-savol so'zlari\n"
            
            for kr, uz in words.items():
                msg += f"   • {kr} → {uz}\n"
            msg += "\n"
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(content_types=['text'])
def handle_all(message):
    text = message.text.strip()
    if text.startswith("/"): return
    
    uid = message.from_user.id
    data = load_data()

    # HOZIRGI JOYING (%l)
    if text == "%l":
        bot.send_message(message.chat.id, get_location_text(uid))
        return

    # 1. TOPIK TANLASH/YARATISH (>35 yoki >35. tezkor kirish)
    if text.startswith(">"):
        # >35. tezkor kirish formatini tekshirish
        is_quick_access = text.endswith(".")
        topic_num = text[1:].strip().rstrip(".")
        topic_name = f"Topik-{topic_num}"
        
        # Tezkor kirish - topikni ko'rsatish
        if is_quick_access:
            if topic_name not in data:
                return bot.send_message(
                    message.chat.id,
                    f"❌ {topic_num}-topik topilmadi\n\n"
                    f"Yaratish uchun: >{topic_num}"
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
            
            # Context saqlash
            if uid not in user_context:
                user_context[uid] = {}
            user_context[uid]["viewing_topic"] = topic_name
            
            bot.send_message(message.chat.id, msg)
            return
        
        # Oddiy topik tanlash/yaratish
        is_new = topic_name not in data
        
        if is_new:
            data[topic_name] = {}
            save_data(data)
        
        # Context yangilash
        if uid not in user_context:
            user_context[uid] = {}
        user_context[uid]["topic"] = topic_name
        user_context[uid]["section"] = None
        user_context[uid]["question"] = None
        
        if is_new:
            bot.send_message(
                message.chat.id,
                f"✅ {topic_num}-topik bo'limi yaratildi\n\n"
                f"Endi savol turini kiriting:\n"
                f"?reading yoki ?writing yoki ?listening"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"✅ {topic_num}-topik tanlandi\n\n"
                f"Endi savol turini kiriting:\n"
                f"?reading yoki ?writing yoki ?listening"
            )
        return

    # 2. SAVOL TURI TANLASH/YARATISH (?reading)
    if text.startswith("?"):
        if uid not in user_context or not user_context[uid].get("topic"):
            return bot.send_message(
                message.chat.id,
                "⚠️ Avval topik tanlang\n\nMisol: >35"
            )
        
        section_name = text[1:].strip().lower()
        topic_key = user_context[uid]["topic"]
        topic_num = topic_key.replace("Topik-", "")
        
        # Mavjudligini tekshirish
        is_new = section_name not in data[topic_key]
        
        if is_new:
            data[topic_key][section_name] = {}
            save_data(data)
        
        # Context yangilash
        user_context[uid]["section"] = section_name
        user_context[uid]["question"] = None
        
        bot.send_message(
            message.chat.id,
            f"✅ {topic_num}-topik bo'limiga {section_name} savol turi belgilandi\n\n"
            f"Endi savol tartib raqamini kiriting:\n"
            f".1 yoki .2 yoki .3 ..."
        )
# 3. SAVOL RAQAMI TANLASH/YARATISH (1.)
    # text.endswith(".") - oxiri nuqta bilan tugashini tekshiradi
    # text[:-1].isdigit() - nuqtadan oldingi hamma narsa raqam ekanini tekshiradi
    if text.endswith(".") and text[:-1].strip().isdigit():
        if uid not in user_context or not user_context[uid].get("section"):
            return bot.send_message(
                message.chat.id,
                "⚠️ Avval savol turini tanlang\n\nMisol: ?reading"
            )
        
        # text[:-1] - oxiridagi nuqtani tashlab yuborib, faqat raqamni oladi
        q_num = text[:-1].strip()
        q_name = f"{q_num}-savol so'zlari"
        
        topic_key = user_context[uid]["topic"]
        section_key = user_context[uid]["section"]
        topic_num = topic_key.replace("Topik-", "")
        
        # Mavjudligini tekshirish
        is_new = q_name not in data[topic_key][section_key]
        
        if is_new:
            data[topic_key][section_key][q_name] = {}
            save_data(data)
        
        # Context yangilash
        user_context[uid]["question"] = q_name
        
        bot.send_message(
            message.chat.id,
            f"✅ {topic_num}-topik > {section_key} > {q_num}-savol so'zlarini kiriting"
        )
        return
    # 4. O'CHIRISH (rm.apple yoki rm.35)
    if text.lower().startswith("rm."):
        target = text[3:].strip()
        
        # Agar raqam bo'lsa - topikni o'chirish
        if target.isdigit():
            topic_key = f"Topik-{target}"
            if topic_key in data:
                del data[topic_key]
                save_data(data)
                bot.send_message(message.chat.id, f"🗑 {target}-topik o'chirildi")
            else:
                bot.send_message(message.chat.id, f"❌ {target}-topik topilmadi")
            return
        
        # Aks holda - so'zni o'chirish
        word_to_rm = target.lower()
        found = False
        
        for t in data:
            for s in data[t]:
                for q in data[t][s]:
                    to_del = [k for k in data[t][s][q] if k.lower() == word_to_rm]
                    for k in to_del: 
                        del data[t][s][q][k]
                        found = True
                    
                    to_del_v = [k for k, v in data[t][s][q].items() if v.lower() == word_to_rm]
                    for k in to_del_v: 
                        del data[t][s][q][k]
                        found = True
        
        if found:
            save_data(data)
            bot.send_message(message.chat.id, f"🗑 O'chirildi: {word_to_rm}")
        else: 
            bot.send_message(message.chat.id, "❌ Topilmadi")
        return

    # 5. QIDIRISH (s.apple)
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
                            results.append(f"📍 {topic_num}-topik > {s.upper()} > {q_num}-savol: {kr} → {uz}")
        
        if results:
            msg = "🔍 TOPILDI:\n\n" + "\n\n".join(results)
        else:
            msg = "❌ Topilmadi"
        
        bot.send_message(message.chat.id, msg)
        return

    # 6. O'ZGARTIRISH (word.new_word)
    if "." in text and not text.startswith("."):
        old_w, new_w = [i.strip() for i in text.split(".", 1)]
        found = False
        
        for t in data:
            for s in data[t]:
                for q in data[t][s]:
                    if old_w in data[t][s][q]:
                        data[t][s][q][old_w] = new_w
                        found = True
                    else:
                        for kr, uz in list(data[t][s][q].items()):
                            if uz == old_w:
                                data[t][s][q].pop(kr)
                                data[t][s][q][new_w] = uz
                                found = True
        
        if found:
            save_data(data)
            bot.send_message(message.chat.id, "✅ Yangilandi")
        else: 
            bot.send_message(message.chat.id, "❌ Topilmadi")
        return

    # 7. SO'Z QO'SHISH
    # Faqat 3tasi ham tayinlangan bo'lsa so'z qabul qilish
    if uid in user_context and user_context[uid].get("topic") and user_context[uid].get("section") and user_context[uid].get("question"):
        lines = text.split("\n")
        t_k = user_context[uid]["topic"]
        s_k = user_context[uid]["section"]
        q_k = user_context[uid]["question"]
        
        topic_num = t_k.replace("Topik-", "")
        q_num = q_k.replace("-savol so'zlari", "")
        
        added = 0
        for line in lines:
            parts = line.split()
            if len(parts) < 2: continue
            
            w1, w2 = parts[0], " ".join(parts[1:])
            if is_korean(w1) == is_korean(w2): continue
            
            kr, uz = (w1, w2) if is_korean(w1) else (w2, w1)
            data[t_k][s_k][q_k][kr] = uz
            added += 1
        
        if added > 0:
            save_data(data)
            bot.send_message(
                message.chat.id,
                f"✅ {added} ta so'z saqlandi"
            )
        # Agar hech narsa qo'shilmasa (format xato), indamay o'tib ketish
    else:
        # Hozirgi holatni ko'rsatish
        current = get_location_text(uid)
        missing = []
        
        if uid not in user_context or not user_context[uid].get("topic"):
            missing.append(">35 (topik)")
        if uid not in user_context or not user_context[uid].get("section"):
            missing.append("?reading (savol turi)")
        if uid not in user_context or not user_context[uid].get("question"):
            missing.append(".1 (savol raqami)")
        
        msg = f"{current}\n\n⚠️ Yetishmayapti:\n"
        for m in missing:
            msg += f"  • {m}\n"
        
        bot.send_message(message.chat.id, msg)

# --- MONITORING ---
def auto_monitor():
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

# --- RUN ---
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