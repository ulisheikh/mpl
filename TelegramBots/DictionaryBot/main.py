# -*- coding: utf-8 -*-
"""
KOREAN-O'ZBEK LUG'AT BOT
Yangilangan versiya - 2.0
User-based tizim
"""

import telebot
import os
import re
import threading
import time
from datetime import datetime

# IMPORT CONFIG
from config import *

# IMPORT UTILS
from utils.auth import *
from utils.data_handler import *
from utils.language import *
from utils.inline_keyboards import *

# IMPORT ADMIN
from admin.monitoring import *
from admin.user_manager import *

# BOT YARATISH
bot = telebot.TeleBot(TOKEN)

# USER CONTEXT
user_context = {}

# ============================================
# YORDAMCHI FUNKSIYALAR
# ============================================

def get_help_text(user_id):
    """Yordam matni"""
    lang = get_user_language(user_id)
    
    header = f"<b>{get_text(user_id, 'help_title')}</b>\n"
    header += "<b>─────────────────────</b>\n\n"
    
    body = f"<b>{get_text(user_id, 'help_create')}</b>\n\n"
    body += f"<b>{get_text(user_id, 'help_add_word')}</b>\n\n"
    body += f"<b>{get_text(user_id, 'help_delete')}</b>\n\n"
    body += f"<b>{get_text(user_id, 'help_restore')}</b>\n\n"
    body += f"<b>{get_text(user_id, 'help_search')}</b>\n\n"
    body += f"<b>{get_text(user_id, 'help_system')}</b>\n"
    body += "<b>━━━━━━━━━━━━━━━━━</b>\n"
    body += f"<i>{get_text(user_id, 'help_tip')}</i>"
    
    return header + body

def get_location_text(user_id):
    """Hozirgi joying"""
    if user_id not in user_context:
        return "❌ Hozir hech qayerda emasmiz"
    
    ctx = user_context[user_id]
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
# START VA AUTENTIFIKATSIYA
# ============================================
"""
DictionaryBot main.py - START HANDLER qismi
"""

from admin.user_manager import save_user_info

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    
    # 1. User ma'lumotlarini saqlash
    save_user_info(
        uid, 
        message.from_user.first_name, 
        message.from_user.last_name, 
        message.from_user.username
    )
    
    # 2. Bloklanganlikni tekshirish
    if is_user_blocked(uid):
        bot.send_message(uid, get_text(uid, 'password_blocked'))
        return

    # 3. Login tekshirish
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'), parse_mode="HTML")
        bot.register_next_step_handler(message, password_handler)
        return
    
    # 4. Welcome xabari (Hamma uchun bir xil)
    bot.send_message(
        uid, 
        get_text(uid, 'welcome'), 
        parse_mode="HTML", 
        reply_markup=get_main_keyboard(uid)
    )
    
    # 5. Help text yuborish (Hamma uchun)
    bot.send_message(uid, get_help_text(uid), parse_mode="HTML")

def password_handler(message):
    """Parol tekshirish"""
    uid = message.from_user.id
    password = message.text.strip()
    
    # Bloklangan userlarni tekshirish
    if is_user_blocked(uid):
        bot.send_message(uid, get_text(uid, 'password_blocked'))
        return
    
    # Parolni tekshirish
    role = verify_password(uid, password)
    
    if role:
        # Login qilish
        login_user(uid, role)
        
        bot.send_message(
            uid,
            get_text(uid, 'password_correct'),
            reply_markup=get_main_keyboard(uid)
        )
        
        bot.send_message(
            uid,
            get_help_text(uid),
            parse_mode="HTML"
        )
    else:
        # Noto'g'ri parol
        blocked = add_login_attempt(uid)
        
        if blocked:
            bot.send_message(uid, get_text(uid, 'password_blocked'))
        else:
            bot.send_message(uid, get_text(uid, 'password_wrong'))
            bot.register_next_step_handler(message, password_handler)

# ============================================
# SOZLAMALAR
# ============================================

