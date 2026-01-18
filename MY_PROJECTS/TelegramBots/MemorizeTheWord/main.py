import asyncio
import random
from datetime import datetime
from aiogram.fsm.storage.base import StorageKey
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
from database.db import UserDatabase



from config import BOT_TOKEN,DICTIONARY_BASE_PATH, USER_DB_PATH
from utils.db_handler import DictionaryHandler


def get_text(lang: str, key: str, **kwargs) -> str:
    """Game matnini olish"""
    text = GAME_TEXTS.get(lang, GAME_TEXTS['uz']).get(key, key)
    try:
        return text.format(**kwargs)
    except:
        return text


class GameModeState(StatesGroup):
    selecting_mode = State()
    selecting_topic = State()
    selecting_section = State()
    playing = State()

class AutoPlayState(StatesGroup):
    selecting_time = State()  # Bu qator aniq mavjudligini tekshiring
    selecting_mode = State()
    selecting_topic = State()
    selecting_section = State()
    playing = State()

# ============================================
# 4. BOT VA ROUTER (FSM dan keyin)
# ============================================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


# DEBUG: Yo'lni tekshirish
import os
print(f"\n{'='*50}")
print(f"📂 Hozirgi papka: {os.getcwd()}")
print(f"📂 Dictionary path: {DICTIONARY_BASE_PATH}")
print(f"📂 Mavjudmi: {os.path.exists(DICTIONARY_BASE_PATH)}")

if os.path.exists(DICTIONARY_BASE_PATH):
    files = os.listdir(DICTIONARY_BASE_PATH)
    print(f"📄 Fayllar: {files}")
print(f"{'='*50}\n")

# Dictionary handler
dict_handler = DictionaryHandler(DICTIONARY_BASE_PATH)

# Initialization
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

dict_handler = DictionaryHandler(DICTIONARY_BASE_PATH)
user_db = UserDatabase(USER_DB_PATH)

# Global so'zlar tracking
user_word_pool = {}  # {user_id: [word_ids]}


class AdminState(StatesGroup):
    waiting_password = State()
    waiting_block_reason = State()
