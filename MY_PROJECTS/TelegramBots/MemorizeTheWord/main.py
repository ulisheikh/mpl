import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, 
    CallbackQuery, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
# my_id = 8515364508
from config import BOT_TOKEN, ADMIN_PASSWORD, DICTIONARY_PATH, USER_DB_PATH
from utils.db_handler import DictionaryHandler
from database.db import UserDatabase

# Initialization
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
auto_mode_users = set()

dict_handler = DictionaryHandler(DICTIONARY_PATH)
user_db = UserDatabase(USER_DB_PATH)

# FSM States
class GameState(StatesGroup):
    playing = State()


class AdminState(StatesGroup):
    waiting_password = State()
    waiting_block_reason = State()

# Translations
# Translations
TEXTS = {
    "uz": {
        "choose_language": "Tilni tanlang:",
        "language_changed": "Til muvaffaqiyatli o'zgartirildi! ✅",
        "start_message": """
🎓 <b>Memorize Bot'ga xush kelibsiz!</b>

Bu bot TOPIK so'zlarini smart tarzda yodlashga yordam beradi.

📊 Statistikangizni ko'rish
📈 Bot haqida ma'lumot
🎯 So'z yodlashni boshlash

Quyidagi tugmalardan foydalaning! 👇
""",
        "blocked_message": "❌ Siz bloklangansiz.\n\n📝 Sabab: {reason}",
        "main_menu": "Asosiy menyu:",
        "game_mode": "🎮 O'yin",
        "auto_mode": "🤖 Avtomatik",
        "chapters": "📂 Bo'limlar",
        "settings": "⚙️ Sozlamalar",
        "statistics": "📊 Statistika",
        "bot_stats": "📈 Bot Statistikasi",
        "admin_panel": "🔐 Admin Panel",
        "stop_game": "🛑 To'xtatish",
        "back": "◀️ Orqaga",
        "about_bot_btn": "ℹ️ Bot haqida",
        "my_stats": """
📊 <b>Sizning statistikangiz:</b>

✅ To'g'ri javoblar: {correct}
❌ Noto'g'ri javoblar: {wrong}
⏱ Faol vaqt: {time} daqiqa
🏆 Reyting: {rank}/{total}
""",
        "bot_statistics": """
📈 <b>Bot Statistikasi:</b>

👥 Jami foydalanuvchilar: {users}
📚 Bazadagi so'zlar: {words}
""",
        "about_bot": """
ℹ️ <b>Bot haqida:</b>

📌 Versiya: 2.0
🔧 Texnologiya: Aiogram 3
💾 Database: SQLite
🎯 Maqsad: TOPIK so'zlarini yodlash

🎮 O'yin rejimi - cheksiz mashq
🤖 Avtomatik - har 15 minutda xabar
📂 Bo'limlar - Topik bo'yicha
""",
        "change_language": "Tilni o'zgartirish:",
        "admin_enter_password": "🔐 Admin panelga kirish uchun parolni kiriting:",
        "admin_wrong_password": "❌ Noto'g'ri parol!",
        "admin_welcome": "✅ Admin panelga xush kelibsiz!",
        "admin_users": "👥 Foydalanuvchilar",
        "admin_user_list": "📋 Foydalanuvchilar ro'yxati:",
        "admin_block": "🚫 Bloklash",
        "admin_unblock": "✅ Blokdan chiqarish",
        "admin_enter_block_reason": "📝 Bloklash sababini yozing (ixtiyoriy):\n\nBekor qilish uchun /cancel yozing",
        "admin_user_blocked": "✅ Foydalanuvchi bloklandi!",
        "admin_user_unblocked": "✅ Foydalanuvchi blokdan chiqarildi!",
        "game_question": "🎮 <b>{uzbek}</b>\n\n📝 Koreys tilida yozing:",
        "game_correct": "✅ To'g'ri!\n\n🇺🇿 {uzbek}\n🇰🇷 {korean}",
        "game_wrong": "❌ Noto'g'ri!\n\n🇺🇿 {uzbek}\n🇰🇷 {korean}\n\n📌 Siz yozgan: {user_answer}",
        "game_stopped": "🛑 O'yin to'xtatildi!\n\n✅ To'g'ri: {correct}\n❌ Noto'g'ri: {wrong}",
        "auto_mode_started": "🤖 Avtomatik rejim yoqildi!\n\nHar 15 minutda 10-15 ta so'z yuboriladi.",
        "auto_mode_stopped": "🤖 Avtomatik rejim o'chirildi!",
        "auto_mode_active": "⚠️ Avtomatik rejim allaqachon faol!",
        "chapters_select_topic": "📂 Topikni tanlang:",
        "chapters_select_section": "📖 Bo'limni tanlang:",
        "chapters_select_chapter": "📝 Bobni tanlang:",
        "chapters_words": "📚 <b>{chapter}</b>\n\nJami so'zlar: {count}",
        "no_words": "❌ So'zlar topilmadi!",
        "next_question": "➡️ Keyingi savol",
        "back_to_menu": "🏠 Asosiy menyu",
    },
    "kr": {
        "choose_language": "언어 선택:",
        "language_changed": "언어가 성공적으로 변경되었습니다! ✅",
        "start_message": "🎓 <b>Memorize Bot에 오신 것을 환영합니다!</b>",
        "main_menu": "메인 메뉴:",
        "settings": "⚙️ 설정",
        "about_bot_btn": "ℹ️ 봇 정보",
        "about_bot": "ℹ️ <b>봇 정보:</b>\n\nTOPIK 단어 학습 봇 버전 2.0",
        "change_language": "언어 변경:",
        "back_to_menu": "🏠 메인 메뉴",
        "game_mode": "🎮 게임",
        "auto_mode": "🤖 자동 모드",
        "statistics": "📊 통계",
        "no_words": "❌ 단어를 찾을 수 없습니다!",
        "game_question": "🎮 <b>{uzbek}</b>\n\n📝 한국어로 쓰세요:",
    }
}