@bot.message_handler(func=lambda m: m.text in ['📂 BO\'LIMLAR', '📂 섹션'])
def sections_handler(message):
    """Bo'limlar menyusi"""
    uid = message.from_user.id
    
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'))
        return
    
    data = load_user_data(uid)
    
    if not data:
        bot.send_message(uid, get_text(uid, 'no_topics'))
        return
    
    # Topiklar ro'yxati
    topics = []
    for topic_key in data.keys():
        if topic_key.startswith("Topik-"):
            topic_num = topic_key.replace("Topik-", "")
            if topic_num.isdigit():
                topics.append(int(topic_num))
    
    topics_sorted = sorted(topics)
    
    if not topics_sorted:
        bot.send_message(uid, get_text(uid, 'no_topics'))
        return
    
    # Inline klaviatura
    markup = get_topics_keyboard(uid, topics_sorted)
    
    bot.send_message(
        uid,
        get_text(uid, 'topics_list'),
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text in ['⚙️ SOZLAMALAR', '⚙️ 설정'])
def settings_handler(message):
    """Sozlamalar menyusi"""
    uid = message.from_user.id
    
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'))
        return
    
    is_admin_user = is_admin(uid)
    markup = get_settings_keyboard(uid, is_admin_user)
    
    bot.send_message(
        uid,
        get_text(uid, 'settings_menu'),
        reply_markup=markup
    )

# ============================================
# BO'LIMLAR
# ============================================


# ============================================
# EXPORT (JSON VA PYTHON)
# ============================================

@bot.message_handler(func=lambda m: m.text in ['📥 JSON', '📥 JSON'])
def export_json_handler(message):
    """JSON export"""
    uid = message.from_user.id
    
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'))
        return
    
    user_file = get_user_file(uid)
    
    if os.path.exists(user_file):
        with open(user_file, 'rb') as f:
            bot.send_document(
                uid,
                f,
                caption=get_text(uid, 'export_json_caption')
            )
    else:
        bot.send_message(uid, get_text(uid, 'export_empty'))

@bot.message_handler(func=lambda m: m.text in ['🐍 PYTHON', '🐍 PYTHON'])
def export_python_handler(message):
    """Python export"""
    uid = message.from_user.id
    
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'))
        return
        
    data = load_user_data(uid)
    if not data:
        bot.send_message(uid, get_text(uid, 'export_empty'))
        return
        
    py_code = json_to_python(uid)
    py_file = f"dictionary_{uid}.py"
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(py_code)
    
    # Mana shu joyda kod ulandi
    with open(py_file, 'rb') as f:
        bot.send_document(
            uid,
            f,
            caption=get_text(uid, 'export_python_caption')
        )

    try:
        os.remove(py_file)
    except:
        pass

# ============================================
# CALLBACK HANDLER
# ============================================

from admin.user_manager import (
    get_all_users, 
    format_users_list, 
    get_user_details,
    format_user_details
)

