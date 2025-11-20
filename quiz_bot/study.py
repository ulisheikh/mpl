# study.py  (Aiogram 3) — Final with UNSUBSCRIBE STOP fix
import asyncio
import importlib.util
import json
import logging
import pathlib
import random
import re
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ------------- CONFIG -------------
BOT_TOKEN = "8284065959:AAEB1_8uVcXpMZCCQEfM8g2ZjKrDOh4ytY4"  # <-- YOUR TOKEN
TC_PY = "tc.py"
STATE_FILE = "quiz_state.json"
BLOCK_INTERVAL_MIN = 12         # default interval in minutes (used outside 08:00-16:00)
QUESTIONS_PER_BLOCK = 5         # blokdagi savol soni
RELOAD_CHECK_SECONDS = 3        # tc.py ni tekshirish intervalli
USERS_DB = "users.db"
# ----------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATA_DIR = pathlib.Path(".")
STATE_PATH = DATA_DIR / STATE_FILE
TC_PATH = DATA_DIR / TC_PY

# ---------- persistent state ----------
def load_state() -> Dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(s: Dict):
    STATE_PATH.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

state = load_state()

# ---------- SQLite users DB ----------
def init_db():
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        joined_at TEXT,
        last_active TEXT,
        is_subscribed INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_or_update_user(user: types.User, is_subscribed: Optional[bool]=None):
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    uid = user.id
    username = user.username or ""
    full_name = (user.full_name or "").strip()
    now = datetime.now().isoformat()
    # insert or update
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, joined_at, last_active, is_subscribed) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, username, full_name, now, now, 1 if is_subscribed else 0)
        )
    else:
        if is_subscribed is None:
            cur.execute("UPDATE users SET username = ?, full_name = ?, last_active = ? WHERE user_id = ?", (username, full_name, now, uid))
        else:
            cur.execute("UPDATE users SET username = ?, full_name = ?, last_active = ?, is_subscribed = ? WHERE user_id = ?", (username, full_name, now, 1 if is_subscribed else 0, uid))
    conn.commit()
    conn.close()

def set_subscription_db(user_id: int, is_sub: bool):
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_subscribed = ?, last_active = ? WHERE user_id = ?", (1 if is_sub else 0, datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def get_all_users(limit: int = 200):
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, full_name, joined_at, last_active, is_subscribed FROM users ORDER BY joined_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- load tc.py dynamically ----------
def load_ltc_from_py() -> Dict[str, Dict[str, str]]:
    if not TC_PATH.exists():
        logger.warning("tc.py topilmadi — loyihaga qo'ying: %s", str(TC_PATH))
        return {}
    mtime = TC_PATH.stat().st_mtime
    if getattr(load_ltc_from_py, "cached_mtime", None) == mtime:
        return load_ltc_from_py.cached
    spec = importlib.util.spec_from_file_location("tc_module", str(TC_PATH))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for var in ("ltc", "LTC", "tc"):
        if hasattr(module, var):
            ltc = getattr(module, var)
            if isinstance(ltc, dict):
                load_ltc_from_py.cached = ltc
                load_ltc_from_py.cached_mtime = mtime
                logger.info("tc.py yuklandi: %d chapters, mtime=%s", len(ltc), time.ctime(mtime))
                return ltc
    logger.warning("tc.py: 'ltc' dict topilmadi.")
    load_ltc_from_py.cached = {}
    load_ltc_from_py.cached_mtime = mtime
    return {}

load_ltc_from_py.cached = {}
load_ltc_from_py.cached_mtime = None

def flatten_ltc(ltc: Dict[str, Dict[str, str]]):
    flat = []
    for ch, cmds in ltc.items():
        for k, v in cmds.items():
            flat.append((ch, k, v))
    return flat

# ---------- normalization ----------
PLACEHOLDERS = re.compile(r"\b(packagename|file|filename|<.*?>)\b", flags=re.IGNORECASE)
BRACKETS = re.compile(r"[\[\]]")

def normalize_for_compare(s: str) -> str:
    s = s or ""
    s = BRACKETS.sub("", s)
    s = PLACEHOLDERS.sub("", s)
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip("`\"' ")
    return s

