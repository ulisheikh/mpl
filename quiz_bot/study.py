# quiz_bot_full.py  (Aiogram 3) - FULL working version with /view and /info handlers
import asyncio
import importlib.util
import json
import logging
import pathlib
import random
import re
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ------------- CONFIG -------------
BOT_TOKEN = "8284065959:AAEB1_8uVcXpMZCCQEfM8g2ZjKrDOh4ytY4"  # <-- YOUR TOKEN (you provided it)
TC_PY = "tc.py"
STATE_FILE = "quiz_state.json"
ASK_INTERVAL_MIN = 6
RELOAD_CHECK_SECONDS = 8
# ----------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()  # Aiogram 3: Dispatcher without bot instance is fine when using start_polling(bot)

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

ltc = load_ltc_from_py()
FLAT = flatten_ltc(ltc)

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

# ---------- question selection ----------
def pick_question(chat_id: str) -> Tuple[str, str, str]:
    global FLAT, ltc
    ltc = load_ltc_from_py()
    FLAT = flatten_ltc(ltc)
    if not FLAT:
        raise RuntimeError("Savollar topilmadi — tc.py ni to'ldiring.")
    st = state.setdefault(chat_id, {"asked": [], "current": None, "next_time": None, "score": 0})
    asked = set(st.get("asked", []))
    choices = [item for item in FLAT if normalize_for_compare(item[1]) not in asked and normalize_for_compare(item[1]) != ""]
    if not choices:
        st["asked"] = []
        choices = FLAT.copy()
    chapter, key, desc = random.choice(choices)
    st["asked"].append(normalize_for_compare(key))
    st["current"] = key
    st["next_time"] = (datetime.now() + timedelta(minutes=ASK_INTERVAL_MIN)).isoformat()
    save_state(state)
    return chapter, key, desc

async def send_question(chat_id: str):
    try:
        chapter, key, desc = pick_question(str(chat_id))
    except RuntimeError:
        await bot.send_message(chat_id, "Savollar mavjud emas. tc.py faylini to‘ldiring.", reply_markup=main_kb)
        return
    # chapter uses HTML bold, so use parse_mode
    await bot.send_message(chat_id, f"📘 <b>{chapter}</b>\n\nSavol:\n{desc}\n\nBuyruq nomini yuboring.", parse_mode="HTML", reply_markup=main_kb)

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
    return False, f"❌ Noto‘g‘ri. To‘g‘ri: <code>{correct_key}</code>"

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
    # avoid raw angle-brackets which break HTML parsing
    help_text = (
        "👋 Assalomu alaykum! Men Linux buyruqlari quiz-botman.\n\n"
        "/quiz — yangi savol olish\n"
        "/reload — tc.py qayta yuklash\n"
        "/info `<buyruq>` — buyruq izohi\n"
        "/view `<chapter>` — bo‘limni ko‘rish\n\n"
        "Savol yuborganimda javob yozing, men tekshiraman."
    )
    # send plain help text (no HTML parsing needed here)
    await msg.answer(help_text, reply_markup=main_kb)
    # then show inline menu (separate message)
    await msg.answer("Menu:", reply_markup=main_menu_markup())

@dp.message(F.text == "/quiz")
async def cmd_quiz(msg: types.Message):
    await send_question(msg.chat.id)

# -------------------------
# /view handler (view a chapter or list chapters)
# -------------------------
@dp.message(F.text.startswith("/view"))
async def cmd_view(msg: types.Message):
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) == 1:
        # list chapters
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
    # ensure FLAT is current
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
        await send_question(uid)
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
        st = state.setdefault(str(uid), {"asked": [], "current": None, "next_time": None, "score": 0})
        st["current"] = None
        st["next_time"] = None
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
    cur = state.get(uid, {}).get("current")
    if cur:
        is_ok, feedback = evaluate_answer(text, cur)
        # reply (feedback may contain HTML tags)
        await msg.answer(feedback, parse_mode="HTML", reply_markup=main_kb)
        if is_ok:
            st = state.setdefault(uid, {"asked": [], "current": None, "next_time": None, "score": 0})
            st["score"] = st.get("score", 0) + 1
        state[uid]["current"] = None
        save_state(state)
        await asyncio.sleep(1.2)
        await send_question(msg.chat.id)
        return

    # no active question
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
    load_ltc_from_py()
    while True:
        try:
            load_ltc_from_py()
            now = datetime.now()
            for uid, info in list(state.items()):
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
                    await send_question(uid)
            await asyncio.sleep(RELOAD_CHECK_SECONDS)
        except Exception as e:
            logger.exception("Scheduler error: %s", e)
            await asyncio.sleep(5)

#--------reload tcp file----------
async def auto_reload_loop():
    while True:
        try:
            load_ltc_from_py()   # fayl o‘zgarsa avtomatik update bo‘ladi
        except Exception as e:
            print("Reload error:", e)
        await asyncio.sleep(3)  # har 3 soniyada tekshiradi


# ---------- startup ----------
async def main():
    if not BOT_TOKEN:
        print("TOKEN kiritilmagan!")
        return
    asyncio.create_task(scheduler_loop())
    asyncio.create_task(auto_reload_loop()) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
