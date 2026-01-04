import telebot
import json
import os
import re
from datetime import datetime

# --- KONFIGURATSIYA ---
TOKEN = "8046330769:AAF-JRhi1yug07Ng_UBSMA2wioKHybc5ub8"
DATA_FILE = "dictionary.json"

bot = telebot.TeleBot(TOKEN)
user_context = {}

# --- MA'LUMOTLAR BILAN ISHLASH ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_korean(text):
    # Koreys alifbosini tekshirish
    return bool(re.search('[\uac00-\ud7af]', text))

# --- TUGMALAR ---
def get_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("▶️ START")
    markup.row("📂 BO‘LIMLAR", "📤 EXPORT")
    return markup

# --- INFO MATNI ---
def get_help_text():
    return (
        "📘 **DICTIONARYBOT — TO‘LIQ TAVSIF**\n\n"
        "1️⃣ **Bo'lim tanlash:**\n"
        "   `>35` — 35-topikni tanlash/yaratish\n"
        "   `.1` — Tanlangan topikda 1-savolni ochish\n\n"
        "2️⃣ **So'z qo'shish:**\n"
        "   `학교 maktab` yoki `maktab 학교` deb yozing.\n"
        "   *Faqat bitta tildagi so'zlar bo'lsa xatolik beradi.*\n\n"
        "3️⃣ **Tahrirlash (Ikki tomonlama):**\n"
        "   🔹 `사과.olma` -> Tarjimani tahrirlash\n"
        "   🔹 `olma.배` -> Koreyscha so'zni tahrirlash\n\n"
        "4️⃣ **Qidiruv:** `s.olma` yoki `s.사과`"
    )

# --- HANDLERLAR ---
@bot.message_handler(commands=['start'])
def welcome_cmd(message):
    bot.send_message(message.chat.id, get_help_text(), parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "▶️ START")
def welcome_btn(message):
    bot.send_message(message.chat.id, get_help_text(), parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📤 EXPORT")
def export_file(message):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"Lug'at fayli\nSana: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        bot.send_message(message.chat.id, "Lug'at hali bo'sh.")

@bot.message_handler(func=lambda m: m.text == "📂 BO‘LIMLAR")
def show_sections(message):
    data = load_data()
    if not data:
        return bot.send_message(message.chat.id, "Lug'at bo'sh.")

    report = "📂 **Mavjud bo'limlar:**\n\n"
    for topic, questions in data.items():
        report += f"📌 **{topic}**\n"
        for q in questions.keys():
            t_nums = re.findall(r'\d+', topic)
            q_nums = re.findall(r'\d+', q)
            if t_nums and q_nums:
                report += f"  ┕ 🔹 {q} (/view_{t_nums[0]}_{q_nums[0]})\n"

    report += "\n👆 So'zlarni ko'rish uchun ko'k buyruqni bosing."
    bot.send_message(message.chat.id, report)

@bot.message_handler(func=lambda m: m.text.startswith("/view_"))
def view_words(message):
    data = load_data()
    try:
        parts = message.text.split("_")
        t_key, q_key = f"{parts[1]}-topik", f"{parts[2]}-savol"
        if t_key in data and q_key in data[t_key]:
            words = data[t_key][q_key]
            res = f"📖 **{t_key}, {q_key} so'zlari:**\n\n" + "\n".join([f"▫️ `{k}` — {v}" for k, v in words.items()])
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "Bo'lim topilmadi.")
    except:
        bot.send_message(message.chat.id, "Xato yuz berdi.")

@bot.message_handler(content_types=['text'])
def handle_all(message):
    text = message.text.strip()
    uid = message.from_user.id
    data = load_data()

    if text.lower() in ["start", "/start", "▶️ start"]: return

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

    if text.lower().startswith("s."):
        query = text[2:].strip().lower()
        res = "🔍 Natijalar:\n"
        found = False
        for t, qs in data.items():
            for q, ws in qs.items():
                for kr, uz in ws.items():
                    if query in kr.lower() or query in uz.lower():
                        res += f"\n📍 {t}, {q}:\n{kr} - {uz}\n"
                        found = True
        bot.send_message(message.chat.id, res if found else "❌ Topilmadi.")
        return

    # --- TAHRIRLASH (Ikki tomonlama) ---
    if "." in text and not text.startswith("."):
        old_word, new_word = [i.strip() for i in text.split(".", 1)]
        found = False
        for t in data:
            for q in data[t]:
                if old_word in data[t][q]: # Kalit bo'lsa qiymatni o'zgartirish
                    data[t][q][old_word] = new_word
                    found = True
                else: # Qiymat bo'lsa kalitni o'zgartirish
                    for kr, uz in list(data[t][q].items()):
                        if uz == old_word:
                            data[t][q].pop(kr)
                            data[t][q][new_word] = uz
                            found = True
        if found:
            save_data(data)
            bot.send_message(message.chat.id, "✅ Tahrirlandi.")
        else:
            bot.send_message(message.chat.id, "❌ Topilmadi.")
        return

    # --- SO'Z QO'SHISH (Filtr bilan) ---
    if uid in user_context and user_context[uid].get("topic") and user_context[uid].get("question"):
        lines = text.split("\n")
        t_key, q_key = user_context[uid]["topic"], user_context[uid]["question"]
        added = 0
        for line in lines:
            parts = line.split()
            if len(parts) < 2: continue
            w1, w2 = parts[0], " ".join(parts[1:])
            
            # Til filtri
            if is_korean(w1) == is_korean(w2):
                bot.send_message(message.chat.id, f"❌ Xato: Siz faqat bir tildagi so'zlarni kiritdingiz! (`{line}`)")
                continue
                
            kr, uz = (w1, w2) if is_korean(w1) else (w2, w1)
            data[t_key][q_key][kr] = uz
            added += 1

        if added > 0:
            save_data(data)
            bot.send_message(message.chat.id, f"✅ {added} ta so'z saqlandi.")
    else:
        bot.send_message(message.chat.id, "⚠️ Avval bo'lim tanlang (>35 va .1)")

# --- RUN INFO ---
if __name__ == "__main__":
    try:
        me = bot.get_me()
        print("\n" + "="*50)
        print(f"BOT ISHGA TUSHDI: @{me.username}")
        print(f"ID: {me.id}")
        print(f"VAQT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"STATUS: Online va lug'at tayyor.")
        print("="*50 + "\n")
        bot.infinity_polling()
    except Exception as e:
        print(f"Xatolik: {e}")