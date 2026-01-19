# -*- coding: utf-8 -*-
"""
AUTENTIFIKATSIYA TIZIMI
Parol va session boshqaruvi
"""

import json
import os
import time
from config import *

# GLOBAL VARIABLES
USER_SESSIONS = {}
LOGIN_ATTEMPTS = {}
BLOCKED_USERS = {}

def load_passwords():
    """Parollarni yuklash"""
    if os.path.exists(PASSWORDS_FILE):
        try:
            with open(PASSWORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_passwords(passwords):
    """Parollarni saqlash"""
    os.makedirs(os.path.dirname(PASSWORDS_FILE), exist_ok=True)
    with open(PASSWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(passwords, f, ensure_ascii=False, indent=4)

import json
import os

def update_password(role, new_password):
    # FAYL YO'LI ANIQLANDI:
    file_path = "database/passwords.json" 
    
    if os.path.exists(file_path):
        try:
            # 1. Asl faylni o'qiymiz
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 2. Yangilaymiz
            if role == 'user':
                data['user_password'] = str(new_password)
            elif role == 'admin':
                data['admin_password'] = str(new_password)
                
            # 3. Aynan o'sha faylga qayta yozamiz
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Parol {file_path} ichida yangilandi!")
            return True
        except Exception as e:
            print(f"❌ Faylga yozishda xato: {e}")
            return False
    else:
        print(f"❌ Xato: {file_path} topilmadi!")
        return False

def load_sessions():
    """Sessiyalarni yuklash"""
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_sessions(sessions):
    """Sessiyalarni saqlash"""
    os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=4)

def initialize_passwords():
    """Default parollarni o'rnatish"""
    passwords = load_passwords()
    if not passwords:
        passwords = {
            'user': DEFAULT_USER_PASSWORD,
            'admin': DEFAULT_ADMIN_PASSWORD
        }
        save_passwords(passwords)
    return passwords

def verify_password(user_id, password):
    """Parolni tekshirish"""
    passwords = load_passwords()
    
    if password == passwords.get('admin', DEFAULT_ADMIN_PASSWORD):
        return 'admin'
    elif password == passwords.get('user', DEFAULT_USER_PASSWORD):
        return 'user'
    else:
        return None

def is_user_blocked(user_id):
    """Foydalanuvchi bloklangan yoki yo'qligini tekshirish"""
    if user_id in BLOCKED_USERS:
        if time.time() < BLOCKED_USERS[user_id]:
            return True
        else:
            del BLOCKED_USERS[user_id]
            LOGIN_ATTEMPTS[user_id] = 0
    return False

def add_login_attempt(user_id):
    """Login urinishni qo'shish"""
    if user_id not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[user_id] = 0
    LOGIN_ATTEMPTS[user_id] += 1
    
    if LOGIN_ATTEMPTS[user_id] >= 3:
        # 5 daqiqaga bloklash
        BLOCKED_USERS[user_id] = time.time() + 300
        return True
    return False

def login_user(user_id, role):
    """Foydalanuvchini tizimga kiritish"""
    global USER_SESSIONS
    USER_SESSIONS[user_id] = {
        'role': role,
        'logged_in': True
    }
    
    # Sessiyani saqlash
    sessions = load_sessions()
    sessions[str(user_id)] = USER_SESSIONS[user_id]
    save_sessions(sessions)
    
    # Login urinishlarni tozalash
    if user_id in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[user_id] = 0

def logout_user(user_id):
    """Foydalanuvchini tizimdan chiqarish"""
    global USER_SESSIONS
    if user_id in USER_SESSIONS:
        del USER_SESSIONS[user_id]
    
    sessions = load_sessions()
    if str(user_id) in sessions:
        del sessions[str(user_id)]
    save_sessions(sessions)

def is_logged_in(user_id):
    """Foydalanuvchi tizimga kirgan yoki yo'qligini tekshirish"""
    # Global sessiyadan tekshirish
    if user_id in USER_SESSIONS:
        return USER_SESSIONS[user_id].get('logged_in', False)
    
    # Fayldan yuklash
    sessions = load_sessions()
    if str(user_id) in sessions:
        USER_SESSIONS[user_id] = sessions[str(user_id)]
        return sessions[str(user_id)].get('logged_in', False)
    
    return False

def get_user_role(user_id):
    """Foydalanuvchi rolini olish"""
    if user_id in USER_SESSIONS:
        return USER_SESSIONS[user_id].get('role', 'user')
    
    sessions = load_sessions()
    if str(user_id) in sessions:
        return sessions[str(user_id)].get('role', 'user')
    
    return 'user'

def is_admin(user_id):
    """Admin yoki yo'qligini tekshirish"""
    return get_user_role(user_id) == 'admin'

def change_password(role, new_password):
    """Parolni o'zgartirish"""
    passwords = load_passwords()
    passwords[role] = new_password
    save_passwords(passwords)

# Default parollarni o'rnatish
initialize_passwords()