ALL_TEXTS = {
    "uz": {
        # ASOSIY MENYU VA UMUMIY
        "choose_language": "🌐 Tilni tanlang:",
        "language_changed": "✅ Til muvaffaqiyatli o'zgartirildi!",
        "main_menu": "📋 Asosiy menyu:",
        "game_mode": "🎮 O'yin boshlash",
        "chapters": "📂 Bo'limlar",
        "settings": "⚙️ Sozlamalar",
        "statistics": "📊 Statistika",
        "admin_panel": "🔐 Admin Panel",
        "back": "◀️ Orqaga",
        "back_to_menu": "🏠 Asosiy menyu",
        "about_bot_btn": "ℹ️ Bot haqida",
        "change_language": "🌐 Tilni o'zgartirish",
        "stop_game": "🛑 To'xtatish",

        # START VA STATISTIKA
        "start_message": "🎓 <b>Memorize Bot'ga xush kelibsiz!</b>\n\nBu bot TOPIK so'zlarini smart tarzda yodlashga yordam beradi.\n\n📊 <b>Bot ma'lumotlari:</b>\n👥 Foydalanuvchilar: {users}\n📚 Topiklar: {topics}\n📖 Jami so'zlar: {words}\n\nQuyidagi tugmalardan foydalaning! 👇",
        "my_stats": "📊 <b>Sizning statistikangiz:</b>\n\n✅ To'g'ri javoblar: {correct}\n❌ Noto'g'ri javoblar: {wrong}\n⏱ Faol vaqt: {time} daqiqa\n🏆 Reyting: {rank}/{total}",
        "bot_statistics": "📈 <b>Bot Statistikasi:</b>\n\n👥 Jami foydalanuvchilar: {users}\n📚 Bazadagi so'zlar: {words}",
        "about_bot": "ℹ️ <b>Bot haqida:</b>\n\n📌 Versiya: 2.0\n🔧 Texnologiya: Aiogram 3\n🎯 Maqsad: TOPIK so'zlarini yodlash\n\n🎮 O'yin rejimi - cheksiz mashq\n📂 Bo'limlar - Topik bo'yicha taqsimlangan\n📊 Statistika - Natijalarni kuzatish\n⏰ Avtomatik - Rejali yodlash",

        # O'YIN REJIMLARI
        "game_select_mode": "🎮 <b>O'yin rejimini tanlang:</b>",
        "btn_general_mode": "🌍 Umumiy rejim",
        "btn_custom_mode": "🎯 Belgilangan rejim",
        "game_select_topic": "📚 <b>Topikni tanlang:</b>",
        "game_select_section": "📖 <b>Bo'limni tanlang:</b>\n<i>{topic}</i>",
        "game_select_section_only": "📖 <b>{topic}</b>\n\nBo'limni tanlang:",
        "game_starting_custom": "🎮 <b>O'yin boshlandi!</b>\n\n📂 Topik: {topic}\n📖 Bo'lim: {section}\n\nYuborilayotgan so'zlar shu bo'limdan!",

        # SAVOLLAR
        "game_question": "🎮 <b>Savol #{count}:</b>\n>>> <i>{uzbek}</i>\n\n📍 {topic} › {section} › {chapter}\n📝 Koreys tilida yozing:",
        "auto_question_first": "🎮 <b>Savol:</b>\n>>> <i>{uzbek}</i>\n\n📍 {topic} › {section} › {chapter}\n📝 Koreys tilida yozing:",
        "auto_question": "🤖 <b>(AVTOMATIK SAVOL)</b> {count}/10\n\n⏰ So'z yodlash vaqti!\n\nSen bu so'zni bilasanmi? 🤔\n\n>>> <b>{uzbek}</b>\n\n📍 {topic} › {section} › {chapter}\n📝 Koreys tilida yozing:",

        # JAVOBLAR (FEEDBACK)
        "feedback_correct": "✅ <b>To'g'ri!</b> 🇰🇷 <code>{korean}</code>",
        "feedback_wrong": "❌ <b>Noto'g'ri!</b>\n🇰🇷 To'g'ri: <code>{korean}</code>\n📌 Siz: <s>{user_answer}</s>",
        "game_correct_short": "✅ <b>To'g'ri!</b> 🇰🇷 <code>{korean}</code>",
        "game_wrong_short": "❌ <b>Noto'g'ri!</b> 🇰🇷 <code>{korean}</code>\n📌 Siz: <s>{user_answer}</s>",

        # O'YIN TUGASHI VA TO'XTATISH
        "game_finished": "🎊 <b>O'yin tugadi!</b>\n\n✅ To'g'ri: <b>{correct}</b>\n❌ Noto'g'ri: <b>{wrong}</b>",
        "auto_game_finished": "🎉 <b>Avtomatik o'yin tugadi!</b>\n\n✅ To'g'ri: {correct}\n❌ Noto'g'ri: {wrong}\n\nKeyingi vaqtda yana so'zlar yuboriladi! ⏰",
        "game_stopped": "🛑 <b>O'yin to'xtatildi!</b>\n\n✅ To'g'ri: {correct}\n❌ Noto'g'ri: {wrong}",
        "btn_stop_game": "🛑 To'xtatish",

        # AVTO REJIM SOZLAMALARI
        "auto_select_time": "⏰ <b>Avtomatik rejim sozalamalari:</b>\n\nNecha daqiqada so'zlar kelsin?",
        "auto_time_set": "✅ Har {time} daqiqada 10 ta so'z yuboriladi!",
        "btn_5min": "⏱ 5 daqiqa", "btn_10min": "⏱ 10 daqiqa", "btn_15min": "⏱ 15 daqiqa", "btn_30min": "⏱ 30 daqiqa", "btn_60min": "⏱ 60 daqiqa",

        # ADMIN VA XATOLAR
        "no_words": "❌ So'zlar topilmadi!",
        "no_topics": "❌ Topiklar yo'q!",
        "no_sections": "❌ Bo'limlar yo'q!",
        "admin_welcome": "✅ Admin panelga xush kelibsiz!",
        "admin_enter_password": "🔐 Admin panelga kirish uchun parolni kiriting:",
        "admin_wrong_password": "❌ Noto'g'ri parol!",
        "admin_user_blocked": "✅ Foydalanuvchi bloklandi!",
        "admin_user_unblocked": "✅ Foydalanuvchi blokdan chiqarildi!"
    },
    "ko": {
        # ASOSIY MENYU VA UMUMIY
        "choose_language": "🌐 언어 선택:",
        "language_changed": "✅ 언어가 성공적으로 변경되었습니다!",
        "main_menu": "📋 메인 메뉴:",
        "game_mode": "🎮 게임 시작",
        "chapters": "📂 섹션",
        "settings": "⚙️ 설정",
        "statistics": "📊 통계",
        "admin_panel": "🔐 관리자 패널",
        "back": "◀️ 뒤로",
        "back_to_menu": "🏠 메인 메뉴",
        "about_bot_btn": "ℹ️ 봇 정보",
        "change_language": "🌐 언어 변경",
        "stop_game": "🛑 중지",

        # START VA STATISTIKA
        "start_message": "🎓 <b>Memorize Bot에 오신 것을 환영합니다!</b>\n\n이 봇은 TOPIK 단어를 스마트하게 암기하는 데 도움을 줍니다.\n\n📊 <b>봇 정보:</b>\n👥 사용자: {users}\n📚 토픽: {topics}\n📖 총 단어: {words}\n\n아래 버튼을 사용하세요! 👇",
        "my_stats": "📊 <b>내 통계:</b>\n\n✅ 정답: {correct}\n❌ 오답: {wrong}\n⏱ 활동 시간: {time}분\n🏆 순위: {rank}/{total}",
        "bot_statistics": "📈 <b>봇 통계:</b>\n\n👥 총 사용자: {users}\n📚 데이터베이스 단어: {words}",
        "about_bot": "ℹ️ <b>봇 정보:</b>\n\n📌 버전: 2.0\n🔧 기술: Aiogram 3\n🎯 목적: TOPIK 단어 암기\n\n🎮 게임 모드 - 무한 연습\n📂 섹션 - 토픽별 분류\n📊 통계 - 결과 추적\n⏰ 자동 - 정기 학습",

        # O'YIN REJIMLARI
        "game_select_mode": "🎮 <b>게임 모드 선택:</b>",
        "btn_general_mode": "🌍 일반 모드",
        "btn_custom_mode": "🎯 맞춤 모드",
        "game_select_topic": "📚 <b>주제 선택:</b>",
        "game_select_section": "📖 <b>섹션 선택:</b>\n<i>{topic}</i>",
        "game_select_section_only": "📖 <b>{topic}</b>\n\n섹션 선택:",
        "game_starting_custom": "🎮 <b>게임 시작!</b>\n\n📂 토픽: {topic}\n📖 섹션: {section}\n\n이 섹션에서 단어가 전송됩니다!",

        # SAVOLLAR
        "game_question": "🎮 <b>질문 #{count}:</b>\n>>> <i>{uzbek}</i>\n\n📍 {topic} › {section} › {chapter}\n📝 한국어로 작성하세요:",
        "auto_question_first": "🎮 <b>질문:</b>\n>>> <i>{uzbek}</i>\n\n📍 {topic} › {section} › {chapter}\n📝 한국어로 작성하세요:",
        "auto_question": "🤖 <b>(자동질문 모드)</b> {count}/10\n\n⏰ <b>단어 학습 시간!</b>\n📊 <b>질문: {count}/10</b>\n\n<i>이 단어를 알고 있나요?</i> 🤔\n\n>>> <i>{uzbek}</i>\n\n📍 {topic} › {section} › {chapter}\n📝 한국어로 작성하세요:",

        # JAVOBLAR (FEEDBACK)
        "feedback_correct": "✅ <b>정답!</b> 🇰🇷 <code>{korean}</code>",
        "feedback_wrong": "❌ <b>오답!</b>\n🇰🇷 정답: <code>{korean}</code>\n📌 입력: <s>{user_answer}</s>",
        "game_correct_short": "✅ <b>정답!</b> 🇰🇷 <code>{korean}</code>",
        "game_wrong_short": "❌ <b>오답!</b> 🇰🇷 <code>{korean}</code>\n📌 입력: <s>{user_answer}</s>",

        # O'YIN TUGASHI VA TO'XTATISH
        "game_finished": "🎊 <b>게임 종료!</b>\n\n✅ 정답: <b>{correct}</b>\n❌ 오답: <b>{wrong}</b>",
        "auto_game_finished": "🎉 <b>자동 게임 완료!</b>\n\n✅ 정답: {correct}\n❌ 오답: {wrong}\n\n다음 시간에 다시 단어가 전송됩니다! ⏰",
        "game_stopped": "🛑 <b>게임 중지!</b>\n\n✅ 정답: {correct}\n❌ 오답: {wrong}",
        "btn_stop_game": "🛑 중지",

        # AVTO REJIM SOZLAMALARI
        "auto_select_time": "⏰ <b>자동 모드 설정:</b>\n\n몇 분마다 단어를 받으시겠습니까?",
        "auto_time_set": "✅ {time}분마다 10개 단어가 전송됩니다!",
        "btn_5min": "⏱ 5분", "btn_10min": "⏱ 10분", "btn_15min": "⏱ 15분", "btn_30min": "⏱ 30분", "btn_60min": "⏱ 60분",

        # ADMIN VA XATOLAR
        "no_words": "❌ 단어를 찾을 수 없습니다!",
        "no_topics": "❌ 주제 없음!",
        "no_sections": "❌ 섹션 없음!",
        "admin_welcome": "✅ 관리자 패널에 오신 것을 환영합니다!",
        "admin_enter_password": "🔐 관리자 패널에 접근하려면 비밀번호를 입력하세요:",
        "admin_wrong_password": "❌ 잘못된 비밀번호!",
        "admin_user_blocked": "✅ 사용자가 차단되었습니다!",
        "admin_user_unblocked": "✅ 사용자 차단이 해제되었습니다!"
    }
}

