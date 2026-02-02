import asyncio
import sys
import aiosqlite
from pathlib import Path
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Loyiha yo'lini sozlash (importlar xato bermasligi uchun)
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils.config import BOT_TOKEN
from src.handlers import hd
from src.database import db
import src.keyboards.kbd as kbd

async def send_morning_reminder(bot: Bot):
    """Har kuni 05:00 da barcha foydalanuvchilarga eslatma yuborish"""
    try:
        async with aiosqlite.connect(db.DB_PATH) as conn:
            async with conn.execute("SELECT user_id FROM users") as cursor:
                users = await cursor.fetchall()
                
        for user in users:
            try:
                await bot.send_message(
                    user[0], 
                    "☀️ 좋은 아침입니다!\n오늘도 업무 기록을 잊지 마세요!",
                    reply_markup=kbd.main_menu_inline(),
                    parse_mode=None
                )
            except Exception:
                continue  # Botni bloklagan foydalanuvchilarni o'tkazib yuboradi
    except Exception as e:
        print(f"Eslatma yuborishda xato: {e}")

async def main():
    # Ma'lumotlar bazasini ishga tushirish
    await db.init_db()
    
    # Botni sozlash
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(hd.router)

    # Scheduler (Koreya vaqti bilan 05:00)
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(send_morning_reminder, "cron", hour=5, minute=0, args=[bot])
    scheduler.start()

    print("--- 봇이 시작되었습니다 (Korea Time Zone) ---")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi")