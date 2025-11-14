# study.py  (Aiogram 3) — Scheduled blocks (12 min) x 5 questions per block, wait-for-answer behavior
import asyncio
import importlib.util
import json
import logging
import pathlib
import random
import re
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
BLOCK_INTERVAL_MIN = 12         # har bir blok orasidagi interval (12 daqiqa)
QUESTIONS_PER_BLOCK = 5         # blokdagi savol soni
RELOAD_CHECK_SECONDS = 3        # tc.py ni tekshirish intervalli
# ----------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATA_DIR = pathlib.Path(".")
STATE_PATH = DATA_DIR / STATE_FILE
TC_PATH = DATA_DIR / TC_PY

# ---------- persistent state ----------
# structure per chat_id:
# { "asked":[norm_keys...], "current": original_key or None, "current_mode": "block"|"single"|None,
#   "in_block": bool, "remaining": int, "next_time": iso or None, "score": int, "auto": bool }
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

# ---------- question selection (no side-effects) ----------
def pick_random_question(chat_id: str) -> Tuple[str, str, str]:
    """
    Pick a random (chapter, key, desc) and mark as asked for this chat to avoid repeats.
    This function DOES NOT set next_time. Caller controls scheduling.
    """
    global state
    ltc_local = load_ltc_from_py()
    FLAT = flatten_ltc(ltc_local)
    if not FLAT:
        raise RuntimeError("Savollar topilmadi — tc.py ni to'ldiring.")
    st = state.setdefault(chat_id, {"asked": [], "current": None, "current_mode": None,
                                    "in_block": False, "remaining": 0, "next_time": None,
                                    "score": 0, "auto": False})
    asked = set(st.get("asked", []))
    choices = [item for item in FLAT if normalize_for_compare(item[1]) not in asked and normalize_for_compare(item[1]) != ""]
    if not choices:
        # reset asked history
        st["asked"] = []
        asked = set()
        choices = FLAT.copy()
    chapter, key, desc = random.choice(choices)
    st["asked"].append(normalize_for_compare(key))
    save_state(state)
    return chapter, key, desc

# ---------- send functions ----------
async def send_single_question(chat_id: str):
    """Ad-hoc single question (for /quiz) — sets current_mode='single'"""
    try:
        chapter, key, desc = pick_random_question(str(chat_id))
    except RuntimeError:
        await bot.send_message(chat_id, "Savollar mavjud emas. tc.py faylini to‘ldiring.", reply_markup=main_kb)
        return
    st = state.setdefault(str(chat_id), {})
    st["current"] = key
    st["current_mode"] = "single"
    save_state(state)
    await bot.send_message(chat_id, f"📘 <b>{chapter}</b>\n\nSavol:\n{desc}\n\nJavob yozing.", parse_mode="HTML", reply_markup=main_kb)

async def start_block_for_user(chat_id: str):
    """Initialize a block for user: set in_block and remaining and send first question."""
    st = state.setdefault(str(chat_id), {})
    st["in_block"] = True
    st["remaining"] = QUESTIONS_PER_BLOCK
    st["current_mode"] = "block"
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
        await bot.send_message(chat_id, "Savollar topilmadi (block).", reply_markup=main_kb)
        st["in_block"] = False
        st["remaining"] = 0
        save_state(state)
        return
    st["current"] = key
    st["current_mode"] = "block"
    save_state(state)
    await bot.send_message(chat_id, f"📘 <b>{chapter}</b>\n\nSavol:\n{desc}\n\nJavob yozing.", parse_mode="HTML", reply_markup=main_kb)

async def finish_block(chat_id: str):
    """Called when a block finishes: clear in_block and schedule next block."""
    st = state.setdefault(str(chat_id), {})
    st["in_block"] = False
    st["remaining"] = 0
    st["current"] = None
    st["current_mode"] = None
    # schedule next block after interval
    st["next_time"] = (datetime.now() + timedelta(minutes=BLOCK_INTERVAL_MIN)).isoformat()
    save_state(state)
    await bot.send_message(chat_id, f"✅ Blok yakunlandi. Keyingi blok {BLOCK_INTERVAL_MIN} daqiqadan so‘ng ko‘rinadi.", reply_markup=main_kb)

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
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text="/help")]],
    resize_keyboard=True
)

