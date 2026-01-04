import telebot
import json
import os
import re
import subprocess
import psutil
import threading
import time
from datetime import datetime

# --- KONFIGURATSIYA ---
TOKEN = "8046330769:AAF-JRhi1yug07Ng_UBSMA2wioKHybc5ub8"
DATA_FILE = "dictionary.json"

bot = telebot.TeleBot(TOKEN)
user_context = {}
ADMIN_ID = 8046330769 # O'z ID raqamingizni kiriting

# --- MA'LUMOTLAR BILAN ISHLASH ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_korean(text):
    return bool(re.search('[\uac00-\ud7af]', text))

def get_battery():
    try:
        out = subprocess.check_output(["termux-battery-status"], timeout=5).decode()
        return json.loads(out)
    except: return None

# --- TUGMALAR ---
def get_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("▶️ START")
    markup.row("📂 BO‘LIMLAR", "📤 EXPORT")
    return markup

def get_help_text():
    return (
        "📘 **DICTIONARYBOT — YO'RIQNOMA**\n\n"
        "1️⃣ **Bo'lim:** `>35` va `.1` (Topik va Savol)\n"
        "2️⃣ **Qo'shish:** `학교 maktab` (Ikki xil til)\n"
        "3️⃣ **Tahrir:** `사과.olma` yoki `olma.배` (Nuqta orqali)\n"
        "4️⃣ **Qidiruv:** `s.olma` \n"
        "📊 **Status:** /status buyrug'ini bosing."
    )

# --- HANDLERLAR TARTIBI MUHIM ---

@bot.message_handler(commands=['start'])
def welcome_cmd(message):
    bot.send_message(message.chat.id, get_help_text(), parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "▶️ START")
def welcome_btn(message):
    bot.send_message(message.chat.id, get_help_text(), parse_mode="Markdown", reply_markup=get_main_keyboard())

# BUYRUQLAR handle_all DAN TEPADA BO'LISHI KERAK
@bot.message_handler(commands=['status'])
def status_cmd(message):
    bat = get_battery()
    ram = psutil.virtual_memory()
    msg = "📊 **TIZIM HOLATI**\n\n"
    if bat:
        msg += (f"🔋 Batareya: {bat.get('percentage') or 0}%\n"
                f"🌡 Harorat: {bat.get('temperature') or 0}°C\n"
                f"⚡ Holat: {bat.get('status') or 'Noma`lum'}\n")
    else:
        msg += "🔋 Batareya: Termux API ma'lumoti yo'q\n"
    msg += f"🧠 RAM: {ram.percent}%"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📤 EXPORT")
def export_file(message):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="Zaxira nusxa")
    else: bot.send_message(message.chat.id, "Lug'at bo'sh.")

@bot.message_handler(func=lambda m: m.text == "📂 BO‘LIMLAR")
def show_sections(message):
    data = load_data()
    if not data: return bot.send_message(message.chat.id, "Lug'at bo'sh.")
    report = "📂 **Mavjud bo'limlar:**\n\n"
    for t, qs in data.items():
        report += f"📌 **{t}**\n"
        for q in qs.keys():
            t_nums = re.findall(r'\d+', t)
            q_nums = re.findall(r'\d+', q)
            if t_nums and q_nums:
                report += f"  ┕ 🔹 {q} (/view_{t_nums[0]}_{q_nums[0]})\n"
    bot.send_message(message.chat.id, report)

@bot.message_handler(func=lambda m: m.text.startswith("/view_"))
def view_words(message):
    data = load_data()
    try:
        p = message.text.split("_")
        t_key, q_key = f"{p[1]}-topik", f"{p[2]}-savol"
        words = data[t_key][q_key]
        res = f"📖 **{t_key}, {q_key}:**\n\n" + "\n".join([f"▫️ `{k}` — {v}" for k, v in words.items()])
        bot.send_message(message.chat.id, res, parse_mode="Markdown")
    except: bot.send_message(message.chat.id, "Xatolik: bo'lim topilmadi.")

