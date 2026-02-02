import aiosqlite
import os

# Baza fayli manzili
DB_PATH = "database.db"

async def init_db():
    """Bazani va jadvallarni yaratish"""
    async with aiosqlite.connect(DB_PATH) as conn:
        # Users jadvali: ism, soatbay haq, soliq va ish kunlarini saqlaydi
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT DEFAULT 'User',
                hourly_rate REAL DEFAULT 12500,
                tax_rate REAL DEFAULT 3.3,
                work_days TEXT DEFAULT '월,화,수,목,금,토,일'
            )
        """)
        # Work_logs jadvali: har kungi ish soatlarini saqlaydi
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                work_date TEXT,
                hours REAL,
                UNIQUE(user_id, work_date) 
            )
        """)
        await conn.commit()

async def get_user_full_info(user_id):
    """Foydalanuvchining barcha sozlamalarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT name, hourly_rate, tax_rate, work_days FROM users WHERE user_id = ?", 
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                # Agar foydalanuvchi bazada bo'lmasa, yangi yaratamiz (default qiymatlar bilan)
                await db.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                await db.commit()
                return "User", 12500, 3.3, "월,화,수,목,금,토,일"
            return row

async def get_user_settings(user_id):
    """Faqat shartli hisob-kitob uchun kerakli (rate va tax) ma'lumotlarni olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT hourly_rate, tax_rate FROM users WHERE user_id = ?", 
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return 12500, 3.3
            return row

async def update_user_rate(user_id, new_rate):
    """Soatlik to'lovni yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET hourly_rate = ? WHERE user_id = ?",
            (new_rate, user_id)
        )
        await db.commit()

async def update_user_tax(user_id, new_tax):
    """Soliq stavkasini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET tax_rate = ? WHERE user_id = ?",
            (new_tax, user_id)
        )
        await db.commit()

async def update_work_days(user_id, work_days_str):
    """Ish kunlarini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET work_days = ? WHERE user_id = ?",
            (work_days_str, user_id)
        )
        await db.commit()