# ---------- helper: ensure per-chat state init (CHANGED) ----------
def ensure_chat_state_initialized(chat_id: str, flat_questions):
    st = state.setdefault(chat_id, {})
    st.setdefault("asked", [])
    st.setdefault("current", None)
    st.setdefault("current_mode", None)
    st.setdefault("in_block", False)
    st.setdefault("remaining", 0)
    st.setdefault("next_time", None)
    st.setdefault("score", 0)
    st.setdefault("auto", False)
    st.setdefault("menu_stack", [])
    st.setdefault("continuous", False)  # CHANGED: continuous mode for unsubscribe
    # unasked: if not present, fill with normalized keys of flat_questions (shuffled)
    if "unasked" not in st or not isinstance(st["unasked"], list):
        keys = []
        for ch, k, v in flat_questions:
            nk = normalize_for_compare(k)
            if nk:
                keys.append(nk)
        # unique and shuffle
        keys = list(dict.fromkeys(keys))  # preserve order unique
        random.shuffle(keys)
        st["unasked"] = keys
    return st

# ---------- balanced question selection (CHANGED) ----------
def pick_random_question(chat_id: str) -> Tuple[str, str, str]:
    """
    Pick a random (chapter, key, desc) using per-chat 'unasked' list so that every question is asked
    once before repeats. Returns original (chapter, key, desc).
    """
    global state
    ltc_local = load_ltc_from_py()
    FLAT = flatten_ltc(ltc_local)

    if not FLAT:
        raise RuntimeError("Savollar topilmadi — tc.py ni to'ldiring.")

    # Ensure chat state including unasked list
    st = ensure_chat_state_initialized(chat_id, FLAT)

    # if unasked empty -> refill from FLAT (re-create keys shuffled)
    if not st.get("unasked"):
        keys = []
        for ch, k, v in FLAT:
            nk = normalize_for_compare(k)
            if nk:
                keys.append(nk)
        keys = list(dict.fromkeys(keys))
        random.shuffle(keys)
        st["unasked"] = keys

    # choose from unasked uniformly at random
    chosen_norm = random.choice(st["unasked"])

    # find first matching item in FLAT (preserve original chapter,key,desc)
    chosen_item = None
    for ch, k, v in FLAT:
        if normalize_for_compare(k) == chosen_norm:
            chosen_item = (ch, k, v)
            break

    if not chosen_item:
        # fallback: repopulate and pick any
        st["unasked"] = []
        save_state(state)
        return pick_random_question(chat_id)

    # remove chosen_norm from unasked, record asked
    try:
        st["unasked"].remove(chosen_norm)
    except ValueError:
        pass
    st.setdefault("asked", []).append(chosen_norm)
    save_state(state)

    return chosen_item

# ---------- helper: compute next_time based on hour (CHANGED) ----------
def compute_next_time(after_dt: Optional[datetime] = None) -> datetime:
    """
    FIXED: Barcha vaqt uchun BLOCK_INTERVAL_MIN (12 minut) ishlatadi.
    Endi soat farqi yo'q!
    """
    now = after_dt or datetime.now()
    minutes = BLOCK_INTERVAL_MIN  # Har doim 12 minut
    return now + timedelta(minutes=minutes)

# ---------- STOP inline keyboard (for continuous mode) ----------
stop_quiz_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛑 STOP", callback_data="menu_stop")]
])

# ---------- send functions (keyboard handling improved) ----------
async def send_single_question(chat_id: str):
    """Ad-hoc single question (for /quiz or continuous mode) — sets current_mode='single'"""
    try:
        chapter, key, desc = pick_random_question(str(chat_id))
    except RuntimeError:
        # show menu for empty database
        await bot.send_message(chat_id, "Savollar mavjud emas. tc.py faylini to‘ldiring.", reply_markup=main_menu_markup())
        return
    st = state.setdefault(str(chat_id), {})
    st["current"] = key
    st["current_mode"] = "single"
    save_state(state)
    # CHANGED: If user is in continuous (unsubscribe) mode, show STOP inline button
    if st.get("continuous"):
        await bot.send_message(chat_id, f"📘 <b>{chapter}</b>\n\nSavol:\n{desc}\n\nJavob yozing.", parse_mode="HTML", reply_markup=stop_quiz_kb)
    else:
        # Do not override user's reply keyboard here — keep main_kb visible
        await bot.send_message(chat_id, f"📘 <b>{chapter}</b>\n\nSavol:\n{desc}\n\nJavob yozing.", parse_mode="HTML")

async def start_block_for_user(chat_id: str, questions_count: int = QUESTIONS_PER_BLOCK):
    """Initialize a block for user: set in_block and remaining and send first question."""
    st = state.setdefault(str(chat_id), {})
    st["in_block"] = True
    st["remaining"] = questions_count
    st["current_mode"] = "block"
    st["next_time"] = None
    save_state(state)
    await send_next_in_block(chat_id)

