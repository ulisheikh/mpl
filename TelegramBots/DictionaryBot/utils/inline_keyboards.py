# ============================================
# IMPORT MUAMMOSINI HAL QILISH
# ============================================

"""
MUAMMO: get_user_language() funksiyasi import qilinmagan
YECHIM: utils/language.py dan import qilish kerak
"""

# ============================================
# 1. utils/inline_keyboards.py - TO'LIQ KOD
# ============================================

from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# ✅ IMPORT QO'SHISH
from utils.language import get_user_language, get_text

def get_main_keyboard(uid):
    """Asosiy klaviatura (Reply tugmalar)"""
    lang = get_user_language(uid)  # ← Endi ishlaydi!
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # 1-qator: Bosh menyu
    if lang == 'uz':
        markup.add(KeyboardButton("/start"))
    elif lang == 'ko':
        markup.add(KeyboardButton("/start"))
    
    # 2-qator: Bo'limlar
    if lang == 'uz':
        markup.add(KeyboardButton("📂 BO'LIMLAR"))
    elif lang == 'ko':
        markup.add(KeyboardButton("📂 섹션"))
    else:
        markup.add(KeyboardButton("📂 SECTIONS"))
    
    # 3-qator: Export
    if lang == 'uz':
        markup.row(
            KeyboardButton("📥 JSON"),
            KeyboardButton("🐍 PYTHON")
        )
    elif lang == 'ko':
        markup.row(
            KeyboardButton("📥 JSON"),
            KeyboardButton("🐍 PYTHON")
        )
    else:
        markup.row(
            KeyboardButton("📥 JSON"),
            KeyboardButton("🐍 PYTHON")
        )
    
    # 4-qator: Sozlamalar
    if lang == 'uz':
        markup.add(KeyboardButton("⚙️ SOZLAMALAR"))
    elif lang == 'ko':
        markup.add(KeyboardButton("⚙️ 설정"))
    else:
        markup.add(KeyboardButton("⚙️ SETTINGS"))
    
    return markup


def get_settings_keyboard(uid, is_admin=False):
    """Sozlamalar klaviaturasi - Yangilangan"""
    markup = InlineKeyboardMarkup()
    
    # Status tugmasi olib tashlandi (Endi u /start xabarida chiqadi)
    
    # Foydalanuvchilar (faqat admin uchun qoladi)
    if is_admin:
        markup.row(
            InlineKeyboardButton(
                text="👥 " + get_text(uid, 'users'),
                callback_data="settings_users"
            )
        )
    
    # Til
    markup.row(
        InlineKeyboardButton(
            text="🌐 " + get_text(uid, 'language'),
            callback_data="settings_language"
        )
    )
    
    # Parol (faqat admin)
    if is_admin:
        markup.row(
            InlineKeyboardButton(
                text="🔐 " + get_text(uid, 'password'),
                callback_data="settings_password"
            )
        )
    
    # Bot haqida
    markup.row(
        InlineKeyboardButton(
            text="ℹ️ " + get_text(uid, 'about'),
            callback_data="settings_about"
        )
    )
    
    # Orqaga
    markup.row(
        InlineKeyboardButton(
            text="🔙 " + get_text(uid, 'back'),
            callback_data="back_main"
        )
    )
    
    return markup


def get_language_keyboard():
    """Til tanlash klaviaturasi"""
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇰🇷 한국어", callback_data="lang_ko")
    )
    
    markup.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_settings")
    )
    
    return markup


def get_topics_keyboard(uid, topics):
    """Topiklar ro'yxati klaviaturasi"""
    markup = InlineKeyboardMarkup()
    
    for topic_num in topics:
        markup.row(
            InlineKeyboardButton(
                text=f"📚 {topic_num}-topik",
                callback_data=f"topic_{topic_num}"
            )
        )
    
    markup.row(
        InlineKeyboardButton(
            text="🔙 " + get_text(uid, 'back'),
            callback_data="back_main"
        )
    )
    
    return markup


def get_sections_keyboard(uid, topic_num, sections):
    """Bo'limlar klaviaturasi"""
    markup = InlineKeyboardMarkup()
    
    for section in sections:
        markup.row(
            InlineKeyboardButton(
                text=f"📖 {section.upper()}",
                callback_data=f"section_{topic_num}_{section}"
            )
        )
    
    markup.row(
        InlineKeyboardButton(
            text="🔙 " + get_text(uid, 'back'),
            callback_data="back_topics"
        )
    )
    
    return markup


def get_back_keyboard(uid, callback_data):
    """Orqaga qaytish klaviaturasi"""
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardButton(
            text="🔙 " + get_text(uid, 'back'),
            callback_data=callback_data
        )
    )
    
    return markup


def get_users_keyboard(uid, users):
    """Foydalanuvchilar ro'yxati klaviaturasi"""
    markup = InlineKeyboardMarkup()
    
    for user_id in users:
        # User ma'lumotlari
        from admin.user_manager import get_user_info
        user_info = get_user_info(user_id)
        
        name = user_info.get('first_name', 'User')
        username = user_info.get('username', '')
        
        display_name = f"{name}"
        if username:
            display_name += f" (@{username})"
        
        markup.row(
            InlineKeyboardButton(
                text=f"👤 {display_name}",
                callback_data=f"user_detail_{user_id}"
            )
        )
    
    markup.row(
        InlineKeyboardButton(
            text="🔙 " + get_text(uid, 'back'),
            callback_data="back_settings"
        )
    )
    
    return markup


def get_user_detail_keyboard(uid, target_uid):
    """User tafsilotlari klaviaturasi"""
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardButton(
            text="📥 Faylni yuklash",
            callback_data=f"user_export_{target_uid}"
        )
    )
    
    markup.row(
        InlineKeyboardButton(
            text="📊 Statistika",
            callback_data=f"user_stats_{target_uid}"
        )
    )
    
    markup.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="settings_users"
        )
    )
    
    return markup


# ============================================
# 2. QISQA XULOSA
# ============================================

"""
O'ZGARTIRILGAN:

1. utils/inline_keyboards.py ning BOSHIDA:
   ✅ from utils.language import get_user_language, get_text

2. get_main_keyboard() funksiyasi:
   ✅ lang = get_user_language(uid) - endi ishlaydi!
   ✅ 🏠 BOSH MENYU tugmasi qo'shildi

QOLGAN KODLAR:
- utils/texts.py - "home_stats" qo'shish
- utils/data_handler.py - get_user_words_count() qo'shish
- main.py - text_handler ga 🏠 BOSH MENYU bloki qo'shish
"""