def main_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Boshlash — Quiz", callback_data="menu_quiz"),
         InlineKeyboardButton(text="Bo‘limlarni ko‘rish", callback_data="menu_view")],
        [InlineKeyboardButton(text="Ballarim", callback_data="menu_score"),
         InlineKeyboardButton(text="Reload tc.py", callback_data="menu_reload")],
        [InlineKeyboardButton(text="To‘xtatish", callback_data="menu_stop")]
    ])

# ---------- handlers ----------
@dp.message(F.text.in_({"/start", "/help"}))
async def cmd_start_help(msg: types.Message):
    help_text = (
        "👋 Assalomu alaykum! Men Linux buyruqlari quiz-botman.\n\n"
        "/quiz — bitta savol oladi\n"
        "/quiz3 — ketma-ket 3 savol oladi (har biriga javobni kutadi)\n"
        "/subscribe — avtomatik bloklarni (har 12 daqiqa) yoqish\n"
        "/unsubscribe — avtomatik bloklarni o‘chirish\n"
        "/reload — tc.py qayta yuklash\n"
        "/info <buyruq> — buyruq izohi\n"
        "/view <chapter> — bo‘limni ko‘rish\n\n"
        "Har blok: 5 savol. Bot har savolga javobingizni kutadi, keyin keyingisiga o‘tadi."
    )
    await msg.answer(help_text, reply_markup=main_kb)
    await msg.answer("Menu:", reply_markup=main_menu_markup())

@dp.message(F.text == "/quiz")
async def cmd_quiz(msg: types.Message):
    await send_single_question(msg.chat.id)

@dp.message(F.text == "/quiz3")
async def cmd_quiz3(msg: types.Message):
    # implement as a temporary short block of 3 questions (user-driven)
    uid = str(msg.chat.id)
    st = state.setdefault(uid, {})
    # if already in block, inform
    if st.get("in_block"):
        await msg.answer("Siz hozir blok ichidasiz — avvalgi blokni tugating yoki /stop qiling.", reply_markup=main_kb)
        return
    # create a temp block
    st["in_block"] = True
    st["remaining"] = 3
    st["current_mode"] = "block"
    save_state(state)
    await send_next_in_block(uid)

@dp.message(F.text == "/subscribe")
async def cmd_subscribe(msg: types.Message):
    uid = str(msg.chat.id)
    st = state.setdefault(uid, {})
    st["auto"] = True
    # schedule first block soon (immediately)
    st["next_time"] = datetime.now().isoformat()
    save_state(state)
    await msg.answer("✅ Avtomatik bloklar yoqildi. Har 12 daqiqada bloklar keladi (har blok 5 savol).", reply_markup=main_kb)

@dp.message(F.text == "/unsubscribe")
async def cmd_unsubscribe(msg: types.Message):
    uid = str(msg.chat.id)
    st = state.setdefault(uid, {})
    st["auto"] = False
    st["next_time"] = None
    save_state(state)
    await msg.answer("❌ Avtomatik bloklar o‘chirildi.", reply_markup=main_kb)

# -------------------------
# /view handler (view a chapter or list chapters)
# -------------------------
@dp.message(F.text.startswith("/view"))
async def cmd_view(msg: types.Message):
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) == 1:
        chapters = list(load_ltc_from_py().keys())
        if not chapters:
            await msg.answer("Hozircha bo'limlar mavjud emas.", reply_markup=main_kb)
            return
        await msg.answer("Mavjud bo'limlar:\n" + "\n".join(chapters), reply_markup=main_kb)
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
    await msg.answer(f"📘 <b>{chapter}</b>\n\n{text}", parse_mode="HTML", reply_markup=main_kb)