async def send_next_in_block(chat_id: str):
    """Pick and send a question inside an active block. Does not touch next_time."""
    st = state.setdefault(str(chat_id), {})
    if not st.get("in_block"):
        return
    if st.get("remaining", 0) <= 0:
        # finish block
        await finish_block(chat_id)
        return
    try:
        chapter, key, desc = pick_random_question(str(chat_id))
    except RuntimeError:
        await bot.send_message(chat_id, "Savollar topilmadi (block).", reply_markup=main_menu_markup())
        st["in_block"] = False
        st["remaining"] = 0
        save_state(state)
        return
    st["current"] = key
    st["current_mode"] = "block"
    save_state(state)
    # keep reply keyboard persistent by NOT passing reply_markup here
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔚 Stop", callback_data="menu_stop")]
    ])
    await bot.send_message(chat_id, f"📘 <b>{chapter}</b>\n\nSavol:\n{desc}\n\nJavob yozing.", parse_mode="HTML", reply_markup=inline_kb)

async def finish_block(chat_id: str):
    """Called when a block finishes: clear in_block and schedule next block based on time rules."""
    st = state.setdefault(str(chat_id), {})
    st["in_block"] = False
    st["remaining"] = 0
    st["current"] = None
    st["current_mode"] = None
    next_dt = compute_next_time(datetime.now())
    st["next_time"] = next_dt.isoformat()
    save_state(state)
    await bot.send_message(chat_id, f"✅ Blok yakunlandi. Keyingi blok { (next_dt - datetime.now()).seconds // 60 } daqiqadan so‘ng ko‘rinadi.", reply_markup=main_menu_markup())

# ---------- answer checking ----------
from difflib import SequenceMatcher

def evaluate_answer(user_text: str, correct_key: str):
    u = normalize_for_compare(user_text)
    c = normalize_for_compare(correct_key)
    if u == c and u:
        return True, "✅ To‘g‘ri!"
    if u and (u in c or c in u):
        return False, f"🤔 Yaqin! To‘g‘ri: <code>{correct_key}</code>"
    ratio = SequenceMatcher(None, u, c).ratio()
    if ratio > 0.75:
        return False, f"⚠️ O‘xshash — lekin to‘liq emas. To‘g‘ri: <code>{correct_key}</code>"
    return False, f"❌ Noto‘g‘ri. Toʻgʻri buyruq: <code>{correct_key}</code>"

# ---------- keyboards ----------
# main reply keyboard:
# Row1: START
# Row2: MENU | /restart
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="Menu"), KeyboardButton(text="/restart")]
    ],
    resize_keyboard=True
)

def main_menu_markup():
    # Inline menu with 3x2 layout: left column: subscribe, unsubscribe, ballarim
    # right column: info, chapters, rank (variant B)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="SUBSCRIBE", callback_data="subscribe"),
         InlineKeyboardButton(text="INFO", callback_data="menu_info")],
        [InlineKeyboardButton(text="UNSUBSCRIBE", callback_data="unsubscribe"),
         InlineKeyboardButton(text="CHAPTERLAR", callback_data="menu_chapters")],
        [InlineKeyboardButton(text="BALLARIM", callback_data="menu_score"),
         InlineKeyboardButton(text="RANK", callback_data="menu_rank")]
    ])

# ---------- handlers ----------
@dp.message(F.text == "/start")
async def cmd_start(msg: types.Message):
    # record user
    add_or_update_user(msg.from_user)
    help_text = (
        "👋 Assalomu alaykum! Men Linux buyruqlari quiz-botman.\n\n"
        "Botni boshlash uchun Menu tugmasini bosing yoki START tugmasi orqali tez ishga tushiring.\n\n"
        "• SUBSCRIBE — avtomatik bloklarni yoqish\n"
        "• UNSUBSCRIBE — cheksiz savol rejimi (Stop tugmasigacha)\n"
        "• BALLARIM — ballaringizni ko‘rish\n"
        "• INFO — buyruqlar haqida ma'lumot\n"
        "• CHAPTERLAR — bo‘limlar\n"
        "• RANK — reyting (Variant B)\n"
    )
    # send initial info + inline menu
    await msg.answer(help_text, reply_markup=main_kb)
    await msg.answer("Menu:", reply_markup=main_menu_markup())

