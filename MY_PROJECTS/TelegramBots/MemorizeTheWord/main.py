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

from config import BOT_TOKEN, ADMIN_PASSWORD, DICTIONARY_PATH, USER_DB_PATH
from utils.db_handler import DictionaryHandler
from database.db import UserDatabase

# Initialization
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

dict_handler = DictionaryHandler(DICTIONARY_PATH)
user_db = UserDatabase(USER_DB_PATH)

# Global so'zlar tracking
user_word_pool = {}  # {user_id: [word_ids]}

# FSM States
class GameState(StatesGroup):
    playing = State()

class AutoPlayState(StatesGroup):
    playing = State()

class AdminState(StatesGroup):
    waiting_password = State()
    waiting_block_reason = State()

# ==================== TRANSLATIONS ====================
TEXTS = {
    "uz": {
        "choose_language": "🌐 Tilni tanlang:",
        "language_changed": "✅ Til muvaffaqiyatli o'zgartirildi!",
        "start_message": """
🎓 <b>Memorize Bot'ga xush kelibsiz!</b>

Bu bot TOPIK so'zlarini smart tarzda yodlashga yordam beradi.

📊 <b>Bot ma'lumotlari:</b>
👥 Foydalanuvchilar: {users}
📚 Topiklar: {topics}
📖 Jami so'zlar: {words}

⏰ <b>Avtomatik xodlash:</b>
Har 15 daqiqada 10 ta so'z yuboriladi!

Quyidagi tugmalardan foydalaning! 👇
""",
        "blocked_message": "❌ Siz bloklangansiz.\n\n📝 Sabab: {reason}",
        "main_menu": "📋 Asosiy menyu:",
        "game_mode": "🎮 O'yin boshlash",
        "chapters": "📂 Bo'limlar",
        "settings": "⚙️ Sozlamalar",
        "statistics": "📊 Statistika",
        "admin_panel": "🔐 Admin Panel",
        "stop_game": "🛑 To'xtatish",
        "back": "◀️ Orqaga",
        "back_to_menu": "🏠 Asosiy menyu",
        "about_bot_btn": "ℹ️ Bot haqida",
        "change_language": "🌐 Tilni o'zgartirish",
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
📂 Bo'limlar - Topik bo'yicha taqsimlangan
📊 Statistika - O'z natijalaringizni kuzating
⏰ Avtomatik - Har 15 daqiqada 10 ta so'z
""",
        "admin_enter_password": "🔐 Admin panelga kirish uchun parolni kiriting:",
        "admin_wrong_password": "❌ Noto'g'ri parol!",
        "admin_welcome": "✅ Admin panelga xush kelibsiz!",
        "admin_users": "👥 Foydalanuvchilar",
        "admin_user_list": "📋 <b>Foydalanuvchilar ro'yxati:</b>",
        "admin_block": "🚫 Bloklash",
        "admin_unblock": "✅ Blokdan chiqarish",
        "admin_enter_block_reason": "📝 Bloklash sababini yozing:\n\n/skip - Sababsiz bloklash\n/cancel - Bekor qilish",
        "admin_user_blocked": "✅ Foydalanuvchi bloklandi!",
        "admin_user_unblocked": "✅ Foydalanuvchi blokdan chiqarildi!",
        "game_question": """
🎮 <b>Savol:</b>

📂 <b>Topik:</b> {topic}
📖 <b>Bo'lim:</b> {section}

🇺🇿 <b>{uzbek}</b>

📝 Koreys tilida yozing:
""",
        "auto_question": """
⏰ <b>So'z yodlash vaqti!</b>

Sen bu so'zni bilasanmi? 🤔

📂 <b>Topik:</b> {topic}
📖 <b>Bo'lim:</b> {section}

🇺🇿 <b>{uzbek}</b>

📝 Koreys tilida yozing:
""",
        "game_correct": "✅ <b>To'g'ri javob!</b>\n\n🇺🇿 {uzbek}\n🇰🇷 {korean}",
        "game_wrong": "❌ <b>Noto'g'ri!</b>\n\n🇺🇿 {uzbek}\n🇰🇷 {korean}\n\n📌 Siz yozgan: <code>{user_answer}</code>",
        "game_stopped": "🛑 O'yin to'xtatildi!\n\n✅ To'g'ri: {correct}\n❌ Noto'g'ri: {wrong}",
        "chapters_select_topic": "📂 Topikni tanlang:",
        "chapters_select_section": "📖 Bo'limni tanlang:",
        "chapters_select_chapter": "📑 Bobni tanlang:",
        "no_words": "❌ So'zlar topilmadi!",
        "settings_menu": "⚙️ <b>Sozlamalar:</b>",
        "bot_status": "🤖 <b>Bot holati:</b>\n\n✅ Faol",
        "word_stats_title": "📊 <b>So'zlar statistikasi (kam → ko'p)</b>\n",
        "word_stats_empty": "📊 <b>So'zlar statistikasi</b>\n\n⚠️ Hozircha ma'lumot yo'q.\nO'yinni boshlang.",
        "auto_game_finished": "🎉 <b>Avtomatik o'yin tugadi!</b>\n\n✅ To'g'ri: {correct}\n❌ Noto'g'ri: {wrong}\n\n15 daqiqadan keyin yana so'zlar yuboriladi! ⏰",
    },
    "kr": {
        "choose_language": "🌐 언어 선택:",
        "language_changed": "✅ 언어가 성공적으로 변경되었습니다!",
        "start_message": """
🎓 <b>Memorize Bot에 오신 것을 환영합니다!</b>

이 봇은 TOPIK 단어를 스마트하게 암기하는 데 도움을 줍니다.

📊 <b>봇 정보:</b>
👥 사용자: {users}
📚 토픽: {topics}
📖 총 단어: {words}

⏰ <b>자동 학습:</b>
15분마다 10개 단어가 전송됩니다!

아래 버튼을 사용하세요! 👇
""",
        "blocked_message": "❌ 차단되었습니다.\n\n📝 이유: {reason}",
        "main_menu": "📋 메인 메뉴:",
        "game_mode": "🎮 게임 시작",
        "chapters": "📂 섹션",
        "settings": "⚙️ 설정",
        "statistics": "📊 통계",
        "admin_panel": "🔐 관리자 패널",
        "stop_game": "🛑 중지",
        "back": "◀️ 뒤로",
        "back_to_menu": "🏠 메인 메뉴",
        "about_bot_btn": "ℹ️ 봇 정보",
        "change_language": "🌐 언어 변경",
        "my_stats": """
📊 <b>내 통계:</b>

✅ 정답: {correct}
❌ 오답: {wrong}
⏱ 활동 시간: {time}분
🏆 순위: {rank}/{total}
""",
        "bot_statistics": """
📈 <b>봇 통계:</b>

👥 총 사용자: {users}
📚 데이터베이스 단어: {words}
""",
        "about_bot": """
ℹ️ <b>봇 정보:</b>

📌 버전: 2.0
🔧 기술: Aiogram 3
💾 데이터베이스: SQLite
🎯 목적: TOPIK 단어 암기

🎮 게임 모드 - 무한 연습
📂 섹션 - 토픽별 분류
📊 통계 - 결과 추적
⏰ 자동 - 15분마다 10개 단어
""",
        "admin_enter_password": "🔐 관리자 패널에 접근하려면 비밀번호를 입력하세요:",
        "admin_wrong_password": "❌ 잘못된 비밀번호!",
        "admin_welcome": "✅ 관리자 패널에 오신 것을 환영합니다!",
        "admin_users": "👥 사용자",
        "admin_user_list": "📋 <b>사용자 목록:</b>",
        "admin_block": "🚫 차단",
        "admin_unblock": "✅ 차단 해제",
        "admin_enter_block_reason": "📝 차단 이유를 입력하세요:\n\n/skip - 이유 없이 차단\n/cancel - 취소",
        "admin_user_blocked": "✅ 사용자가 차단되었습니다!",
        "admin_user_unblocked": "✅ 사용자 차단이 해제되었습니다!",
        "game_question": """
🎮 <b>질문:</b>

📂 <b>토픽:</b> {topic}
📖 <b>섹션:</b> {section}

🇺🇿 <b>{uzbek}</b>

📝 한국어로 작성하세요:
""",
        "auto_question": """
⏰ <b>단어 학습 시간!</b>

이 단어를 알고 있나요? 🤔

📂 <b>토픽:</b> {topic}
📖 <b>섹션:</b> {section}

🇺🇿 <b>{uzbek}</b>

📝 한국어로 작성하세요:
""",
        "game_correct": "✅ <b>정답입니다!</b>\n\n🇺🇿 {uzbek}\n🇰🇷 {korean}",
        "game_wrong": "❌ <b>오답입니다!</b>\n\n🇺🇿 {uzbek}\n🇰🇷 {korean}\n\n📌 입력: <code>{user_answer}</code>",
        "game_stopped": "🛑 게임 중지!\n\n✅ 정답: {correct}\n❌ 오답: {wrong}",
        "chapters_select_topic": "📂 토픽 선택:",
        "chapters_select_section": "📖 섹션 선택:",
        "chapters_select_chapter": "📑 챕터 선택:",
        "no_words": "❌ 단어를 찾을 수 없습니다!",
        "settings_menu": "⚙️ <b>설정:</b>",
        "bot_status": "🤖 <b>봇 상태:</b>\n\n✅ 활성",
        "word_stats_title": "📊 <b>단어 통계 (적음 → 많음)</b>\n",
        "word_stats_empty": "📊 <b>단어 통계</b>\n\n⚠️ 아직 데이터가 없습니다.\n게임을 시작하세요.",
        "auto_game_finished": "🎉 <b>자동 게임 완료!</b>\n\n✅ 정답: {correct}\n❌ 오답: {wrong}\n\n15분 후 다시 단어가 전송됩니다! ⏰",
    }
}

def get_text(lang: str, key: str, **kwargs) -> str:
    """Til bo'yicha matn olish"""
    text = TEXTS.get(lang, TEXTS['uz']).get(key, key)
    return text.format(**kwargs) if kwargs else text

# ==================== WORD POOL MANAGER ====================

def get_next_word(user_id: int):
    """Takrorlanmaslik uchun so'z olish"""
    all_words = dict_handler.get_all_words()
    
    if not all_words:
        return None
    
    # Agar user uchun pool bo'lmasa yoki tugasa, yangi pool yaratish
    if user_id not in user_word_pool or len(user_word_pool[user_id]) == 0:
        user_word_pool[user_id] = [w['id'] for w in all_words if 'id' in w]
        random.shuffle(user_word_pool[user_id])
    
    # Pool'dan birinchi so'zni olish
    word_id = user_word_pool[user_id].pop(0)
    
    # So'zni topish
    word = next((w for w in all_words if w.get('id') == word_id), None)
    
    return word if word else random.choice(all_words)

# ==================== KEYBOARDS ====================

def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="/game"), KeyboardButton(text="/bo'limlar")],
        [KeyboardButton(text="/sozlamalar")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Inline asosiy menyu"""
    keyboard = [
        [InlineKeyboardButton(text=get_text(lang, "game_mode"), callback_data="start_game")],
        [InlineKeyboardButton(text=get_text(lang, "chapters"), callback_data="chapters_main")],
        [InlineKeyboardButton(text=get_text(lang, "statistics"), callback_data="show_stats")],
        [InlineKeyboardButton(text=get_text(lang, "settings"), callback_data="settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_game_keyboard(lang: str) -> InlineKeyboardMarkup:
    """O'yin klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text=get_text(lang, "stop_game"), callback_data="stop_game")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_topics_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Topiklar ro'yxati"""
    topics = dict_handler.get_all_topics()
    keyboard = []
    
    for topic in topics:
        keyboard.append([
            InlineKeyboardButton(text=topic, callback_data=f"topic_{topic}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_sections_keyboard(topic: str, lang: str) -> InlineKeyboardMarkup:
    """Bo'limlar (reading, writing, listening)"""
    sections = dict_handler.get_topic_sections(topic)
    keyboard = []
    
    for section in sections:
        keyboard.append([
            InlineKeyboardButton(text=section.title(), callback_data=f"section_{topic}_{section}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text=get_text(lang, "back"), callback_data="chapters_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_chapters_keyboard(topic: str, section: str, lang: str) -> InlineKeyboardMarkup:
    """Boblar (9-savol, 13-savol...)"""
    chapters = dict_handler.get_section_chapters(topic, section)
    keyboard = []
    
    for chapter in chapters:
        keyboard.append([
            InlineKeyboardButton(text=chapter, callback_data=f"chapter_{topic}_{section}_{chapter}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text=get_text(lang, "back"), callback_data=f"topic_{topic}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇰🇷 한국어", callback_data="lang_kr")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_settings_keyboard(lang: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Sozlamalar menyusi"""
    buttons = []
    
    # Faqat admin bo'lsa
    if is_admin:
        buttons.append([InlineKeyboardButton(text=get_text(lang, "admin_panel"), callback_data="admin_panel")])
    
    buttons.extend([
        [InlineKeyboardButton(text=get_text(lang, "change_language"), callback_data="change_language")],
        [InlineKeyboardButton(text=get_text(lang, "about_bot_btn"), callback_data="about_bot")],
        [InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Admin panel klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text=get_text(lang, "admin_users"), callback_data="admin_users")],
        [InlineKeyboardButton(text=get_text(lang, "statistics"), callback_data="admin_stats")],
        [InlineKeyboardButton(text=get_text(lang, "back_to_menu"), callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_user_action_keyboard(user_id: int, is_blocked: bool, lang: str) -> InlineKeyboardMarkup:
    """User uchun block/unblock tugmasi"""
    if is_blocked:
        button_text = get_text(lang, "admin_unblock")
        callback_data = f"unblock_{user_id}"
    else:
        button_text = get_text(lang, "admin_block")
        callback_data = f"block_{user_id}"
    
    keyboard = [
        [InlineKeyboardButton(text=button_text, callback_data=callback_data)],
        [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin_users")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ==================== MIDDLEWARE ====================

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
            lang = await user_db.get_language(user_id) or "uz"
            reason_text = reason or "Sabab ko'rsatilmagan"
            await event.answer(get_text(lang, "blocked_message", reason=reason_text))
            return
        
        return await handler(event, data)

router.message.middleware(BlockCheckMiddleware())

# ==================== HANDLERS ====================

# /start command
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Foydalanuvchini ro'yxatdan o'tkazish
    await user_db.add_user(
        user_id=user_id,
        username=message.from_user.username or "unknown",
        first_name=message.from_user.first_name or "User"
    )
    
    lang = await user_db.get_language(user_id) or "uz"
    
    # Statistika
    total_users = await user_db.get_total_users()
    total_topics = len(dict_handler.get_all_topics())
    total_words = dict_handler.get_total_words()
    
    await message.answer(
        get_text(lang, "start_message", users=total_users, topics=total_topics, words=total_words),
        parse_mode="HTML",
        reply_markup=get_main_keyboard(lang)
    )
    
    await message.answer(
        get_text(lang, "main_menu"),
        reply_markup=get_main_menu_keyboard(lang)
    )

# /sozlamalar command
@router.message(Command("sozlamalar"))
async def cmd_settings(message: Message):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    is_admin = await user_db.is_admin(user_id)
    
    await message.answer(
        get_text(lang, "settings_menu"),
        reply_markup=get_settings_keyboard(lang, is_admin),
        parse_mode="HTML"
    )

# /bo'limlar command
@router.message(Command("bo'limlar"))
async def cmd_chapters(message: Message):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await message.answer(
        get_text(lang, "chapters_select_topic"),
        reply_markup=get_chapters_topics_keyboard(lang)
    )

# Til tanlash callback
@router.callback_query(F.data.startswith("lang_"))
async def set_language_callback(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    await user_db.set_language(user_id, lang)
    
    await callback.message.edit_text(
        get_text(lang, "language_changed"),
        reply_markup=get_main_menu_keyboard(lang)
    )
    
    # Pastki tugmalarni yangilash
    await callback.message.answer(
        get_text(lang, "main_menu"),
        reply_markup=get_main_keyboard(lang)
    )
    await callback.answer()

# Statistika callback
@router.callback_query(F.data == "show_stats")
async def show_my_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
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

# Sozlamalar callback
@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    is_admin = await user_db.is_admin(user_id)
    
    await callback.message.edit_text(
        get_text(lang, "settings_menu"),
        reply_markup=get_settings_keyboard(lang, is_admin),
        parse_mode="HTML"
    )
    await callback.answer()

# About Bot
@router.callback_query(F.data == "about_bot")
async def show_about(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    is_admin = await user_db.is_admin(user_id)
    
    await callback.message.edit_text(
        get_text(lang, "about_bot"),
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(lang, is_admin)
    )
    await callback.answer()

# Tilni o'zgartirish
@router.callback_query(F.data == "change_language")
async def change_lang_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        get_text(lang, "choose_language"),
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

# ==================== BO'LIMLAR ====================

@router.callback_query(F.data == "chapters_main")
async def chapters_main_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        get_text(lang, "chapters_select_topic"),
        reply_markup=get_chapters_topics_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("topic_"))
async def chapters_topic_selected(callback: CallbackQuery):
    topic = callback.data.replace("topic_", "")
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        f"📂 {topic}\n\n" + get_text(lang, "chapters_select_section"),
        reply_markup=get_chapters_sections_keyboard(topic, lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("section_"))
async def chapters_section_selected(callback: CallbackQuery):
    parts = callback.data.replace("section_", "").split("_", 1)
    topic = parts[0]
    section = parts[1]
    
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        f"📖 {topic} → {section.title()}\n\n" + get_text(lang, "chapters_select_chapter"),
        reply_markup=get_chapters_chapters_keyboard(topic, section, lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("chapter_"))
async def chapters_chapter_selected(callback: CallbackQuery):
    parts = callback.data.replace("chapter_", "").split("_", 2)
    topic = parts[0]
    section = parts[1]
    chapter = parts[2]
    
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    words = dict_handler.get_chapter_words(topic, section, chapter)
    
    if not words:
        await callback.answer(get_text(lang, "no_words"), show_alert=True)
        return
    
    text = f"📚 <b>{chapter}</b>\n\n"
    for korean, uzbek in words.items():
        text += f"🇰🇷 {korean} — 🇺🇿 {uzbek}\n"
    
    text += f"\n📊 {get_text(lang, 'statistics')}: {len(words)}"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "back"), callback_data=f"section_{topic}_{section}")]
        ])
    )
    await callback.answer()

# ==================== ADMIN PANEL ====================

@router.callback_query(F.data == "admin_panel")
async def admin_panel_entry(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    is_admin = await user_db.is_admin(user_id)
    
    if is_admin:
        await callback.message.edit_text(
            get_text(lang, "admin_welcome"),
            reply_markup=get_admin_keyboard(lang)
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        get_text(lang, "admin_enter_password")
    )
    await state.set_state(AdminState.waiting_password)
    await callback.answer()

@router.message(AdminState.waiting_password)
async def check_admin_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    if message.text == ADMIN_PASSWORD:
        await user_db.add_admin(user_id)
        
        await message.answer(
            get_text(lang, "admin_welcome"),
            reply_markup=get_admin_keyboard(lang)
        )
        await state.clear()
    else:
        await message.answer(get_text(lang, "admin_wrong_password"))
        await state.clear()

@router.callback_query(F.data == "admin_users")
async def admin_show_users(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    users = await user_db.get_all_users()
    
    text = get_text(lang, "admin_user_list") + "\n\n"
    
    keyboard = []
    for idx, user in enumerate(users[:15], 1):
        status = "🚫" if user['is_blocked'] else "✅"
        rank, total = await user_db.get_ranking(user['user_id'])
        
        text += (
            f"{idx}. {status} <b>{user['first_name']}</b> (@{user['username']})\n"
            f"   📊 ✅ {user['correct']} | ❌ {user['wrong']} | 🏆 {rank}/{total}\n\n"
        )
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{user['first_name'][:20]}",
                callback_data=f"user_detail_{user['user_id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin_panel")
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("user_detail_"))
async def admin_user_detail(callback: CallbackQuery):
    target_user_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    users = await user_db.get_all_users()
    user = next((u for u in users if u['user_id'] == target_user_id), None)
    
    if not user:
        await callback.answer("❌ User topilmadi!", show_alert=True)
        return
    
    is_blocked, reason = await user_db.is_blocked(target_user_id)
    rank, total = await user_db.get_ranking(target_user_id)
    
    status = "🚫 Bloklangan" if is_blocked else "✅ Faol"
    block_reason = f"\n📝 Sabab: {reason}" if is_blocked and reason else ""
    
    text = (
        f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
        f"📛 Ism: {user['first_name']}\n"
        f"🆔 Username: @{user['username']}\n"
        f"🔢 ID: <code>{user['user_id']}</code>\n"
        f"🎯 Status: {status}{block_reason}\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"✅ To'g'ri: {user['correct']}\n"
        f"❌ Noto'g'ri: {user['wrong']}\n"
        f"⏱ Faol vaqt: {user['active_time'] // 60} daqiqa\n"
        f"🏆 Reyting: {rank}/{total}\n"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_user_action_keyboard(target_user_id, is_blocked, lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("block_"))
async def admin_block_user(callback: CallbackQuery, state: FSMContext):
    target_user_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await state.update_data(target_user_id=target_user_id)
    await callback.message.edit_text(
        get_text(lang, "admin_enter_block_reason")
    )
    await state.set_state(AdminState.waiting_block_reason)
    await callback.answer()

@router.callback_query(F.data.startswith("unblock_"))
async def admin_unblock_user(callback: CallbackQuery):
    target_user_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await user_db.unblock_user(target_user_id)
    await callback.answer(get_text(lang, "admin_user_unblocked"), show_alert=True)
    
    # Detail sahifaga qaytish
    await admin_user_detail(callback)

@router.message(AdminState.waiting_block_reason)
async def admin_block_with_reason(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    if message.text == "/cancel":
        await message.answer(get_text(lang, "main_menu"), reply_markup=get_main_keyboard(lang))
        await state.clear()
        return
    
    data = await state.get_data()
    target_user_id = data['target_user_id']
    
    if message.text == "/skip":
        reason = None
    else:
        reason = message.text
    
    await user_db.block_user(target_user_id, reason)
    
    await message.answer(get_text(lang, "admin_user_blocked"))
    await message.answer(
        get_text(lang, "admin_welcome"),
        reply_markup=get_admin_keyboard(lang)
    )
    
    await state.clear()

@router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    total_users = await user_db.get_total_users()
    total_words = dict_handler.get_total_words()
    
    await callback.message.edit_text(
        get_text(lang, "bot_statistics", users=total_users, words=total_words),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin_panel")]
        ])
    )
    await callback.answer()

# ==================== O'YIN TIZIMI ====================

@router.message(Command("game"))
async def start_game_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    word = get_next_word(user_id)
    if not word:
        await message.answer(get_text(lang, "no_words"))
        return
    
    if 'id' in word:
        await user_db.increment_word_count(word['id'])
    
    await user_db.track_word(user_id, word.get('id', 0))
    
    await state.update_data(current_word=word, start_time=datetime.now().timestamp())
    
    topic = word.get('category', 'Unknown')
    section = word.get('sub_category', 'Unknown')
    
    await message.answer(
        get_text(lang, "game_question", uzbek=word['uzbek'], topic=topic, section=section),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )
    await state.set_state(GameState.playing)

@router.callback_query(F.data == "start_game")
async def start_game_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    word = get_next_word(user_id)
    if not word:
        await callback.answer(get_text(lang, "no_words"), show_alert=True)
        return
    
    if 'id' in word:
        await user_db.increment_word_count(word['id'])
    
    await user_db.track_word(user_id, word.get('id', 0))
    
    await state.update_data(current_word=word, start_time=datetime.now().timestamp())
    
    topic = word.get('category', 'Unknown')
    section = word.get('sub_category', 'Unknown')
    
    await callback.message.edit_text(
        get_text(lang, "game_question", uzbek=word['uzbek'], topic=topic, section=section),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )
    await state.set_state(GameState.playing)
    await callback.answer()

@router.message(GameState.playing)
async def process_game_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    data = await state.get_data()
    word = data['current_word']
    
    user_answer = message.text.strip().lower()
    correct_answer = word['korean'].strip().lower()
    
    time_spent = int(datetime.now().timestamp() - data['start_time'])
    
    if user_answer == correct_answer:
        await user_db.update_statistics(user_id, True, time_spent)
        await message.answer(
            get_text(lang, "game_correct", uzbek=word['uzbek'], korean=word['korean']),
            parse_mode="HTML"
        )
    else:
        await user_db.update_statistics(user_id, False, time_spent)
        await message.answer(
            get_text(lang, "game_wrong", uzbek=word['uzbek'], korean=word['korean'], user_answer=message.text),
            parse_mode="HTML"
        )
    
    # Keyingi savol
    next_word = get_next_word(user_id)
    
    if 'id' in next_word:
        await user_db.increment_word_count(next_word['id'])
    
    await user_db.track_word(user_id, next_word.get('id', 0))
    
    topic = next_word.get('category', 'Unknown')
    section = next_word.get('sub_category', 'Unknown')
    
    await state.update_data(current_word=next_word, start_time=datetime.now().timestamp())
    await message.answer(
        get_text(lang, "game_question", uzbek=next_word['uzbek'], topic=topic, section=section),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "stop_game")
async def stop_game_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    stats = await user_db.get_statistics(user_id)
    
    await state.clear()
    
    await callback.message.edit_text(
        get_text(lang, "game_stopped", correct=stats['correct'], wrong=stats['wrong']),
        parse_mode="HTML"
    )
    
    await callback.message.answer(
        get_text(lang, "main_menu"),
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()

# ==================== AVTOMATIK O'YIN (Har 15 daqiqada) ====================

@router.message(AutoPlayState.playing)
async def process_auto_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    data = await state.get_data()
    word = data['current_word']
    question_count = data.get('question_count', 0)
    
    user_answer = message.text.strip().lower()
    correct_answer = word['korean'].strip().lower()
    
    time_spent = int(datetime.now().timestamp() - data['start_time'])
    
    if user_answer == correct_answer:
        await user_db.update_statistics(user_id, True, time_spent)
        await message.answer(
            get_text(lang, "game_correct", uzbek=word['uzbek'], korean=word['korean']),
            parse_mode="HTML"
        )
    else:
        await user_db.update_statistics(user_id, False, time_spent)
        await message.answer(
            get_text(lang, "game_wrong", uzbek=word['uzbek'], korean=word['korean'], user_answer=message.text),
            parse_mode="HTML"
        )
    
    question_count += 1
    
    # Agar 10 ta savol tugasa
    if question_count >= 10:
        stats = await user_db.get_statistics(user_id)
        await state.clear()
        await message.answer(
            get_text(lang, "auto_game_finished", correct=stats['correct'], wrong=stats['wrong']),
            parse_mode="HTML"
        )
        return
    
    # Keyingi savol
    next_word = get_next_word(user_id)
    
    if 'id' in next_word:
        await user_db.increment_word_count(next_word['id'])
    
    await user_db.track_word(user_id, next_word.get('id', 0))
    
    topic = next_word.get('category', 'Unknown')
    section = next_word.get('sub_category', 'Unknown')
    
    await state.update_data(current_word=next_word, start_time=datetime.now().timestamp(), question_count=question_count)
    await message.answer(
        get_text(lang, "auto_question", uzbek=next_word['uzbek'], topic=topic, section=section),
        parse_mode="HTML"
    )

async def send_auto_words():
    """Har 15 daqiqada barcha userlarga 10 ta so'z yuborish"""
    while True:
        await asyncio.sleep(900)  # 15 daqiqa = 900 sekund
        
        try:
            users = await user_db.get_all_users()
            
            for user in users:
                user_id = user['user_id']
                is_blocked, _ = await user_db.is_blocked(user_id)
                
                if is_blocked:
                    continue
                
                lang = await user_db.get_language(user_id) or "uz"
                
                # Birinchi so'zni yuborish
                word = get_next_word(user_id)
                if not word:
                    continue
                
                if 'id' in word:
                    await user_db.increment_word_count(word['id'])
                
                await user_db.track_word(user_id, word.get('id', 0))
                
                topic = word.get('category', 'Unknown')
                section = word.get('sub_category', 'Unknown')
                
                # FSM holatini o'rnatish (har bir user uchun alohida)
                state = FSMContext(storage=storage, key=f"{user_id}")
                await state.set_state(AutoPlayState.playing)
                await state.update_data(current_word=word, start_time=datetime.now().timestamp(), question_count=0)
                
                try:
                    await bot.send_message(
                        user_id,
                        get_text(lang, "auto_question", uzbek=word['uzbek'], topic=topic, section=section),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"❌ User {user_id} ga xabar yuborishda xato: {e}")
        
        except Exception as e:
            print(f"❌ Avtomatik so'z yuborishda xato: {e}")

# ==================== MAIN ====================

async def main():
    await user_db.init_db()
    dp.include_router(router)
    
    # Avtomatik so'z yuborish taskini ishga tushirish
    asyncio.create_task(send_auto_words())
    
    print("✅ Bot ishga tushdi!")
    print("⏰ Avtomatik so'z yuborish faollashtirildi (har 15 daqiqada)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())