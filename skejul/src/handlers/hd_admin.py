from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite
from datetime import datetime
from src.database import db
from src.keyboards import kbd, kbd_admin

admin_router = Router()

class AdminForm(StatesGroup):
    admin_edit_rate = State()
    admin_edit_tax = State()
    admin_manual_hours = State()

# Hafta kunini olish
def get_weekday_korean(date_obj):
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return weekdays[date_obj.weekday()]

# --- MAXFIY ADMIN KOMANDA ---
@admin_router.message(F.text == "/my_users")
async def admin_panel(message: Message):
    """Maxfiy admin panel - faqat admin ko'radi"""
    if not db.is_admin(message.from_user.id):
        # Oddiy foydalanuvchi uchun xech narsa ko'rsatilmaydi
        return
    
    await message.answer(
        "🔐 관리자 패널\n\n선택하세요:",
        reply_markup=kbd_admin.admin_main_menu()
    )

@admin_router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery):
    """Admin panelga qaytish"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    await callback.message.edit_text(
        "🔐 관리자 패널\n\n선택하세요:",
        reply_markup=kbd_admin.admin_main_menu()
    )

# --- FOYDALANUVCHILAR RO'YXATI ---
@admin_router.callback_query(F.data == "admin_users")
async def show_users_list(callback: CallbackQuery):
    """Barcha foydalanuvchilar ro'yxati"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    users = await db.get_all_users()
    
    if not users:
        await callback.message.edit_text(
            "📋 등록된 사용자가 없습니다.",
            reply_markup=kbd_admin.admin_main_menu()
        )
        return
    
    text = f"👥 사용자 목록 ({len(users)}명)\n\n사용자를 선택하세요:"
    
    await callback.message.edit_text(
        text,
        reply_markup=kbd_admin.admin_users_list(users)
    )

# --- TANLANGAN FOYDALANUVCHI ---
@admin_router.callback_query(F.data.startswith("admin_user_"))
async def show_user_menu(callback: CallbackQuery):
    """Foydalanuvchi menyusi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    user_id = int(callback.data.split("_")[-1])
    
    # Foydalanuvchi ma'lumotlari
    async with aiosqlite.connect(db.DB_PATH) as conn:
        async with conn.execute(
            "SELECT full_name, username, hourly_rate, tax_rate, work_days FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            user_data = await cursor.fetchone()
    
    if not user_data:
        await callback.answer("❌ 사용자를 찾을 수 없습니다.")
        return
    
    full_name, username, hourly_rate, tax_rate, work_days = user_data
    display_name = full_name if full_name else (username if username else f"User {user_id}")
    
    text = f"""👤 {display_name}

🔢 ID: {user_id}
🆔 사용자명: @{username if username else '없음'}

⚙️ 설정
💰 시급: {hourly_rate:,}원
📉 세금: {tax_rate}%
📅 근무요일: {work_days}

원하는 작업을 선택하세요:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=kbd_admin.admin_user_menu(user_id)
    )
    
    # Admin action log
    await db.log_admin_action(
        callback.from_user.id,
        "view_user",
        user_id,
        f"Viewed user profile"
    )

# --- FOYDALANUVCHI HISOBOTINI KO'RISH ---
@admin_router.callback_query(F.data.startswith("admin_view_"))
async def admin_view_report(callback: CallbackQuery):
    """Admin foydalanuvchining hisobotini ko'radi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    user_id = int(callback.data.split("_")[-1])
    now = datetime.now()
    current_month = now.strftime('%Y-%m')

    async with aiosqlite.connect(db.DB_PATH) as conn:
        async with conn.execute("""
            SELECT work_date, hours FROM work_logs 
            WHERE user_id = ? AND work_date LIKE ?
            ORDER BY work_date ASC
        """, (user_id, f"{current_month}%")) as c:
            rows = await c.fetchall()
        
        async with conn.execute("""
            SELECT hourly_rate, tax_rate, full_name FROM users WHERE user_id = ?
        """, (user_id,)) as c:
            settings = await c.fetchone()
            hourly_rate = settings[0] if settings else 12500
            tax_rate = settings[1] if settings else 3.3
            full_name = settings[2] if settings and settings[2] else f"User {user_id}"

    if not rows:
        text = f"👤 {full_name}\n📅 {now.month}월 근무 기록이 없습니다."
    else:
        report_lines = [f"👤 {full_name}\n📅 {now.month}월 근무 상세 기록\n"]
        total_month_hours = 0
        
        for date_str, hours in rows:
            day_only = date_str.split('-')[-1]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = get_weekday_korean(date_obj)
            
            if hours == 0:
                report_lines.append(f"▫️ {day_only}일 ({weekday}): 🏖 휴무")
            else:
                report_lines.append(f"▫️ {day_only}일 ({weekday}): {hours}시간")
                total_month_hours += hours
        
        gross_pay = total_month_hours * hourly_rate
        tax_amount = gross_pay * (tax_rate / 100)
        net_pay = gross_pay - tax_amount
        
        report_lines.append(f"\n━━━━━━━━━━━━━━")
        report_lines.append(f"⏱ 총 근무시간: {total_month_hours}시간")
        report_lines.append(f"💰 세전 급여: {gross_pay:,.0f}원")
        report_lines.append(f"📉 세금 ({tax_rate}%): {tax_amount:,.0f}원")
        report_lines.append(f"💵 실수령액: {net_pay:,.0f}원")

        text = "\n".join(report_lines)

    await callback.message.edit_text(
        text,
        reply_markup=kbd_admin.admin_user_menu(user_id),
        parse_mode=None
    )

# --- FOYDALANUVCHI KUNDALIGINI TAHRIRLASH ---
@admin_router.callback_query(F.data.startswith("admin_edit_"))
async def admin_edit_calendar(callback: CallbackQuery):
    """Admin foydalanuvchi uchun kalendar ko'rsatadi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    user_id = int(callback.data.split("_")[-1])
    now = datetime.now()
    
    # User name
    async with aiosqlite.connect(db.DB_PATH) as conn:
        async with conn.execute(
            "SELECT full_name, username FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            user_data = await cursor.fetchone()
    
    full_name = user_data[0] if user_data and user_data[0] else (user_data[1] if user_data and user_data[1] else f"User {user_id}")
    
    await callback.message.edit_text(
        f"👤 {full_name}\n📅 {now.year}년 {now.month}월\n\n수정할 날짜를 선택하세요:",
        reply_markup=kbd_admin.admin_calendar_inline(user_id)
    )

@admin_router.callback_query(F.data.startswith("admin_day_"))
async def admin_select_day(callback: CallbackQuery):
    """Admin kun tanlaganda soatlarni ko'rsatish"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[2])
    day = parts[3]
    
    now = datetime.now()
    selected_date = datetime(now.year, now.month, int(day))
    weekday = get_weekday_korean(selected_date)
    
    await callback.message.edit_text(
        f"📍 {now.month}월 {day}일 ({weekday})\n근무 시간을 선택하세요:",
        reply_markup=kbd_admin.admin_hours_inline(user_id, day)
    )

@admin_router.callback_query(F.data.startswith("admin_save_"))
async def admin_save_hours(callback: CallbackQuery):
    """Admin foydalanuvchi uchun soatlarni saqlaydi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[2])
    day = parts[3]
    hours = float(parts[4])
    
    work_date = datetime.now().strftime(f"%Y-%m-{int(day):02d}")

    async with aiosqlite.connect(db.DB_PATH) as conn:
        await conn.execute("""
            INSERT INTO work_logs (user_id, work_date, hours) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, work_date) DO UPDATE SET hours = excluded.hours
        """, (user_id, work_date, hours))
        await conn.commit()

    # Log admin action
    await db.log_admin_action(
        callback.from_user.id,
        "edit_hours",
        user_id,
        f"Set {day}일 to {hours} hours"
    )

    if hours == 0:
        await callback.answer(f"✅ {day}일 휴무로 저장되었습니다!")
    else:
        await callback.answer(f"✅ {day}일 {hours}시간 저장완료!")
    
    await callback.message.edit_text(
        "다른 날짜를 선택하세요:",
        reply_markup=kbd_admin.admin_calendar_inline(user_id)
    )

