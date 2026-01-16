"""
DictionaryBot - User boshqaruv moduli
Userlar haqida to'liq ma'lumot
"""

import os
import json
from datetime import datetime
from config import USER_DATA_DIR, DATABASE_DIR, USERS_INFO_FILE


def ensure_users_info_file():
    """users_info.json faylini yaratish"""
    if not os.path.exists(USERS_INFO_FILE):
        with open(USERS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def save_user_info(user_id, first_name=None, last_name=None, username=None):
    """User ma'lumotlarini saqlash"""
    ensure_users_info_file()
    
    with open(USERS_INFO_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    uid = str(user_id)
    
    # Yangi user yoki mavjud userni yangilash
    if uid not in users:
        users[uid] = {
            "first_name": first_name or "User",
            "last_name": last_name or "",
            "username": username or "",
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        # Mavjud ma'lumotlarni yangilash
        if first_name:
            users[uid]["first_name"] = first_name
        if last_name:
            users[uid]["last_name"] = last_name
        if username:
            users[uid]["username"] = username
    
    with open(USERS_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def get_user_info(user_id):
    """User ma'lumotlarini olish"""
    ensure_users_info_file()
    
    with open(USERS_INFO_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    uid = str(user_id)
    
    if uid in users:
        return users[uid]
    
    # Ma'lumot yo'q bo'lsa default
    return {
        "first_name": "User",
        "last_name": "",
        "username": "",
        "joined_at": "Unknown"
    }


def get_all_users():
    """Barcha userlar ro'yxati"""
    if not os.path.exists(USER_DATA_DIR):
        return []
    
    users = []
    
    for filename in os.listdir(USER_DATA_DIR):
        if filename.startswith('user_') and filename.endswith('.json'):
            if '.backup' in filename:
                continue
            
            user_id = filename.replace('user_', '').replace('.json', '')
            users.append(user_id)
    
    return users


def get_user_file(user_id):
    """User fayl yo'li"""
    return os.path.join(USER_DATA_DIR, f"user_{user_id}.json")


def get_user_stats(user_id):
    """User statistikasi"""
    user_file = get_user_file(user_id)
    
    if not os.path.exists(user_file):
        return {
            'topics': 0,
            'words': 0,
            'size': '0 B'
        }
    
    # Fayl hajmi
    size_bytes = os.path.getsize(user_file)
    if size_bytes < 1024:
        size = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size = f"{size_bytes / 1024:.1f} KB"
    else:
        size = f"{size_bytes / (1024 * 1024):.1f} MB"
    
    # Topik va so'zlar soni
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topics = len([k for k in data.keys() if k.startswith('Topik-')])
        
        words = 0
        for topic in data.values():
            for section in topic.values():
                for question in section.values():
                    words += len(question)
        
        return {
            'topics': topics,
            'words': words,
            'size': size
        }
    except:
        return {
            'topics': 0,
            'words': 0,
            'size': size
        }


def get_user_details(user_id):
    """User to'liq ma'lumotlari"""
    info = get_user_info(user_id)
    stats = get_user_stats(user_id)
    
    return {
        'user_id': user_id,
        'first_name': info['first_name'],
        'last_name': info['last_name'],
        'username': info['username'],
        'joined_at': info['joined_at'],
        'topics': stats['topics'],
        'words': stats['words'],
        'size': stats['size']
    }


def format_user_details(current_user_id, details):
    """User ma'lumotlarini formatlash"""
    full_name = f"{details['first_name']} {details['last_name']}".strip()
    username = f"@{details['username']}" if details['username'] else "Username yo'q"
    
    msg = f"📊 <b>Foydalanuvchi ma'lumotlari</b>\n\n"
    msg += f"👤 <b>Ism:</b> {full_name}\n"
    msg += f"🆔 <b>Username:</b> {username}\n"
    msg += f"📱 <b>ID:</b> <code>{details['user_id']}</code>\n"
    msg += f"📅 <b>Qo'shilgan:</b> {details['joined_at']}\n\n"
    msg += f"📚 <b>Topiklar:</b> {details['topics']} ta\n"
    msg += f"📝 <b>So'zlar:</b> {details['words']} ta\n"
    msg += f"💾 <b>Fayl hajmi:</b> {details['size']}\n"
    
    return msg


def format_users_list(current_user_id, users_list):
    """Userlar ro'yxatini formatlash"""
    if not users_list:
        msg = "❌ Hech qanday foydalanuvchi topilmadi."
        return msg
    
    msg = f"👥 <b>Foydalanuvchilar ro'yxati</b> ({len(users_list)} ta)\n\n"
    
    for idx, user_id in enumerate(users_list, 1):
        details = get_user_details(user_id)
        
        full_name = f"{details['first_name']} {details['last_name']}".strip()
        username = f"@{details['username']}" if details['username'] else "❌"
        
        msg += f"📊 <b>#{idx}</b>\n"
        msg += f"├ 👤 {full_name}\n"
        msg += f"├ 🆔 {username}\n"
        msg += f"├ 📱 ID: <code>{user_id}</code>\n"
        msg += f"├ 📚 Topiklar: {details['topics']}\n"
        msg += f"├ 📝 So'zlar: {details['words']}\n"
        msg += f"└ 💾 Hajm: {details['size']}\n\n"
    
    return msg


def delete_user_data(user_id):
    """User ma'lumotlarini o'chirish"""
    user_file = get_user_file(user_id)
    backup_file = f"{user_file}.backup"
    
    deleted = False
    
    # Asosiy faylni o'chirish
    if os.path.exists(user_file):
        os.remove(user_file)
        deleted = True
    
    # Backup faylni o'chirish
    if os.path.exists(backup_file):
        os.remove(backup_file)
    
    # users_info.json dan o'chirish
    ensure_users_info_file()
    
    with open(USERS_INFO_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    uid = str(user_id)
    if uid in users:
        del users[uid]
        
        with open(USERS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    return deleted
def get_user_words_count(user_id):
    """User so'zlari sonini hisoblash"""
    user_file = get_user_file(user_id)
    
    if not os.path.exists(user_file):
        return 0
    
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        words = 0
        for topic in data.values():
            for section in topic.values():
                for question in section.values():
                    words += len(question)
        
        return words
    except:
        return 0