@bot.message_handler(content_types=['text'])
def handle_all(message):
    text = message.text.strip()
    # AGAR MATN BUYRUQ BO'LSA (/) UNI QABUL QILMA
    if text.startswith("/"):
        return

    uid = message.from_user.id
    data = load_data()

    # Bo'limlarni tanlash logicasi (> va .)
    if text.startswith(">"):
        t_key = f"{text[1:].strip()}-topik"
        if t_key not in data: data[t_key] = {}
        user_context[uid] = {"topic": t_key, "question": None}
        save_data(data)
        bot.send_message(message.chat.id, f"✅ Tanlandi: {t_key}")
        return

    if text.startswith("."):
        if uid not in user_context or not user_context[uid].get("topic"):
            return bot.send_message(message.chat.id, "⚠️ Avval topikni tanlang (>35)")
        q_key = f"{text[1:].strip()}-savol"
        t_key = user_context[uid]["topic"]
        if q_key not in data[t_key]: data[t_key][q_key] = {}
        user_context[uid]["question"] = q_key
        save_data(data)
        bot.send_message(message.chat.id, f"✅ Tanlandi: {t_key} | {q_key}")
        return

    # Qidiruv s.
    if text.lower().startswith("s."):
        query = text[2:].strip().lower()
        res = "🔍 Natijalar:\n"; found = False
        for t, qs in data.items():
            for q, ws in qs.items():
                for kr, uz in ws.items():
                    if query in kr.lower() or query in uz.lower():
                        res += f"\n📍 {t}, {q}:\n{kr} - {uz}\n"; found = True
        bot.send_message(message.chat.id, res if found else "❌ Topilmadi.")
        return

    # Tahrirlash x.y (Ikki tomonlama)
    if "." in text and not text.startswith("."):
        old_w, new_w = [i.strip() for i in text.split(".", 1)]
        found = False
        for t in data:
            for q in data[t]:
                if old_w in data[t][q]:
                    data[t][q][old_w] = new_w; found = True
                else:
                    for kr, uz in list(data[t][q].items()):
                        if uz == old_w:
                            data[t][q].pop(kr); data[t][q][new_w] = uz; found = True
        if found:
            save_data(data); bot.send_message(message.chat.id, "✅ Tahrirlandi.")
        else: bot.send_message(message.chat.id, "❌ Topilmadi.")
        return

    # So'z qo'shish (Agar bo'lim tanlangan bo'lsa)
    if uid in user_context and user_context[uid].get("topic") and user_context[uid].get("question"):
        lines = text.split("\n")
        t_key, q_key = user_context[uid]["topic"], user_context[uid]["question"]
        added = 0
        for line in lines:
            parts = line.split()
            if len(parts) < 2: continue
            w1, w2 = parts[0], " ".join(parts[1:])
            if is_korean(w1) == is_korean(w2): continue
            kr, uz = (w1, w2) if is_korean(w1) else (w2, w1)
            data[t_key][q_key][kr] = uz; added += 1
        if added > 0:
            save_data(data); bot.send_message(message.chat.id, f"✅ {added} ta so'z saqlandi.")
    else:
        bot.send_message(message.chat.id, "⚠️ Avval bo'lim tanlang (>35 va .1)")

# --- MONITORING ---
def auto_status():
    while True:
        try:
            bat = get_battery()
            ram = psutil.virtual_memory()
            if bat and ADMIN_ID:
                if bat.get('percentage', 100) <= 10:
                    bot.send_message(ADMIN_ID, "🔴 Batareya 10% qoldi!")
            if ram.percent >= 90 and ADMIN_ID:
                bot.send_message(ADMIN_ID, f"🧠 RAM to'ldi: {ram.percent}%")
        except: pass
        time.sleep(300)

threading.Thread(target=auto_status, daemon=True).start()

# --- RUN INFO ---
if __name__ == "__main__":
    try:
        me = bot.get_me()
        print("\n" + "="*40)
        print(f"BOT ISHGA TUSHDI: @{me.username}")
        print(f"ID: {me.id}")
        print(f"SANA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"STATUS: ONLINE")
        print("="*40 + "\n")
        bot.infinity_polling()
    except Exception as e: print(f"Xato: {e}")