# --- ADMIN SOZLAMALARNI O'ZGARTIRISH ---
@admin_router.callback_query(F.data.startswith("admin_settings_"))
async def admin_settings(callback: CallbackQuery):
    """Foydalanuvchi sozlamalarini o'zgartirish menyusi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    user_id = int(callback.data.split("_")[-1])
    
    await callback.message.edit_text(
        "⚙️ 설정 변경\n\n변경할 항목을 선택하세요:",
        reply_markup=kbd_admin.admin_settings_menu(user_id)
    )

@admin_router.callback_query(F.data.startswith("admin_rate_"))
async def admin_edit_rate(callback: CallbackQuery, state: FSMContext):
    """Admin soatlik to'lovni o'zgartiradi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(target_user_id=user_id)
    
    await callback.message.answer("💰 새로운 시급을 입력하세요 (예: 12500):")
    await state.set_state(AdminForm.admin_edit_rate)

@admin_router.message(AdminForm.admin_edit_rate)
async def process_admin_rate(message: Message, state: FSMContext):
    if not db.is_admin(message.from_user.id):
        return
    
    try:
        new_rate = float(message.text.replace(',', '').replace('원', '').strip())
        data = await state.get_data()
        user_id = data['target_user_id']
        
        await db.update_user_rate(user_id, new_rate)
        
        # Log
        await db.log_admin_action(
            message.from_user.id,
            "change_rate",
            user_id,
            f"Changed hourly rate to {new_rate}"
        )
        
        await message.answer(
            f"✅ 시급이 {new_rate:,}원으로 변경되었습니다!",
            reply_markup=kbd_admin.admin_user_menu(user_id)
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ 올바른 숫자를 입력해주세요.")

# --- UMUMIY STATISTIKA ---
@admin_router.callback_query(F.data == "admin_stats")
async def show_all_stats(callback: CallbackQuery):
    """Barcha foydalanuvchilarning statistikasi"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("❌ 권한이 없습니다.")
        return
    
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    
    users = await db.get_all_users()
    
    if not users:
        await callback.message.edit_text(
            "📊 통계가 없습니다.",
            reply_markup=kbd_admin.admin_main_menu()
        )
        return
    
    # report_lines = [f"📊 전체 통계 ({now.month}월)\n"]
    total_all_hours = 0
    total_all_pay = 0
    
    for user in users:
        user_id = user[0]
        full_name = user[2] if user[2] else (user[3] if user[3] else f"User {user_id}")
        
        stats = await db.get_user_stats(user_id, current_month)
        
        # report_lines.append(f"\n👤 {full_name}")
        # report_lines.append(f"   ⏱ {stats['total_hours']}시간")
        # report_lines.append(f"   💵 {stats['net_pay']:,.0f}원")
        
        total_all_hours += stats['total_hours']
        total_all_pay += stats['net_pay']
    
    # report_lines.append(f"\n━━━━━━━━━━━━━━")
    # report_lines.append(f"⏱ 총 근무시간: {total_all_hours}시간")
    # report_lines.append(f"💰 총 지급액: {total_all_pay:,.0f}원")
    
    # text = "\n".join(report_lines)
    
    await callback.message.edit_text(
        # text,
        reply_markup=kbd_admin.admin_main_menu(),
        parse_mode=None
    )