@dp.message(F.text == "/restart")
async def cmd_restart(msg: types.Message):
    uid = str(msg.chat.id)
    # clear chat state for this user
    state[uid] = {
        "asked": [], "unasked": [], "current": None, "current_mode": None,
        "in_block": False, "remaining": 0, "next_time": None,
        "score": 0, "auto": False, "menu_stack": [], "continuous": False
    }
    save_state(state)
    # reset DB subscription flag for user (optional)
    try:
        set_subscription_db(msg.from_user.id, False)
    except Exception:
        pass
    await msg.answer("🔄 Bot holati tozalandi. Hammasi 0 dan boshlandi.", reply_markup=main_kb)

@dp.message(F.text == "Menu")
async def msg_menu(msg: types.Message):
    add_or_update_user(msg.from_user)
    await msg.answer("Menu:", reply_markup=main_menu_markup())

@dp.message(F.text == "/quiz")
async def cmd_quiz(msg: types.Message):
    add_or_update_user(msg.from_user)
    await send_single_question(msg.chat.id)

# remove /quiz3 per request (not used)

@dp.message(F.text == "/subscribe")
async def cmd_subscribe(msg: types.Message):
    uid = str(msg.chat.id)
    st = state.setdefault(uid, {})
    st["auto"] = True
    st["continuous"] = False
    st["next_time"] = datetime.now().isoformat()
    save_state(state)
    set_subscription_db(msg.from_user.id, True)
    add_or_update_user(msg.from_user, is_subscribed=True)
    await msg.answer("✅ Avtomatik bloklar yoqildi. Vaqt qoidalariga ko‘ra bloklar keladi.", reply_markup=main_kb)

@dp.message(F.text == "/unsubscribe")
async def cmd_unsubscribe(msg: types.Message):
    uid = str(msg.chat.id)
    st = state.setdefault(uid, {})
    # continuous mode: send questions without scheduling until stopped
    st["auto"] = False
    st["continuous"] = True
    st["in_block"] = False
    st["remaining"] = 0
    st["current_mode"] = None
    st["next_time"] = None
    save_state(state)
    set_subscription_db(msg.from_user.id, False)
    add_or_update_user(msg.from_user, is_subscribed=False)
    # start first question immediately
    await msg.answer("🔁 Cheksiz savol rejimi yoqildi. To‘xtatish uchun Stop tugmasini bosing (inline).", reply_markup=main_kb)
    await asyncio.sleep(0.5)
    await send_single_question(uid)

# -------------------------
# /view handler (via text command)
# -------------------------
@dp.message(F.text.startswith("/view"))
async def cmd_view(msg: types.Message):
    add_or_update_user(msg.from_user)
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) == 1:
        chapters = list(load_ltc_from_py().keys())
        if not chapters:
            await msg.answer("Hozircha bo'limlar mavjud emas.", reply_markup=main_kb)
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            *[[InlineKeyboardButton(text=ch, callback_data=f"view::{ch}") ] for ch in chapters],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")]
        ])
        await msg.answer("Mavjud bo'limlar:", reply_markup=kb)
        return
    chapter = parts[1].strip()
    ltc_local = load_ltc_from_py()
    if chapter not in ltc_local:
        await msg.answer("Bunday chapter topilmadi. Mavjudlar:\n" + "\n".join(ltc_local.keys()), reply_markup=main_kb)
        return
    lines = []
    for k, v in ltc_local[chapter].items():
        lines.append(f"{k} ➤ {v}")
    text = "\n".join(lines)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_chapters")],
    ])
    await msg.answer(f"📘 <b>{chapter}</b>\n\n{text}", parse_mode="HTML", reply_markup=kb)

@dp.message(F.text.startswith("/info"))
async def cmd_info(msg: types.Message):
    add_or_update_user(msg.from_user)
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) == 1:
        await msg.answer("Iltimos: /info <buyruq> (masalan: /info apt-get purge)", reply_markup=main_kb)
        return
    key = parts[1].strip()
    best = None
    ltc_local = load_ltc_from_py()
    flat_local = flatten_ltc(ltc_local)
    for ch, k, v in flat_local:
        if normalize_for_compare(k) == normalize_for_compare(key):
            best = (k, v)
            break
    if not best:
        for ch, k, v in flat_local:
            if normalize_for_compare(key) in normalize_for_compare(k) or normalize_for_compare(k) in normalize_for_compare(key):
                best = (k, v)
                break
    if best:
        await msg.answer(f"<b>{best[0]}</b>\n\n{best[1]}", parse_mode="HTML", reply_markup=main_kb)
    else:
        await msg.answer("Buyruq topilmadi. Iltimos toʻliq yoki aniqroq kiriting.", reply_markup=main_kb)