def get_text(lang: str, key: str, **kwargs) -> str:
    """Til bo'yicha matn olish"""
    text = TEXTS.get(lang, TEXTS['uz']).get(key, key)
    return text.format(**kwargs) if kwargs else text

#keyboards 2-qism

def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi - YANGILANGAN"""
    keyboard = [
        [KeyboardButton(text="/start")],
        [
            KeyboardButton(text="/avtomatik"),
            KeyboardButton(text="/game")
        ],
        [
            KeyboardButton(text="/bo'limlar"),
            KeyboardButton(text="/sozlamalar")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard(lang):
    # Bu yerda tugmalar nomi lug'atdan olinadi
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕹 Game", callback_data="start_game"),
         InlineKeyboardButton(text="🤖 Avtomatik", callback_data="toggle_auto")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")]
    ])
    return keyboard
def get_game_keyboard(lang: str) -> InlineKeyboardMarkup:
    """O'yin klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text=get_text(lang, "stop_game"), callback_data="stop_game")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_topics_keyboard() -> InlineKeyboardMarkup:
    """Topiklar ro'yxati"""
    topics = dict_handler.get_all_topics()
    keyboard = []
    
    for topic in topics:
        keyboard.append([
            InlineKeyboardButton(text=topic, callback_data=f"topic_{topic}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_sections_keyboard(topic: str) -> InlineKeyboardMarkup:
    """Bo'limlar (reading, writing, listening)"""
    sections = dict_handler.get_topic_sections(topic)
    keyboard = []
    
    for section in sections:
        keyboard.append([
            InlineKeyboardButton(text=section.title(), callback_data=f"section_{topic}_{section}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="chapters_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_chapters_keyboard(topic: str, section: str) -> InlineKeyboardMarkup:
    """Boblar (9-savol, 13-savol...)"""
    chapters = dict_handler.get_section_chapters(topic, section)
    keyboard = []
    
    for chapter in chapters:
        keyboard.append([
            InlineKeyboardButton(text=chapter, callback_data=f"chapter_{topic}_{section}_{chapter}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"topic_{topic}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash klaviaturasi"""
    keyboard = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
        ],
        [
            InlineKeyboardButton(text="🇰🇷 한국어", callback_data="lang_kr")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_settings_keyboard(lang: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📈 So'zlar statistikasi", callback_data="showWord_info")],
        [InlineKeyboardButton(text="🤖 Bot holati", callback_data="bot_status")],
        [InlineKeyboardButton(text=get_text(lang, "change_language"), callback_data="change_language")],
        [InlineKeyboardButton(text=get_text(lang, "about_bot_btn"), callback_data="about_bot")],
    ]

    # 🔐 Faqat admin bo‘lsa chiqadi
    if is_admin:
        buttons.append(
            [InlineKeyboardButton(text="🔐 Admin panel", callback_data="admin_panel")]
        )

    buttons.append(
        [InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Admin panel klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text=get_text(lang, "admin_users"), callback_data="admin_users")],
        [InlineKeyboardButton(text=get_text(lang, "statistics"), callback_data="admin_stats")],
        [InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
# main.py ichidagi /sozlamalar handleri va callback qismiga

@router.message(F.text.in_({"⚙️ Sozlamalar", "⚙️ Settings", "⚙️ 설정"}))
async def settings_handler(message: Message):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    await message.answer(
        get_text(lang, "settings_menu"),
        reply_markup=get_settings_keyboard(lang)
    )

@router.callback_query(F.data == "bot_status")
async def bot_status_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    is_admin = await user_db.is_admin(user_id)

    text = "🤖 <b>Bot holati:</b>\n\n✅ Faol"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(lang, is_admin)
    )
    await callback.answer()

InlineKeyboardButton(
    text="📈 So'zlar statistikasi",
    callback_data="showWord_info"
)

# Tugma bosilganda ishlaydigan handler
# @router.callback_query(F.data == "showWord_info")

#3-qism Basic Handlers

# Middleware
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

class BlockCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        is_blocked, reason = await user_db.is_blocked(user_id)
        
        if is_blocked:
            lang = await user_db.get_language(user_id)
            reason_text = reason or "No reason provided"
            await event.answer(get_text(lang, "blocked_message", reason=reason_text))
            return
        
        return await handler(event, data)

router.message.middleware(BlockCheckMiddleware())

# /start command
# /start command - YANGILANGAN
@router.message(Command("sozlamalar"))
async def cmd_settings(message: Message):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    is_admin = await user_db.is_admin(user_id)

    await message.answer(
        get_text(lang, "settings_menu"),
        reply_markup=get_settings_keyboard(lang, is_admin)
    )


# /sozlamalar command
# main.py taxminan 382-qator
# @router.message(Command("sozlamalar"))
# async def cmd_settings(message: Message):
#     user_id = message.from_user.id
#     lang = await user_db.get_language(user_id) or "uz"

#     await message.answer(
#         get_text(lang, "settings_menu"),
#         reply_markup=get_settings_keyboard(lang)
#     )


# main.py ichid

# /bo'limlar command
@router.message(Command("bo'limlar"))
async def cmd_chapters(message: Message):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id)
    
    await message.answer(
        get_text(lang, "chapters_select_topic"),
        reply_markup=get_chapters_topics_keyboard()
    )
# Til tanlash callback (main.py ichida change_language funksiyasi o'rniga)
@router.callback_query(F.data.startswith("lang_"))
async def set_language_callback(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    await user_db.set_language(user_id, lang)
    await callback.message.delete()
    
    # Yangi tilda javob yuborish
    await callback.message.answer(
        get_text(lang, "language_changed"),
        reply_markup=get_main_keyboard(lang) # Bu yerda pastki tugmalar chiqadi
    )
    await callback.answer()
# Statistika callback
@router.callback_query(F.data == "my_stats")
async def show_my_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    stats = await user_db.get_statistics(user_id)
    rank, total = await user_db.get_ranking(user_id)
    
    time_minutes = stats['active_time'] // 60
    
    await callback.message.edit_text(
        get_text(
            lang, "my_stats",
            correct=stats['correct'],
            wrong=stats['wrong'],
            time=time_minutes,
            rank=rank,
            total=total
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")]
        ])
    )
    await callback.answer()

# Bot statistikasi callback
@router.callback_query(F.data == "bot_stats")
async def show_bot_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    total_users = await user_db.get_total_users()
    total_words = dict_handler.get_total_words()
    
    await callback.message.edit_text(
        get_text(lang, "bot_statistics", users=total_users, words=total_words),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")]
        ])
    )
    await callback.answer()

# Sozlamalar
@router.message(F.text.in_([
    TEXTS['uz']['settings'],
    TEXTS['kr']['settings']
]))
async def show_settings(message: Message):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id)
    
    await message.answer(
        get_text(lang, "settings"),
        reply_markup=get_settings_keyboard(lang)
    )

# About Bot
# --- TAXMINAN 320-QATOR ---
@router.callback_query(F.data == "about_bot")
async def show_about(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Foydalanuvchi tilini bazadan olish, bo'lsa lang, bo'lmasa 'uz'
    lang = await user_db.get_language(user_id) or "uz"
    
    # Lug'atdan matnni qidirish
    about_text = TEXTS.get(lang, TEXTS['uz']).get('about_bot')
    
    # Agar lug'atda matn baribir topilmasa, qo'lda yozilgan matnni chiqarish
    if not about_text:
        about_text = (
            "ℹ️ <b>Bot haqida:</b>\n\n"
            "📌 Versiya: 2.0\n"
            "🔧 Texnologiya: Aiogram 3\n"
            "🎯 Maqsad: TOPIK so'zlarini yodlash\n\n"
            "🎮 O'yin rejimi - cheksiz mashq\n"
            "🤖 Avtomatik - har 15 minutda xabar"
        )

    await callback.message.edit_text(
        text=about_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(lang)
    )
    await callback.answer()


# Tilni o'zgartirish
@router.callback_query(F.data == "change_language")
async def change_lang_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    await callback.message.edit_text(
        get_text(lang, "change_language"),
        reply_markup=get_language_keyboard()
    )
    await callback.answer()

# Asosiy menyuga qaytish
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        get_text(lang, "main_menu"),
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()
    #4-qism


# Javob tekshirish

    # Bo'limlar: Topik tanlash
@router.callback_query(F.data.startswith("topic_"))
async def chapters_topic_selected(callback: CallbackQuery):
    topic = callback.data.replace("topic_", "")
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    await callback.message.edit_text(
        f"📂 {topic}\n\n" + get_text(lang, "chapters_select_section"),
        reply_markup=get_chapters_sections_keyboard(topic)
    )
    await callback.answer()

# Bo'limlar: Bo'lim tanlash
@router.callback_query(F.data.startswith("section_"))
async def chapters_section_selected(callback: CallbackQuery):
    parts = callback.data.replace("section_", "").split("_", 1)
    topic = parts[0]
    section = parts[1]
    
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    await callback.message.edit_text(
        f"📖 {topic} → {section.title()}\n\n" + get_text(lang, "chapters_select_chapter"),
        reply_markup=get_chapters_chapters_keyboard(topic, section)
    )
    await callback.answer()

# Bo'limlar: Bob tanlash va so'zlarni ko'rsatish
@router.callback_query(F.data.startswith("chapter_"))
async def chapters_chapter_selected(callback: CallbackQuery):
    parts = callback.data.replace("chapter_", "").split("_", 2)
    topic = parts[0]
    section = parts[1]
    chapter = parts[2]
    
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    # So'zlarni olish
    words = dict_handler.get_chapter_words(topic, section, chapter)
    
    if not words:
        await callback.answer(get_text(lang, "no_words"), show_alert=True)
        return
    
    # So'zlarni formatlash
    text = f"📚 <b>{chapter}</b>\n\n"
    for korean, uzbek in words.items():
        text += f"🇰🇷 {korean} — 🇺🇿 {uzbek}\n"
    
    text += f"\n📊 Jami: {len(words)} ta so'z"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"section_{topic}_{section}")]
        ])
    )
    await callback.answer()

# Bo'limlarga qaytish
@router.callback_query(F.data == "chapters_main")
async def chapters_back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    await callback.message.edit_text(
        get_text(lang, "chapters_select_topic"),
        reply_markup=get_chapters_topics_keyboard()
    )
    await callback.answer()

    #5-qism

    # Admin panel
@router.callback_query(F.data == "admin_panel")
async def admin_panel_entry(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    # Admin ekanligini tekshirish
    is_admin = await user_db.is_admin(user_id)
    
    if is_admin:
        await callback.message.edit_text(
            get_text(lang, "admin_welcome"),
            reply_markup=get_admin_keyboard(lang)
        )
        await callback.answer()
        return
    
    # Parol so'rash
    await callback.message.edit_text(
        get_text(lang, "admin_enter_password")
    )
    await state.set_state(AdminState.waiting_password)
    await callback.answer()

# Admin parol tekshirish
@router.message(AdminState.waiting_password)
async def check_admin_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id)
    
    if message.text == ADMIN_PASSWORD:
        # Admin qo'shish
        await user_db.add_admin(user_id)
        
        await message.answer(
            get_text(lang, "admin_welcome"),
            reply_markup=get_admin_keyboard(lang)
        )
        await state.clear()
    else:
        await message.answer(get_text(lang, "admin_wrong_password"))
        await state.clear()

# Admin: Userlar ro'yxati
@router.callback_query(F.data == "admin_users")
async def admin_show_users(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    users = await user_db.get_all_users()
    
    text = get_text(lang, "admin_user_list") + "\n\n"
    
    keyboard = []
    for idx, user in enumerate(users[:10], 1):  # Faqat birinchi 10 ta
        status = "🚫" if user['is_blocked'] else "✅"
        text += f"{idx}. {status} {user['first_name']} (@{user['username']}) - {user['correct']} ✅\n"
        
        block_text = get_text(lang, "admin_unblock") if user['is_blocked'] else get_text(lang, "admin_block")
        keyboard.append([
            InlineKeyboardButton(
                text=f"{user['first_name'][:15]} - {block_text}",
                callback_data=f"admin_toggle_{user['user_id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="admin_panel")
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

# Admin: Block/Unblock toggle
@router.callback_query(F.data.startswith("admin_toggle_"))
async def admin_toggle_block(callback: CallbackQuery, state: FSMContext):
    target_user_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    is_blocked, _ = await user_db.is_blocked(target_user_id)
    
    if is_blocked:
        # Unblock
        await user_db.unblock_user(target_user_id)
        await callback.answer(get_text(lang, "admin_user_unblocked"), show_alert=True)
    else:
        # Block - sabab so'rash
        await state.update_data(target_user_id=target_user_id)
        await callback.message.edit_text(
            get_text(lang, "admin_enter_block_reason")
        )
        await state.set_state(AdminState.waiting_block_reason)
        return
    
    # Ro'yxatni yangilash
    await admin_show_users(callback)

# Admin: Block sababi
@router.message(AdminState.waiting_block_reason)
async def admin_block_with_reason(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id)
    
    if message.text == "/cancel":
        await message.answer(get_text(lang, "main_menu"), reply_markup=get_main_keyboard(lang))
        await state.clear()
        return
    
    data = await state.get_data()
    target_user_id = data['target_user_id']
    
    reason = message.text if message.text else "No reason"
    
    await user_db.block_user(target_user_id, reason)
    
    await message.answer(get_text(lang, "admin_user_blocked"))
    await message.answer(
        get_text(lang, "admin_welcome"),
        reply_markup=get_admin_keyboard(lang)
    )
    
    await state.clear()

# Admin panelga qaytish
@router.callback_query(F.data == "admin_panel", StateFilter("*"))
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id)
    
    await state.clear()
    
    await callback.message.edit_text(
        get_text(lang, "admin_welcome"),
        reply_markup=get_admin_keyboard(lang)
    )
    await callback.answer()

# --- O'YIN TIZIMI (GAME) ---

@router.message(F.text == "/game")
async def start_game_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    all_words = dict_handler.get_all_words()
    if not all_words:
        await message.answer(get_text(lang, "no_words"))
        return
        
    word = random.choice(all_words)
    
    # 1. Global statistikada so'z so'ralganini hisobga olish
    if 'id' in word:
        await user_db.increment_word_count(word['id'])
    
    # 2. User uchun takrorlanish nazoratini belgilash
    await user_db.track_word(user_id, word.get('id', 0))
    
    await state.update_data(current_word=word, start_time=datetime.now().timestamp())
    
    await message.answer(
        get_text(lang, "game_question", uzbek=word['uzbek']),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )
    await state.set_state(GameState.playing)

@router.message(GameState.playing)
async def process_game_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    data = await state.get_data()
    word = data['current_word']
    
    # Foydalanuvchi javobini tozalash
    user_answer = message.text.strip().lower()
    correct_answer = word['korean'].strip().lower()
    
    time_spent = int(datetime.now().timestamp() - data['start_time'])
    
    # Javobni tekshirish va foydalanuvchi statistikasini yangilash
    if user_answer == correct_answer:
        await user_db.update_statistics(user_id, True, time_spent)
        await message.answer(get_text(lang, "game_correct", uzbek=word['uzbek'], korean=word['korean']))
    else:
        await user_db.update_statistics(user_id, False, time_spent)
        await message.answer(get_text(lang, "game_wrong", uzbek=word['uzbek'], korean=word['korean'], user_answer=message.text))

    # --- KEYINGI SAVOLGA O'TISH ---
    all_words = dict_handler.get_all_words()
    next_word = random.choice(all_words)
    
    # Keyingi so'z hisoblagichini oshirish
    if 'id' in next_word:
        await user_db.increment_word_count(next_word['id'])
    
    # User track
    await user_db.track_word(user_id, next_word.get('id', 0))
    
    await state.update_data(current_word=next_word, start_time=datetime.now().timestamp())
    await message.answer(
        get_text(lang, "game_question", uzbek=next_word['uzbek']),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )
@router.callback_query(F.data == "stop_game")
async def stop_game_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    await callback.message.edit_text("🛑 O'yin to'xtatildi.")
    await callback.message.answer(get_text(lang, "main_menu"), reply_markup=get_main_keyboard(lang))
@router.callback_query(F.data == "showWord_info")
async def show_word_usage_handler(callback: CallbackQuery):
    lang = await user_db.get_language(callback.from_user.id) or "uz"
    is_admin = await user_db.is_admin(callback.from_user.id)

    words = await user_db.get_words_sorted_by_usage()

    if not words:
        await callback.message.answer(
            "📊 <b>So'zlar statistikasi</b>\n\n"
            "⚠️ Hozircha ma'lumot yo‘q.\n"
            "O‘yinni boshlang.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = "📊 <b>So‘zlar statistikasi (kam → ko‘p)</b>\n"
    current_group = None

    for w in words:
        group = f"{w['category'] or 'Nomaʼlum'} > {w['sub_category'] or 'Umumiy'}"
        if group != current_group:
            text += f"\n📘 <b>{group}</b>\n"
            current_group = group

        text += f" • {w['korean']} — {w['asked_count']} marta\n"

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(lang, is_admin)
    )
    await callback.answer()



# --- 3. ASOSIY ISHGA TUSHIRISH (Main) ---
async def main():
    await user_db.init_db()
    dp.include_router(router)
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())