"""
DictionaryBot main.py - TO'LIQ CALLBACK HANDLER
"""
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Barcha callback querylar"""
    uid = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    try:
        # 1. SOZLAMALAR - TIZIM HOLATI
        if data == 'settings_status':
            stats = get_system_stats()
            msg = format_system_status(uid, stats)
            bot.edit_message_text(msg, chat_id, message_id, parse_mode="HTML", reply_markup=get_back_keyboard(uid, 'back_settings'))
            bot.answer_callback_query(call.id)
        
        # 2. FOYDALANUVCHILAR RO'YXATI
        elif data == 'settings_users':
            users = get_all_users()
            if not users:
                bot.answer_callback_query(call.id, get_text(uid, 'no_users'), show_alert=True)
                return
            
            msg = f"👥 <b>Foydalanuvchilar boshqaruvi</b>\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"📊 Jami foydalanuvchilar: <b>{len(users)}</b> ta\n\n"
            msg += f"<i>Boshqarish uchun foydalanuvchini tanlang:</i>"
            
            markup = get_users_keyboard(uid, users)
            bot.edit_message_text(msg, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
            bot.answer_callback_query(call.id)
        
        # 3. USER TAFSILOTLARI (FAQAT BU BITTA BO'LISHI KERAK!)
        elif data.startswith('user_detail_'):
            target_uid = data.split('_')[2]
            details = get_user_details(target_uid)
            
            # Blok holati
            is_blocked = is_user_blocked(int(target_uid))
            status_text = "🚫 Bloklangan" if is_blocked else "✅ Faol"
            
            msg = format_user_details(uid, details)
            msg += f"\n<b>Holati:</b> {status_text}"
            
            # Tugmalar
            from telebot import types
            markup = types.InlineKeyboardMarkup()
            
            b_text = "🔓 Blokdan chiqarish" if is_blocked else "🚫 Bloklash"
            b_call = f"user_unblock_{target_uid}" if is_blocked else f"user_block_{target_uid}"
            
            markup.row(types.InlineKeyboardButton(b_text, callback_data=b_call))
            markup.row(types.InlineKeyboardButton("📥 Lug'atni yuklash (JSON)", callback_data=f"user_export_{target_uid}"))
            markup.row(types.InlineKeyboardButton("⬅️ Orqaga", callback_data="settings_users"))
            
            bot.edit_message_text(msg, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
            bot.answer_callback_query(call.id)

        # 4. BLOKLASH/OCHISH
        elif data.startswith(('user_block_', 'user_unblock_')):
            target_uid = data.split('_')[2]
            
            # O'zini bloklashni oldini olish
            if "user_block_" in data and str(target_uid) == str(uid):
                bot.answer_callback_query(call.id, "O'zingizni bloklay olmaysiz! ❌", show_alert=True)
                return
            
            if "user_block_" in data:
                block_user(int(target_uid))
                bot.answer_callback_query(call.id, "✅ Foydalanuvchi bloklandi")
            else:
                unblock_user(int(target_uid))
                bot.answer_callback_query(call.id, "✅ Blokdan chiqarildi")
            
            # Ma'lumotni yangilash
            new_call = call
            new_call.data = f"user_detail_{target_uid}"
            callback_handler(new_call)
        
        # 5. SOZLAMALAR - TIL
        elif data == 'settings_language':
            bot.edit_message_text(
                get_text(uid, 'select_language'),
                chat_id,
                message_id,
                reply_markup=get_language_keyboard()
            )
            bot.answer_callback_query(call.id)
        
        # 6. SOZLAMALAR - BOT HAQIDA
        elif data == 'settings_about':
            bot.edit_message_text(
                get_text(uid, 'about_bot'),
                chat_id,
                message_id,
                parse_mode="HTML",
                reply_markup=get_back_keyboard(uid, 'back_settings')
            )
            bot.answer_callback_query(call.id)
        
        # 7. SOZLAMALAR - PAROL
        elif data == 'settings_password':
            bot.edit_message_text(
                "🔐 Parolni o'zgartirish:\n\n"
                "1. User parolni o'zgartirish: /newpass_user yangi_parol\n"
                "2. Admin parolni o'zgartirish: /newpass_admin yangi_parol",
                chat_id,
                message_id,
                reply_markup=get_back_keyboard(uid, 'back_settings')
            )
            bot.answer_callback_query(call.id)
        
        # 8. TIL O'ZGARTIRISH
        elif data.startswith('lang_'):
            lang = data.split('_')[1]
            set_user_language(uid, lang)
            
            bot.answer_callback_query(
                call.id, 
                get_text(uid, 'language_changed'),
                show_alert=True
            )
            
            bot.edit_message_text(
                get_text(uid, 'settings_menu'),
                chat_id,
                message_id,
                reply_markup=get_settings_keyboard(uid, is_admin(uid))
            )
            
            # Reply tugmalarni yangilash
            bot.send_message(
                uid,
                get_text(uid, 'language_changed'),
                reply_markup=get_main_keyboard(uid)
            )
        
        # 9. TOPIKLAR
        elif data.startswith('topic_'):
            topic_num = data.split('_')[1]
            topic_key = f"Topik-{topic_num}"
            
            user_data = load_user_data(uid)
            
            if topic_key not in user_data:
                bot.answer_callback_query(
                    call.id, 
                    get_text(uid, 'error_not_found'), 
                    show_alert=True
                )
                return
            
            sections = list(user_data[topic_key].keys())
            markup = get_sections_keyboard(uid, topic_num, sections)
            
            bot.edit_message_text(
                get_text(uid, 'topic_selected', topic_num=topic_num),
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        
        # 10. BO'LIMLAR
        elif data.startswith('section_'):
            parts = data.split('_')
            topic_num = parts[1]
            section = parts[2]
            
            topic_key = f"Topik-{topic_num}"
            user_data = load_user_data(uid)
            
            if topic_key not in user_data or section not in user_data[topic_key]:
                bot.answer_callback_query(
                    call.id, 
                    get_text(uid, 'error_not_found'), 
                    show_alert=True
                )
                return
            
            msg = f"📌 <b>{topic_num}-Topik > {section.upper()}</b>\n\n"
            
            questions = user_data[topic_key][section]
            if not questions:
                msg += "❌ Bo'sh"
            else:
                for q_key in sorted(questions.keys(), key=lambda x: int(x.replace("-savol so'zlari", "")) if x.replace("-savol so'zlari", "").isdigit() else 0):
                    words = questions[q_key]
                    if words:
                        q_num = q_key.replace("-savol so'zlari", "")
                        msg += f"<code>{q_num}-savol so'zlari</code>\n"
                        
                        for ko, uz in words.items():
                            msg += f"   <b>• {ko}</b> - <i>{uz}</i>\n"
                        msg += "\n"
            
            bot.edit_message_text(
                msg,
                chat_id,
                message_id,
                parse_mode="HTML",
                reply_markup=get_back_keyboard(uid, f'topic_{topic_num}')
            )
            bot.answer_callback_query(call.id)
        
        # 11. USER EXPORT
        elif data.startswith('user_export_'):
            target_uid = data.split('_')[2]
            user_file = get_user_file(target_uid)
            
            if os.path.exists(user_file):
                from admin.user_manager import get_user_info
                
                user_info = get_user_info(target_uid)
                full_name = f"{user_info['first_name']} {user_info['last_name']}".strip()
                
                if not full_name:
                    full_name = f"User {target_uid}"
                
                with open(user_file, 'rb') as f:
                    bot.send_document(
                        chat_id, 
                        f, 
                        caption=f"📥 <b>{full_name}</b> lug'ati\n🆔 ID: <code>{target_uid}</code>",
                        parse_mode="HTML"
                    )
        
                bot.answer_callback_query(call.id, "✅ Fayl yuborildi")
        
        # 12. ORQAGA QAYTISH
        elif data == 'back_main':
            bot.delete_message(chat_id, message_id)
            bot.answer_callback_query(call.id)
        
        elif data == 'back_settings':
            bot.edit_message_text(
                get_text(uid, 'settings_menu'),
                chat_id,
                message_id,
                reply_markup=get_settings_keyboard(uid, is_admin(uid))
            )
            bot.answer_callback_query(call.id)
        
        elif data == 'back_topics':
            user_data = load_user_data(uid)
            topics = []
            for topic_key in user_data.keys():
                if topic_key.startswith("Topik-"):
                    topic_num = topic_key.replace("Topik-", "")
                    if topic_num.isdigit():
                        topics.append(int(topic_num))
            
            topics_sorted = sorted(topics)
            markup = get_topics_keyboard(uid, topics_sorted)
            
            bot.edit_message_text(
                get_text(uid, 'topics_list'),
                chat_id,
                message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)

    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik", show_alert=True)

# ============================================
# /STATUS KOMANDASI
# ============================================

@bot.message_handler(commands=['status'])
def status_command_handler(message):
    uid = message.from_user.id
    
    # 1. Login tekshirish
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'))
        return
    
    # 2. Admin tekshirish
    if not is_admin(uid):
        bot.send_message(uid, "❌ Bu buyruq faqat admin uchun!")
        return
    
    # 3. Status yuborish
    try:
        stats = get_system_stats()
        status_text = format_system_status(uid, stats)
        bot.send_message(
            uid, 
            f"📊 <b>Tizim holati:</b>\n\n{status_text}", 
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Status xatolik: {e}")
        bot.send_message(uid, f"❌ Xatolik: {e}")

# ============================================
# PAROL O'ZGARTIRISH BUYRUQLARI
# ============================================
@bot.message_handler(commands=['newpass_user', 'newpass_admin'])
def change_password_handlers(message):
    uid = message.from_user.id
    text = message.text
    
    if not is_logged_in(uid):
        bot.reply_to(message, "⚠️ Avval botga kiring!")
        return

    parts = text.split()
    if len(parts) < 2:
        cmd = parts[0]
        bot.reply_to(message, f"⚠️ Xato! Parolni ham yozing.\nMisol: `{cmd} 8888`", parse_mode="Markdown")
        return

    new_pwd = parts[1]
    
    # Qaysi parolni o'zgartirishni aniqlaymiz
    role = 'user' if 'newpass_user' in text else 'admin'
    
    # FAYLGA SAQLASH (Tepada yozgan funksiyamiz)
    if update_password(role, new_pwd):
        bot.reply_to(message, f"✅ {role.capitalize()} paroli muvaffaqiyatli o'zgartirildi: `{new_pwd}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Xatolik yuz berdi. passwords.json faylini tekshiring.")
#============================================
#ASOSIY TEXT HANDLER
#============================================
@bot.message_handler(content_types=['text'])
def text_handler(message):
    """Barcha matnli xabarlar"""
    uid = message.from_user.id
    text = message.text.strip()
    # AGAR BUYRUQ BO'LSA, BU YERDA TO'XTATISH (YANGI QATOR)
    if text.startswith('/'):
        return
    # Login tekshirish
    if not is_logged_in(uid):
        bot.send_message(uid, get_text(uid, 'enter_password'))
        bot.register_next_step_handler(message, password_handler)
        return

    
    # Context tekshirish
    if uid not in user_context:
        user_context[uid] = {}

    data = load_user_data(uid)

    # %l - Hozirgi joy
    if text.lower() == "%l":
        bot.send_message(uid, get_location_text(uid))
        return

    # >35r1 - Bo'lim yaratish/tanlash
    if text.startswith(">"):
        match = re.match(r">(\d+)([rwl,]+)?(\d+)?(\.)?", text.lower())
        
        if not match:
            bot.send_message(uid, get_text(uid, 'error_format'))
            return
        
        t_num, sec_codes, q_num, view_mode = match.groups()
        topic_key = f"Topik-{t_num}"
        section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
        
        # Ko'rish rejimi
        if view_mode == ".":
            if topic_key not in data:
                bot.send_message(uid, get_text(uid, 'error_not_found'))
                return
            
            if sec_codes and q_num:
                sec_name = section_map.get(sec_codes[0])
                q_key = f"{q_num}-savol so'zlari"
                words = data.get(topic_key, {}).get(sec_name, {}).get(q_key, {})
                if not words:
                    bot.send_message(uid, "⚠️ Bu savolda so'zlar yo'q.")
                    return
                res = f"📑 {topic_key} > {sec_name} > {q_num}-savol:\n\n"
                res += "\n".join([f"🇰🇷 {k} - 🇺🇿 {v}" for k, v in words.items()])
                bot.send_message(uid, res)
            
            elif sec_codes:
                sec_name = section_map.get(sec_codes[0])
                chapters = list(data.get(topic_key, {}).get(sec_name, {}).keys())
                if not chapters:
                    bot.send_message(uid, "⚠️ Bo'lim bo'sh.")
                    return
                bot.send_message(uid, f"📂 {topic_key} > {sec_name} savollari:\n\n" + "\n".join(chapters))
            
            else:
                secs = list(data.get(topic_key, {}).keys())
                if not secs:
                    bot.send_message(uid, "⚠️ Topik bo'sh.")
                    return
                bot.send_message(uid, f"📚 {topic_key} bo'limlari:\n\n" + "\n".join([f"• {s}" for s in secs]))
            return
        
        # Yaratish rejimi
        is_new = False
        
        if topic_key not in data:
            data[topic_key] = {}
            is_new = True
        user_context[uid]["topic"] = topic_key
        
        active_sec = None
        if sec_codes:
            codes = sec_codes.replace(",", "")
            for c in codes:
                s_name = section_map.get(c)
                if s_name:
                    if s_name not in data[topic_key]:
                        data[topic_key][s_name] = {}
                        is_new = True
                    if not active_sec:
                        active_sec = s_name
            user_context[uid]["section"] = active_sec
        
        if q_num:
            q_key = f"{q_num}-savol so'zlari"
            if active_sec:
                if q_key not in data[topic_key][active_sec]:
                    data[topic_key][active_sec][q_key] = {}
                    is_new = True
                user_context[uid]["question"] = q_key
        
        # Savollarni tartibga solish
        if active_sec and topic_key in data and active_sec in data[topic_key]:
            sorted_questions = dict(sorted(
                data[topic_key][active_sec].items(),
                key=lambda x: int(re.search(r'\d+', x[0]).group()) if re.search(r'\d+', x[0]) else 0
            ))
            data[topic_key][active_sec] = sorted_questions
        
        save_user_data(uid, data)
        
        status = "yaratildi ✨" if is_new else "tanlandi ✅"
        loc = f"📍 {topic_key}"
        if active_sec:
            loc += f" > {active_sec}"
        if q_num:
            loc += f" > {q_num}-savol"
        
        bot.send_message(uid, f"{loc} {status}")
        return

    # rm. - O'chirish
    if text.lower().startswith("rm."):
        target = text[3:].strip()
        
        # Bo'limni o'chirish (rm.35r)
        if len(target) >= 2 and target[:-1].isdigit() and target[-1] in ['r', 'w', 'l']:
            topic_num = int(target[:-1])
            section_code = target[-1]
            topic_key = f"Topik-{topic_num}"
            
            section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
            section_name = section_map[section_code]
            
            if topic_key in data and section_name in data[topic_key]:
                backup_data = {
                    'type': 'section',
                    'topic': topic_key,
                    'section': section_name,
                    'content': data[topic_key][section_name]
                }
                create_backup(uid, 'section', backup_data, f"{topic_num}_{section_name}")
                
                del data[topic_key][section_name]
                save_user_data(uid, data)
                bot.send_message(
                    uid,
                    f"🗑 {topic_num}-topik > {section_name} o'chirildi\n\n"
                    f"💡 Qaytarish: rs.{topic_num}{section_code}"
                )
            else:
                bot.send_message(uid, get_text(uid, 'error_not_found'))
            return
        
        # Topikni o'chirish (rm.35)
        if target.isdigit():
            topic_num = int(target)
            topic_key = f"Topik-{topic_num}"
            
            if topic_key in data:
                backup_data = {
                    'type': 'topic',
                    'topic': topic_key,
                    'content': data[topic_key]
                }
                create_backup(uid, 'topic', backup_data, topic_num)
                
                del data[topic_key]
                save_user_data(uid, data)
                bot.send_message(
                    uid,
                    f"🗑 {topic_num}-topik o'chirildi\n\n"
                    f"💡 Qaytarish: rs.{topic_num}"
                )
            else:
                bot.send_message(uid, get_text(uid, 'error_not_found'))
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
                backup_data = {
                    'type': 'question',
                    'topic': topic_key,
                    'section': section_name,
                    'question_key': q_key,
                    'content': data[topic_key][section_name][q_key]
                }
                create_backup(uid, 'question', backup_data, target)
                
                del data[topic_key][section_name][q_key]
                save_user_data(uid, data)
                bot.send_message(uid, f"🗑 {topic_num}-topik > {section_name} > {q_num}-savol o'chirildi\n\n💡 Qaytarish: rs.{target}")
            else:
                bot.send_message(uid, get_text(uid, 'error_not_found'))
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
                        backup_data = {
                            'type': 'word',
                            'topic': t,
                            'section': s,
                            'question': q,
                            'korean': match_key,
                            'uzbek': data[t][s][q][match_key]
                        }
                        create_backup(uid, 'word', backup_data, word_to_rm)
                        
                        del data[t][s][q][match_key]
                        save_user_data(uid, data)
                        msg = get_text(uid, 'word_deleted', word=match_key) + f"\n\n💡 Qaytarish: rs.{word_to_rm}"
                        bot.send_message(uid, msg)
                        found = True
                        break
                if found:
                    break
            if found:
                break
        
        if not found:
            bot.send_message(uid, get_text(uid, 'word_not_found'))
        return

    # rs. - Tiklash
    if text.lower().startswith("rs."):
        target = text[3:].strip()
        backup_file = None
        
        # Topikni tiklash (rs.35)
        if target.isdigit():
            topic_num = int(target)
            backup_files = [f for f in os.listdir(BACKUPS_DIR) if f.startswith(f'backup_topic_{uid}_{topic_num}')]
            if backup_files:
                backup_file = os.path.join(BACKUPS_DIR, backup_files[0])
        
        # Bo'limni tiklash (rs.35r)
        elif len(target) >= 2 and target[:-1].isdigit() and target[-1] in ['r', 'w', 'l']:
            topic_num = int(target[:-1])
            section_code = target[-1]
            section_map = {'r': 'reading', 'w': 'writing', 'l': 'listening'}
            section_name = section_map[section_code]
            backup_files = [f for f in os.listdir(BACKUPS_DIR) if f.startswith(f'backup_section_{uid}_{topic_num}_{section_name}')]
            if backup_files:
                backup_file = os.path.join(BACKUPS_DIR, backup_files[0])
        
        # Savolni tiklash (rs.35r33)
        elif any(c in target for c in ['r', 'w', 'l']) and target[-1].isdigit():
            backup_files = [f for f in os.listdir(BACKUPS_DIR) if f.startswith(f'backup_question_{uid}_{target}')]
            if backup_files:
                backup_file = os.path.join(BACKUPS_DIR, backup_files[0])
        
        # So'zni tiklash (rs.so'z)
        else:
            safe_name = "".join(x for x in target if x.isalnum())
            backup_files = [f for f in os.listdir(BACKUPS_DIR) if f.startswith(f'backup_word_{uid}_{safe_name}') or f.startswith(f'backup_word_{uid}_{target}')]
            if backup_files:
                backup_file = os.path.join(BACKUPS_DIR, backup_files[0])
        
        if backup_file and os.path.exists(backup_file):
            try:
                backup_data = restore_from_backup(backup_file)
                
                if backup_data['type'] == 'topic':
                    data[backup_data['topic']] = backup_data['content']
                elif backup_data['type'] == 'section':
                    if backup_data['topic'] not in data:
                        data[backup_data['topic']] = {}
                    data[backup_data['topic']][backup_data['section']] = backup_data['content']
                elif backup_data['type'] == 'question':
                    t_k = backup_data['topic']
                    s_k = backup_data['section']
                    q_k = backup_data['question_key']
                    if t_k not in data:
                        data[t_k] = {}
                    if s_k not in data[t_k]:
                        data[t_k][s_k] = {}
                    data[t_k][s_k][q_k] = backup_data['content']
                elif backup_data['type'] == 'word':
                    t_k = backup_data['topic']
                    s_k = backup_data['section']
                    q_k = backup_data['question']
                    kor = backup_data['korean']
                    uz = backup_data['uzbek']
                    if t_k not in data:
                        data[t_k] = {}
                    if s_k not in data[t_k]:
                        data[t_k][s_k] = {}
                    if q_k not in data[t_k][s_k]:
                        data[t_k][s_k][q_k] = {}
                    data[t_k][s_k][q_k][kor] = uz
                
                save_user_data(uid, data)
                delete_backup(backup_file)
                
                bot.send_message(uid, get_text(uid, 'word_restored'))
            except Exception as e:
                bot.send_message(uid, f"❌ Xatolik: {e}")
        else:
            bot.send_message(uid, "❌ Backup fayl topilmadi")
        return

    # s.so'z - Qidirish
    if text.lower().startswith("s."):
        query = text[2:].strip().lower()
        results = []
        
        for t, s_dict in data.items():
            topic_num = t.replace("Topik-", "")
            for s, q_dict in s_dict.items():
                for q, w_dict in q_dict.items():
                    q_num = q.replace("-savol so'zlari", "")
                    for ko, uz in w_dict.items():
                        if query in ko.lower() or query in uz.lower():
                            results.append(f"📍 {topic_num}-topik > {s.upper()} > {q_num}-savol: {ko} → {uz}")
        
        if results:
            msg = "🔍 TOPILDI:\n\n" + "\n\n".join(results[:20])
            if len(results) > 20:
                msg += f"\n\n... va yana {len(results)-20} ta natija"
        else:
            msg = "❌ Topilmadi"
        
        bot.send_message(uid, msg)
        return

    # Savol raqami (faqat raqam)
    if text.isdigit():
        if user_context[uid].get("section"):
            q_key = f"{text}-savol so'zlari"
            t = user_context[uid]["topic"]
            s = user_context[uid]["section"]
            
            if q_key not in data[t][s]:
                data[t][s][q_key] = {}
                save_user_data(uid, data)
            
            user_context[uid]["question"] = q_key
            bot.send_message(uid, f"📍 {text}-savol tanlandi. So'zlarni yuboring:")
        else:
            bot.send_message(uid, get_text(uid, 'error_no_location'))
        return

    # So'z qo'shish
    if " " in text and not text.startswith(">"):
        t = user_context[uid].get("topic")
        s = user_context[uid].get("section")
        q = user_context[uid].get("question")
        
        if not t or not s or not q:
            bot.send_message(uid, get_text(uid, 'error_no_location'))
            return
        
        lines = text.strip().split('\n')
        added_count = 0
        added_words_list = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
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
                    if re.search(r'[가-힣]', p1):
                        kor, uzb = p1, p2
                    else:
                        kor, uzb = p2, p1
                else:
                    continue
            
            if t not in data:
                data[t] = {}
            if s not in data[t]:
                data[t][s] = {}
            if q not in data[t][s]:
                data[t][s][q] = {}
            
            data[t][s][q][kor] = uzb
            added_words_list.append(f"• {kor} - {uzb}")
            added_count += 1
        
        if added_count > 0:
            save_user_data(uid, data)
            
            clean_q = q.replace("-savol so'zlari", "")
            report = get_text(uid, 'word_added', count=added_count) + "\n\n"
            report += "\n".join(added_words_list)
            report += f"\n\n{get_text(uid, 'word_saved_location', topic=t, section=s.upper(), question=clean_q)}"
            
            bot.send_message(uid, report)
        else:
            bot.send_message(uid, get_text(uid, 'error_format'))
        return



# ============================================
# MONITORING (AUTO)
# ============================================
def auto_monitor():
    """Avtomatik monitoring"""
    while True:
        try:
            if ADMIN_ID:
                check_battery_warning(bot, ADMIN_ID)
        except:
            pass
        time.sleep(600)

def clean_old_backups():
    """Eski backuplarni tozalash"""
    while True:
        try:
            now = time.time()
            cutoff = now - (BACKUP_CLEANUP_HOURS * 3600)

            if os.path.exists(BACKUPS_DIR):
                deleted_count = 0
                for f in os.listdir(BACKUPS_DIR):
                    if f.startswith("backup_") and f.endswith(".json"):
                        file_path = os.path.join(BACKUPS_DIR, f)
                        if os.path.getmtime(file_path) < cutoff:
                            os.remove(file_path)
                            deleted_count += 1
                
                if deleted_count > 0:
                    print(f"🧹 Tozalash: {deleted_count} ta eski backup o'chirildi.")
        except Exception as e:
            print(f"❌ Tozalashda xato: {e}")
        
        time.sleep(3600)

# ============================================
# ISHGA TUSHIRISH
# ============================================
if __name__ == "__main__":
    # Threading - Monitoringni alohida oqimda ishga tushirish
    threading.Thread(target=clean_old_backups, daemon=True).start()

    try:
        me = bot.get_me()
        print(f"\n{'='*40}")
        print(f"BOT: @{me.username}")
        print(f"STATUS: RUNNING ✅")
        print(f"{'='*40}\n")
        bot.infinity_polling()
    except Exception as e:
        print(f"ERROR: {e}")