# -------------------------
# /info handler (info about a specific command)
# -------------------------
@dp.message(F.text.startswith("/info"))
async def cmd_info(msg: types.Message):
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
# Inline callback handler
# -------------------------
@dp.callback_query(F.data)
async def cb_menu(cq: types.CallbackQuery):
    data = cq.data
    uid = cq.message.chat.id
    if data == "menu_quiz":
        await cq.message.answer("Quiz boshlanmoqda...", reply_markup=main_kb)
        # start an ad-hoc single question
        await send_single_question(uid)
    elif data == "menu_view":
        chapters = list(load_ltc_from_py().keys())
        if not chapters:
            await cq.message.answer("Hozircha bo'limlar mavjud emas.", reply_markup=main_kb)
            await cq.answer()
            return
        kb = InlineKeyboardMarkup(row_width=2)
        for ch in chapters:
            kb.add(InlineKeyboardButton(ch, callback_data=f"view::{ch}"))
        await cq.message.answer("Bo‘limni tanlang:", reply_markup=kb)
    elif data and data.startswith("view::"):
        ch = data.split("::", 1)[1]
        ltc_local = load_ltc_from_py()
        if ch in ltc_local:
            text = "\n".join(f"{k} ➤ {v}" for k, v in ltc_local[ch].items())
            await cq.message.answer(f"📘 {ch}\n\n{text}", reply_markup=main_kb)
        else:
            await cq.message.answer("Bunday bo‘lim topilmadi.", reply_markup=main_kb)
    elif data == "menu_score":
        sc = state.get(str(uid), {}).get("score", 0)
        await cq.message.answer(f"Sizning ballingiz: {sc}", reply_markup=main_kb)
    elif data == "menu_reload":
        load_ltc_from_py.cached_mtime = None
        _ = load_ltc_from_py()
        await cq.message.answer("tc.py qayta yuklandi.", reply_markup=main_kb)
    elif data == "menu_stop":
        st = state.setdefault(str(uid), {"asked": [], "current": None, "current_mode": None,
                                        "in_block": False, "remaining": 0, "next_time": None,
                                        "score": 0, "auto": False})
        st["in_block"] = False
        st["remaining"] = 0
        st["current"] = None
        st["current_mode"] = None
        save_state(state)
        await cq.message.answer("Quiz to‘xtatildi.", reply_markup=main_kb)
    await cq.answer()

# -------------------------
# generic message handler (answers + fallback)
# -------------------------
@dp.message()
async def generic_handler(msg: types.Message):
    text = (msg.text or "").strip()
    uid = str(msg.chat.id)
    st = state.setdefault(uid, {})
    cur = st.get("current")
    if cur:
        is_ok, feedback = evaluate_answer(text, cur)
        # reply (feedback may contain HTML tags)
        await msg.answer(feedback, parse_mode="HTML", reply_markup=main_kb)
        if is_ok:
            st["score"] = st.get("score", 0) + 1
        # After answering: behavior depends on mode
        mode = st.get("current_mode")
        # clear current
        st["current"] = None
        save_state(state)
        if mode == "block" and st.get("in_block"):
            # decrement remaining and either send next or finish block
            st["remaining"] = max(0, st.get("remaining", 0) - 1)
            save_state(state)
            if st.get("remaining", 0) > 0:
                # send next question in same block (wait-for-answer behavior satisfied)
                await asyncio.sleep(0.8)
                await send_next_in_block(uid)
            else:
                await finish_block(uid)
        else:
            # single question mode: do not automatically send another unless user asks /quiz
            st["current_mode"] = None
            save_state(state)
        return

    # no active question => commands / fallback
    low = text.lower()
    if low in ("/start", "/help"):
        await cmd_start_help(msg)
        return
    if low.startswith("/view"):
        await cmd_view(msg)
        return
    if low.startswith("/info"):
        await cmd_info(msg)
        return

    await msg.answer("Hozir savol yo‘q. /quiz bilan boshlang yoki /help ni bosing.", reply_markup=main_kb)

# ---------- scheduler ----------
async def scheduler_loop():
    """
    Scheduler checks all users with 'auto' True and 'next_time' set.
    If now >= next_time and user not in active block, start a block.
    """
    # ensure initial load
    load_ltc_from_py()
    while True:
        try:
            _ = load_ltc_from_py()
            now = datetime.now()
            for uid, info in list(state.items()):
                # only for subscribed users
                if not info.get("auto"):
                    continue
                # if currently in block, skip (block manages itself)
                if info.get("in_block"):
                    continue
                nxt = info.get("next_time")
                if not nxt:
                    continue
                try:
                    nxt_dt = datetime.fromisoformat(nxt)
                except Exception:
                    # repair invalid value
                    state[uid]["next_time"] = None
                    save_state(state)
                    continue
                if now >= nxt_dt:
                    logger.info("Starting block for %s (scheduled)", uid)
                    # start block (non-blocking)
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
    # start background tasks
    asyncio.create_task(scheduler_loop())
    asyncio.create_task(auto_reload_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