def get_text(lang, key, **kwargs):
    # Til kodlarini standartlashtirish
    target_lang = "ko" if lang in ["ko", "kr", "kr"] else "uz"
    
    # Matnni olish
    text = ALL_TEXTS.get(target_lang, {}).get(key, f"Missing key: {key}")
    
    # Formatlash (kwargs orqali o'zgaruvchilarni joylash)
    try:
        return text.format(**kwargs)
    except KeyError:
        return text

# ==================== WORD POOL MANAGER ====================

def get_next_word(user_id: int):
    """Takrorlanmaslik uchun so'z olish"""
    all_words = dict_handler.get_all_words(user_id)  # ✅ user_id qo'shildi
    
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
        [KeyboardButton(text="/game"), KeyboardButton(text="/avtogame")],
        [KeyboardButton(text="/bo'limlar")],
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
    """O'yin klaviaturasi (To'xtatish tugmasi - INLINE)"""
    keyboard = [
        [InlineKeyboardButton(
            text=get_text(lang, "btn_stop_game"),
            callback_data="stop_game"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_topics_keyboard(user_id: int, lang: str) -> InlineKeyboardMarkup:
    """Topiklar ro'yxati"""
    topics = dict_handler.get_all_topics(user_id)  # ✅
    
    keyboard = []
    for topic in topics:
        keyboard.append([InlineKeyboardButton(
            text=f"📚 {topic}",
            callback_data=f"topic_{topic}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text=get_text(lang, "back"),
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_sections_keyboard(user_id: int, topic: str, lang: str) -> InlineKeyboardMarkup:
    sections = dict_handler.get_topic_sections(user_id, topic)  # ✅
    
    keyboard = []
    for section in sections:
        keyboard.append([InlineKeyboardButton(
            text=f"📖 {section.title()}",
            callback_data=f"section_{topic}_{section}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text=get_text(lang, "back"),
        callback_data="chapters_main"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chapters_chapters_keyboard(user_id: int, topic: str, section: str, lang: str) -> InlineKeyboardMarkup:
    chapters = dict_handler.get_section_chapters(user_id, topic, section)  # ✅
    
    keyboard = []
    for chapter in chapters:
        keyboard.append([InlineKeyboardButton(
            text=f"📝 {chapter}",
            callback_data=f"chapter_{topic}_{section}_{chapter}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text=get_text(lang, "back"),
        callback_data=f"section_{topic}_{section}"
    )])
    
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
    total_topics = len(dict_handler.get_all_topics(user_id))  # ✅ user_id qo'shildi
    total_words = dict_handler.get_total_words(user_id)       # ✅ user_id qo'shildi
    
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
        reply_markup=get_chapters_topics_keyboard(user_id, lang)  # ✅
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

## ============================================
# /GAME KOMANDASI VA INLINE BOSHLASH
# ============================================

@router.message(Command("game"))
async def cmd_game(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_general_mode"), callback_data="game_mode_general")],
        [InlineKeyboardButton(text=get_text(lang, "btn_custom_mode"), callback_data="game_mode_custom")]
    ])
    await state.set_state(GameModeState.selecting_mode)
    await message.answer(get_text(lang, "game_select_mode"), reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data == "start_game")
async def inline_start_game(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_general_mode"), callback_data="game_mode_general")],
        [InlineKeyboardButton(text=get_text(lang, "btn_custom_mode"), callback_data="game_mode_custom")]
    ])
    
    await state.set_state(GameModeState.selecting_mode)
    await callback.message.edit_text(get_text(lang, "game_select_mode"), reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# ============================================
# UMUMIY REJIM HANDLERI
# ============================================

@router.callback_query(F.data == "game_mode_general")
async def game_general_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    # get_next_word o'rniga yangi yozgan get_random_word funksiyangizni ishlatamiz
    word = dict_handler.get_random_word(user_id)
    
    if not word:
        await callback.answer(get_text(lang, "no_words"), show_alert=True)
        await state.clear()
        return
    
    await state.set_state(GameModeState.playing)
    await state.update_data(
        current_word=word,
        start_time=datetime.now().timestamp(),
        question_count=1,
        mode='general'
    )
    
    await callback.message.edit_text(
        get_text(
            lang, "game_question",
            uzbek=word['uzbek'],
            topic=word['topic'],
            section=word['section'],
            chapter=word['chapter'],
            count=1
        ),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()

# ============================================
# BELGILANGAN REJIM - TOPIK TANLASH
# ============================================

@router.callback_query(F.data == "game_mode_custom")
async def game_custom_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    topics = dict_handler.get_all_topics(user_id)
    if not topics:
        await callback.answer(get_text(lang, "no_topics"), show_alert=True)
        return
    
    keyboard = [[InlineKeyboardButton(text=f"📚 {topic}", callback_data=f"game_topic_{topic}")] for topic in topics]
    
    await state.set_state(GameModeState.selecting_topic)
    await callback.message.edit_text(get_text(lang, "game_select_topic"), 
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    await callback.answer()

# ============================================
# BELGILANGAN REJIM - BO'LIM TANLASH
# ============================================

@router.callback_query(F.data.startswith("game_topic_"))
async def game_select_topic(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    topic = callback.data.replace("game_topic_", "")
    sections = dict_handler.get_topic_sections(user_id, topic)
    
    if not sections:
        await callback.answer(get_text(lang, "no_sections"), show_alert=True)
        return
    
    keyboard = [[InlineKeyboardButton(text=f"📖 {s.title()}", callback_data=f"game_section_{topic}_{s}")] for s in sections]
    
    await state.set_state(GameModeState.selecting_section)
    await state.update_data(selected_topic=topic)
    
    await callback.message.edit_text(get_text(lang, "game_select_section", topic=topic),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    await callback.answer()

# ============================================
# BELGILANGAN REJIM - O'YIN BOSHLASH
# ============================================

@router.callback_query(F.data.startswith("game_section_"))
async def game_select_section(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    # Callbackni ajratib olish
    parts = callback.data.replace("game_section_", "").split("_", 1)
    topic = parts[0]
    section = parts[1]
    
    # Bo'limdan birinchi so'zni olish
    word = dict_handler.get_random_word(user_id, topic=topic, section=section)
    
    if not word:
        await callback.answer(get_text(lang, "no_words"), show_alert=True)
        return
    
    await state.update_data(
        mode='custom',
        topic=topic,
        section=section,
        current_word=word,
        start_time=datetime.now().timestamp(),
        question_count=1
    )
    await state.set_state(GameModeState.playing)
    
    await callback.message.edit_text(
        get_text(lang, "game_starting_custom", topic=topic, section=section) + "\n\n" +
        get_text(lang, "game_question", uzbek=word['uzbek'], topic=topic, section=section, 
                      chapter=word.get('chapter', '---'), count=1),
        reply_markup=get_game_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()

# ============================================
# JAVOBNI TEKSHIRISH (ASOSIY MANTIQ)
# ============================================

@router.message(GameModeState.playing, lambda message: not message.text.startswith('/'))
async def process_game_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    data = await state.get_data()
    
    word = data.get('current_word')
    if not word:
        return

    user_answer = message.text.strip().lower()
    correct_answer = word['korean'].strip().lower()
    is_correct = (user_answer == correct_answer)
    
    # Statistika
    start_time = data.get('start_time', datetime.now().timestamp())
    time_spent = int(datetime.now().timestamp() - start_time)
    await user_db.update_statistics(user_id, is_correct, time_spent)
    
    # Natija matni (Tilga qarab)
    if is_correct:
        feedback = f"✅ <b>To'g'ri!</b>\n🇰🇷 {word['korean']}" if lang == "uz" else f"✅ <b>정답입니다!</b>\n🇰🇷 {word['korean']}"
    else:
        feedback = f"❌ <b>Noto'g'ri!</b>\nTo'g'ri: <code>{word['korean']}</code>" if lang == "uz" else f"❌ <b>틀렸습니다!</b>\n정답: <code>{word['korean']}</code>"
    
    # Keyingi so'zni olish
    mode = data.get('mode', 'general')
    next_word = dict_handler.get_random_word(user_id, 
                                             topic=data.get('topic') if mode == 'custom' else None, 
                                             section=data.get('section') if mode == 'custom' else None)
    
    if not next_word:
        await message.answer(f"{feedback}\n\n🏁 " + get_text(lang, "no_words"))
        await state.clear()
        return

    q_count = data.get('question_count', 1) + 1
    await state.update_data(current_word=next_word, start_time=datetime.now().timestamp(), question_count=q_count)

    next_question = get_text(lang, "game_question", uzbek=next_word['uzbek'], 
                                  topic=next_word['topic'], section=next_word['section'], 
                                  chapter=next_word['chapter'], count=q_count)

    await message.answer(f"{feedback}\n\n━━━━━━━━━━━━━━\n\n{next_question}", 
                         reply_markup=get_game_keyboard(lang), parse_mode="HTML")
@router.message(AutoPlayState.playing, lambda message: not message.text.startswith('/'))
async def process_auto_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    data = await state.get_data()
    word = data.get('current_word')

    if not word: return

    # 1. Javobni tekshirish
    user_answer = message.text.strip().lower()
    correct_answer = word['korean'].strip().lower()
    
    if user_answer == correct_answer:
        await user_db.update_statistics(user_id, True, 0)
        await message.answer(f"✅ <b>To'g'ri!</b> (Avtomatik)", parse_mode="HTML")
    else:
        await user_db.update_statistics(user_id, False, 0)
        await message.answer(f"❌ <b>Xato!</b> 🇰🇷: <code>{word['korean']}</code>", parse_mode="HTML")

    # 2. Keyingi savolga o'tish mantiqi
    current_step = data.get('auto_current_step', 1)
    max_steps = 10 # Siz xohlagan 10 ta savol

    if current_step < max_steps:
        # Keyingi savolni olish
        next_word = dict_handler.get_random_word(user_id)
        if next_word:
            new_step = current_step + 1
            await state.update_data(current_word=next_word, auto_current_step=new_step)
            
            await message.answer(
                f"🤖 <b>(AVTOMATIK SAVOL)</b> {new_step}/{max_steps}\n\n" +
                get_text(lang, "auto_question", 
                         uzbek=next_word['uzbek'], topic=next_word['topic']),
                parse_mode="HTML"
            )
    else:
        # 10 ta savol tugadi
        await state.update_data(current_word=None)
        await message.answer(f"🏁 <b>Navbatdagi 10 talik paket tugadi!</b>\nKeyingi savollar belgilangan vaqtdan so'ng yuboriladi.")
# ============================================
# O'YINNI TO'XTATISH
# ============================================

@router.callback_query(F.data == "stop_game")
async def stop_game_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    stats = await user_db.get_statistics(user_id)
    await state.clear()
    
    await callback.message.edit_text(
        get_text(lang, "game_stopped", correct=stats['correct'], wrong=stats['wrong']),
        parse_mode="HTML"
    )
    # Asosiy menyu tugmalarini yuborish
    from main import get_main_menu_keyboard # Import muammosi bo'lmasligi uchun
    await callback.message.answer("🏠", reply_markup=get_main_menu_keyboard(lang))
    await callback.answer()

# ============================================
# AVTOMATIK O'YIN TIZIMI
# ============================================

# /avtogame komandasi
@router.message(Command("avtogame"))
async def cmd_auto_game(message: Message, state: FSMContext):
    """Avtomatik o'yin - vaqtni tanlash"""
    await state.clear()
    user_id = message.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_5min"), callback_data="auto_time_5")],
        [InlineKeyboardButton(text=get_text(lang, "btn_10min"), callback_data="auto_time_10")],
        [InlineKeyboardButton(text=get_text(lang, "btn_15min"), callback_data="auto_time_15")],
        [InlineKeyboardButton(text=get_text(lang, "btn_30min"), callback_data="auto_time_30")],
        [InlineKeyboardButton(text=get_text(lang, "btn_60min"), callback_data="auto_time_60")]
    ])
    
    await state.set_state(AutoPlayState.selecting_time)
    await message.answer(
        get_text(lang, "auto_select_time"),
        reply_markup=markup,
        parse_mode="HTML"
    )

# Avto vaqtni tanlash
@router.callback_query(F.data.startswith("auto_time_"))
async def auto_select_time(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    time_minutes = int(callback.data.split("_")[2])
    await state.update_data(auto_interval=time_minutes)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_general_mode"), callback_data="auto_mode_general")],
        [InlineKeyboardButton(text=get_text(lang, "btn_custom_mode"), callback_data="auto_mode_custom")]
    ])
    
    await state.set_state(AutoPlayState.selecting_mode)
    await callback.message.edit_text(
        get_text(lang, "auto_time_set", time=time_minutes) + "\n\n" + get_text(lang, "game_select_mode"),
        reply_markup=markup,
        parse_mode="HTML"
    )
    await callback.answer()

# Avto umumiy rejim
@router.callback_query(F.data == "auto_mode_general")
async def auto_general_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    data = await state.get_data()
    interval = data.get('auto_interval', 15)
    
    await state.update_data(mode='general', topic=None, section=None)
    
    msg = (f"✅ Avtomatik rejim faollashtirildi!\n⏰ Har {interval} daqiqada so'zlar keladi." if lang == "uz" 
           else f"✅ 자동 모드가 활성화되었습니다!\n⏰ {interval}분마다 단어가 전송됩니다.")
    
    await callback.message.edit_text(msg, parse_mode="HTML")
    await state.set_state(AutoPlayState.playing)
    await callback.answer()

# Avto belgilangan rejim - topik
@router.callback_query(F.data == "auto_mode_custom")
async def auto_custom_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    topics = dict_handler.get_all_topics(user_id)
    if not topics:
        await callback.answer(get_text(lang, "no_topics"), show_alert=True)
        return
    
    keyboard = [[InlineKeyboardButton(text=f"📚 {t}", callback_data=f"auto_topic_{t}")] for t in topics]
    
    await state.set_state(AutoPlayState.selecting_topic)
    await callback.message.edit_text(
        get_text(lang, "game_select_topic"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

# Avto topik tanlandi - bo'lim tanlash
@router.callback_query(F.data.startswith("auto_topic_"))
async def auto_select_topic(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    topic = callback.data.replace("auto_topic_", "")
    sections = dict_handler.get_topic_sections(user_id, topic)
    
    if not sections:
        await callback.answer(get_text(lang, "no_sections"), show_alert=True)
        return
    
    await state.update_data(topic=topic)
    keyboard = [[InlineKeyboardButton(text=f"📖 {s.title()}", callback_data=f"auto_section_{s}")] for s in sections]
    
    await state.set_state(AutoPlayState.selecting_section)
    await callback.message.edit_text(
        get_text(lang, "game_select_section_only", topic=topic),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )
    await callback.answer()

# Avto bo'lim tanlandi - faollashtirish
@router.callback_query(F.data.startswith("auto_section_"))
async def auto_select_section(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    section = callback.data.replace("auto_section_", "")
    data = await state.get_data()
    interval = data.get('auto_interval', 15)
    
    await state.update_data(mode='custom', section=section)
    
    msg = (get_text(lang, "game_starting_custom", topic=data.get('topic'), section=section) + 
           f"\n\n⏰ Every {interval} min.")
    
    await callback.message.edit_text(msg, parse_mode="HTML")
    await state.set_state(AutoPlayState.playing)
    await callback.answer()

# ============================================
# AVTOMATIK YUBORISH TIZIMI (Scheduler)
# ============================================
async def send_auto_words():
    from aiogram.fsm.storage.base import StorageKey
    import time

    while True:
        try:
            users = await user_db.get_all_users()
            for user in users:
                user_id = user['user_id']
                state_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
                state = FSMContext(storage=storage, key=state_key)
                current_state = await state.get_state()
                
                if current_state == AutoPlayState.playing:
                    data = await state.get_data()
                    
                    # Foydalanuvchi tanlagan vaqt (minutda)
                    interval_min = data.get('auto_interval', 15) 
                    interval_sec = interval_min * 60
                    last_sent = data.get('last_auto_sent', 0)
                    now = time.time()

                    # Qat'iy vaqt tekshiruvi: faqat vaqti kelgandagina yuboradi
                    if now - last_sent >= interval_sec:
                        lang = await user_db.get_language(user_id) or "uz"
                        word = dict_handler.get_random_word(
                            user_id,
                            topic=data.get('topic'),
                            section=data.get('section')
                        )
                        
                        if word:
                            # Eskisini unutib, yangi paketni 1/10 dan boshlaymiz
                            await state.update_data(
                                current_word=word, 
                                last_auto_sent=now, 
                                auto_current_step=1
                            )
                            
                            text = get_text(
                                lang, "auto_question", 
                                uzbek=word['uzbek'], 
                                topic=word.get('topic', '...'),
                                section=word.get('section', '...'),
                                chapter=word.get('chapter', '...'),
                                count=1
                            )
                            
                            await bot.send_message(user_id, text, parse_mode="HTML")
                            
        except Exception as e:
            print(f"❌ send_auto_words xatosi: {e}")
            
        await asyncio.sleep(20) # Bazani tekshirish oralig'i
# ==================== BO'LIMLAR ====================

@router.callback_query(F.data == "chapters_main")
async def chapters_main_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        get_text(lang, "chapters_select_topic"),
        reply_markup=get_chapters_topics_keyboard(user_id, lang)  # ✅
    )
    await callback.answer()

@router.callback_query(F.data.startswith("topic_"))
async def chapters_topic_selected(callback: CallbackQuery):
    topic = callback.data.replace("topic_", "")
    user_id = callback.from_user.id
    lang = await user_db.get_language(user_id) or "uz"
    
    await callback.message.edit_text(
        f"📂 {topic}\n\n" + get_text(lang, "chapters_select_section"),
        reply_markup=get_chapters_sections_keyboard(user_id, topic, lang)  # ✅
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
        reply_markup=get_chapters_chapters_keyboard(user_id, topic, section, lang)  # ✅
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
    
    words = dict_handler.get_chapter_words(user_id, topic, section, chapter)  # ✅
    
    if not words:
        await callback.answer(get_text(lang, "no_words"), show_alert=True)
        return
    
    text = f"📚 <b>{chapter}</b>\n\n"
    for korean, uzbek in words.items():
        text += f"🇰🇷 {korean} – 🇺🇿 {uzbek}\n"
    
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
    
    # BARCHA userlarning so'zlari
    all_users = await user_db.get_all_users()
    total_words = sum(dict_handler.get_total_words(u['user_id']) for u in all_users)  # ✅
    
    await callback.message.edit_text(
        get_text(lang, "bot_statistics", users=total_users, words=total_words),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin_panel")]
        ])
    )
    await callback.answer()


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