# -------------------------
# Inline callback handler (menu navigation + actions)
# -------------------------
@dp.callback_query(F.data)
async def cb_menu(cq: types.CallbackQuery):
    data = cq.data
    uid = str(cq.message.chat.id)
    add_or_update_user(cq.from_user)

    # SUBSCRIBE (inline) -> same as /subscribe
    if data == "subscribe":
        st = state.setdefault(uid, {})
        st["auto"] = True
        st["continuous"] = False
        st["next_time"] = datetime.now().isoformat()
        save_state(state)
        set_subscription_db(cq.from_user.id, True)
        await cq.message.answer("✅ Avtomatik bloklar yoqildi.", reply_markup=main_kb)

    # UNSUBSCRIBE (inline) -> continuous mode
    elif data == "unsubscribe":
        st = state.setdefault(uid, {})
        st["auto"] = False
        st["continuous"] = True
        st["in_block"] = False
        st["remaining"] = 0
        st["current_mode"] = None
        st["next_time"] = None
        save_state(state)
        set_subscription_db(cq.from_user.id, False)
        await cq.message.answer("🔁 Cheksiz savol rejimi yoqildi. To‘xtatish uchun Stop tugmasini bosing.", reply_markup=main_kb)
        await asyncio.sleep(0.5)
        await send_single_question(uid)

    # BALLARIM
    elif data == "menu_score":
        sc = state.get(str(uid), {}).get("score", 0)
        await cq.message.answer(f"Sizning ballingiz: {sc}", reply_markup=main_kb)

    # INFO
    elif data == "menu_info":
        await cq.message.answer("Info: /info <buyruq> bilan buyruq haqida ma'lumot oling.", reply_markup=main_kb)

    # CHAPTERLAR
    elif data == "menu_chapters":
        chapters = list(load_ltc_from_py().keys())
        if not chapters:
            await cq.message.answer("Hozircha bo'limlar mavjud emas.", reply_markup=main_kb)
            await cq.answer()
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            *[[InlineKeyboardButton(text=ch, callback_data=f"view::{ch}") ] for ch in chapters],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")]
        ])
        # push to stack
        st = state.setdefault(uid, {})
        st.setdefault("menu_stack", [])
        st["menu_stack"].append("menu_chapters")
        save_state(state)
        await cq.message.answer("Bo‘limni tanlang:", reply_markup=kb)

    # RANK (variant B)
    elif data == "menu_rank":
        # simple rank: order by score from state (in-memory)
        # build list
        ranks = []
        for k, info in state.items():
            ranks.append((k, info.get("score", 0)))
        ranks.sort(key=lambda x: x[1], reverse=True)
        top_lines = []
        for i, (chatid, sc) in enumerate(ranks[:10], start=1):
            top_lines.append(f"{i}. {chatid} — {sc} ball")
        text = "🏆 Top:\n" + ("\n".join(top_lines) if top_lines else "Hozircha hech kim yo'q.")
        await cq.message.answer(text, reply_markup=main_kb)

    # view::chapter handled elsewhere (same as previous)
    elif data and data.startswith("view::"):
        ch = data.split("::", 1)[1]
        ltc_local = load_ltc_from_py()
        if ch in ltc_local:
            text = "\n".join(f"{k} ➤ {v}" for k, v in ltc_local[ch].items())
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_chapters")]
            ])
            st = state.setdefault(uid, {})
            st.setdefault("menu_stack", [])
            st["menu_stack"].append(f"view::{ch}")
            save_state(state)
            await cq.message.answer(f"📘 {ch}\n\n{text}", reply_markup=kb)
        else:
            await cq.message.answer("Bunday bo‘lim topilmadi.", reply_markup=main_kb)

    # STOP (used to stop blocks or continuous mode)
    elif data == "menu_stop":
        st = state.setdefault(uid, {})
        st["in_block"] = False
        st["remaining"] = 0
        st["current"] = None
        st["current_mode"] = None
        st["continuous"] = False
        st["auto"] = False
        st["next_time"] = None
        save_state(state)
        await cq.message.answer("Quiz to‘xtatildi.", reply_markup=main_kb)

    # BACK navigation
    elif data == "back_to_menu":
        st = state.setdefault(uid, {})
        st["menu_stack"] = []
        save_state(state)
        await cq.message.answer("Menu:", reply_markup=main_menu_markup())

    elif data == "back_to_chapters":
        st = state.setdefault(uid, {})
        if st.get("menu_stack"):
            st["menu_stack"].pop()
        chapters = list(load_ltc_from_py().keys())
        if not chapters:
            await cq.message.answer("Hozircha bo'limlar mavjud emas.", reply_markup=main_kb)
            await cq.answer()
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            *[[InlineKeyboardButton(text=ch, callback_data=f"view::{ch}") ] for ch in chapters],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")]
        ])
        save_state(state)
        await cq.message.answer("Bo‘limni tanlang:", reply_markup=kb)

    await cq.answer()

