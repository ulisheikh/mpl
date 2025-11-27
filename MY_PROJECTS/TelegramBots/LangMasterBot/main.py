# bot/main.py
# Minimal runnable Aiogram 3 bot skeleton with a few demo handlers:
# - /start
# - /get_dict <path>   -> fetch a file from GitHub repo (if configured)
# - /update_dict <path> -> update file on GitHub with provided JSON (admin-only demo)
#
# Usage:
#   python -m bot.main
#
import asyncio
import json
from aiogram import types
from aiogram import Bot
from aiogram.fsm.context import FSMContext

from .loader import dp, bot, logger
from .config import config
from .states import StartStates, EditDictStates, AdminStates
from .github_api import github_api

# Simple in-memory admin list (replace with real admin/user DB)
ADMINS = { }  # put telegram user ids here as integers: {123456789}

# ---------- handlers ----------
async def cmd_start(message: types.Message, state: FSMContext):
    """Start handler: greet and ask for language selection (simple demo)."""
    await state.clear()
    text = (
        "Assalomu alaykum! 👋\n"
        "LangMaster Botga xush kelibsiz.\n\n"
        " /get_dict <path> - GitHubdagi faylni o'qish (masalan: languages/korean/dict.json)\n"
        " /update_dict <path> - GitHubdagi faylni yangilash (admin only)\n\n"
        "Agar GitHub sozlanmagan bo'lsa, shunchaki local ishlatishingiz mumkin."
    )
    await message.answer(text)
    await StartStates.choosing_language.set()

async def get_dict_handler(message: types.Message):
    """Usage: /get_dict languages/korean/dict.json
    Fetches the file from GitHub (if repo configured) and sends content (up to telegram limits).
    """
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Iltimos fayl yo'lini kiriting. Masalan:\n/get_dict languages/korean/dict.json")
        return
    path = parts[1].strip()
    try:
        if not config.GITHUB_REPO:
            await message.reply("GitHub repository sozlanmagan (GITHUB_REPO env).")
            return
        data = await github_api.get_file(path)
        content = data.get("content", "")
        # Try to pretty-print JSON if possible
        try:
            parsed = json.loads(content)
            pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
            if len(pretty) > 3500:
                # If large, send as a file
                await message.answer_document(types.InputFile.from_bytes(pretty.encode("utf-8"), filename=path.split("/")[-1]))
            else:
                await message.reply(f"<pre>{pretty}</pre>")
        except Exception:
            # not JSON, send raw
            if len(content) > 3500:
                await message.answer_document(types.InputFile.from_bytes(content.encode("utf-8"), filename=path.split("/")[-1]))
            else:
                await message.reply(f"<pre>{content}</pre>")
    except Exception as e:
        logger.exception("get_dict error")
        await message.reply(f"Xatolik: {e}")

async def update_dict_handler(message: types.Message):
    """
    Demo update (admin-only).
    Usage:
      /update_dict languages/korean/dict.json
    Then bot will ask to send new JSON content (stateful).
    """
    if message.from_user.id not in ADMINS:
        await message.reply("Bu buyruq faqat adminlar uchun.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Fayl yo'lini kiriting: /update_dict languages/korean/dict.json")
        return
    path = parts[1].strip()
    # store path in FSM and ask for content
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(EditDictStates.waiting_for_value)
    await state.update_data(target_path=path)
    await message.reply("Yangi fayl kontentini JSON formatda yuboring. (Kichik o'zgartirish uchun ham to'liq faylni yuboring)")

async def on_new_json_content(message: types.Message, state: FSMContext):
    """Receive new JSON content and push to GitHub (admin-only)."""
    if message.from_user.id not in ADMINS:
        await message.reply("Bu amaliyot faqat adminlar uchun.")
        await state.clear()
        return

    data = await state.get_data()
    path = data.get("target_path")
    if not path:
        await message.reply("Hech qanday target_path topilmadi. /update_dict bilan boshlang.")
        await state.clear()
        return

    text = message.text
    # Validate JSON
    try:
        parsed = json.loads(text)
    except Exception as e:
        await message.reply(f"JSON parsida xatolik: {e}\nIltimos to'g'ri JSON yuboring.")
        return

    # fetch current sha
    try:
        remote = await github_api.get_file(path)
        sha = remote.get("sha")
    except Exception as e:
        # If file not found, create it
        sha = None

    new_content = json.dumps(parsed, ensure_ascii=False, indent=2)
    try:
        if sha:
            res = await github_api.update_file(path=path, new_content=new_content, sha=sha, message=f"Update by bot user {message.from_user.id}")
        else:
            res = await github_api.create_file(path=path, new_content=new_content, message=f"Create by bot user {message.from_user.id}")
        await message.reply("Fayl GitHubga muvaffaqiyatli yuklandi.")
    except Exception as e:
        await message.reply(f"GitHubga yuklashda xatolik: {e}")
    finally:
        await state.clear()

# ---------- register handlers ----------
def register_handlers():
    dp.message.register(cmd_start, commands=["start", "help"])
    dp.message.register(get_dict_handler, commands=["get_dict"])
    dp.message.register(update_dict_handler, commands=["update_dict"])
    # handler to receive new json content while in EditDictStates.waiting_for_value
    dp.message.register(on_new_json_content, EditDictStates.waiting_for_value)

# ---------- run ----------
async def main():
    register_handlers()
    logger.info("Bot started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