# -------------------------
# generic message handler (answers + fallback)
# -------------------------
@dp.message()
async def generic_handler(msg: types.Message):
    text = (msg.text or "").strip()
    uid = str(msg.chat.id)
    add_or_update_user(msg.from_user)  # update activity on any message
    st = state.setdefault(uid, {})
    cur = st.get("current")
    if cur:
        is_ok, feedback = evaluate_answer(text, cur)
        await msg.answer(feedback, parse_mode="HTML")
        if is_ok:
            st["score"] = st.get("score", 0) + 1
        mode = st.get("current_mode")
        st["current"] = None
        save_state(state)
        # If continuous mode (unsubscribe), send next question immediately after answer
        if st.get("continuous"):
            await asyncio.sleep(0.5)
            await send_single_question(uid)
            return
        if mode == "block" and st.get("in_block"):
            st["remaining"] = max(0, st.get("remaining", 0) - 1)
            save_state(state)
            if st.get("remaining", 0) > 0:
                await asyncio.sleep(0.8)
                await send_next_in_block(uid)
            else:
                await finish_block(uid)
        else:
            st["current_mode"] = None
            save_state(state)
        return

    # no active question => commands / fallback
    low = text.lower()
    if low == "/start":
        await cmd_start(msg)
        return
    if low == "/restart":
        await cmd_restart(msg)
        return
    if low == "menu":
        await msg_menu(msg)
        return
    # support /users to view DB users (admin can use)
    if low == "/users":
        rows = get_all_users(200)
        lines = []
        for r in rows:
            uid_r, uname, fulln, joined, last_active, is_sub = r
            lines.append(f"{uid_r} | @{uname or '-'} | {fulln or '-'} | sub:{is_sub} | last:{last_active}")
        if not lines:
            await msg.answer("Hech qanday foydalanuvchi topilmadi.", reply_markup=main_kb)
        else:
            # send chunked if long
            chunk = "\n".join(lines[:100])
            await msg.answer(f"Users (top {min(len(lines),100)}):\n{chunk}", reply_markup=main_kb)
        return

    if low.startswith("/view"):
        await cmd_view(msg)
        return
    if low.startswith("/info"):
        await cmd_info(msg)
        return

    await msg.answer("Hozir savol yo‘q. Menu tugmasini bosing yoki /start ni bosing.", reply_markup=main_kb)

# ---------- scheduler ----------
async def scheduler_loop():
    load_ltc_from_py()
    while True:
        try:
            _ = load_ltc_from_py()
            now = datetime.now()
            for uid, info in list(state.items()):
                if not info.get("auto"):
                    continue
                if info.get("in_block"):
                    continue
                nxt = info.get("next_time")
                if not nxt:
                    continue
                try:
                    nxt_dt = datetime.fromisoformat(nxt)
                except Exception:
                    state[uid]["next_time"] = None
                    save_state(state)
                    continue
                if now >= nxt_dt:
                    logger.info("Starting block for %s (scheduled)", uid)
                    asyncio.create_task(start_block_for_user(uid))
            await asyncio.sleep(RELOAD_CHECK_SECONDS)
        except Exception as e:
            logger.exception("Scheduler error: %s", e)
            await asyncio.sleep(5)

# ---------- auto-reload loop ----------
async def auto_reload_loop():
    while True:
        try:
            load_ltc_from_py()
        except Exception as e:
            logger.exception("Auto-reload error: %s", e)
        await asyncio.sleep(RELOAD_CHECK_SECONDS)

# ---------- startup ----------
async def main():
    if not BOT_TOKEN:
        print("TOKEN kiritilmagan!")
        return
    init_db()
    asyncio.create_task(scheduler_loop())
    asyncio.create_task(auto_reload_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
