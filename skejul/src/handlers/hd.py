from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite
from datetime import datetime
from src.database import db
from src.keyboards import kbd

router = Router()

class Form(StatesGroup):
    edit_manual_day = State()
    edit_rate = State()
    edit_tax = State()

# --- START VA ASOSIY MENYU ---
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "원하시는 메뉴를 선택해주세요:", 
        reply_markup=kbd.main_menu_inline()
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "원하시는 메뉴를 선택해주세요:", 
        reply_markup=kbd.main_menu_inline()
    )

# --- SOZLAMALAR MENYUSI ---
@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    name, hourly_rate, tax_rate, work_days = await db.get_user_full_info(user_id)
    
    text = f"""⚙️ 현재 설정

💰 시급: {hourly_rate:,}원
📉 세금: {tax_rate}%
📅 근무요일: {work_days}

수정할 항목을 선택하세요:
"""
    await callback.message.edit_text(text, reply_markup=kbd.settings_inline(), parse_mode=None)

# --- SOATLIK TO'LOVNI TAHRIRLASH ---
@router.callback_query(F.data == "edit_rate")
async def edit_rate_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 새로운 시급을 입력하세요 (예: 12500):")
    await state.set_state(Form.edit_rate)

@router.message(Form.edit_rate)
async def process_edit_rate(message: Message, state: FSMContext):
    try:
        new_rate = float(message.text.replace(',', '').replace('원', '').strip())
        user_id = message.from_user.id
        
        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute(
                "UPDATE users SET hourly_rate = ? WHERE user_id = ?",
                (new_rate, user_id)
            )
            await conn.commit()
        
        await message.answer(
            f"✅ 시급이 {new_rate:,}원으로 변경되었습니다!",
            reply_markup=kbd.main_menu_inline()
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ 올바른 숫자를 입력해주세요.")

# --- SOLIQNI TAHRIRLASH ---
@router.callback_query(F.data == "edit_tax")
async def edit_tax_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📉 새로운 세금율을 입력하세요 (예: 3.3):")
    await state.set_state(Form.edit_tax)

@router.message(Form.edit_tax)
async def process_edit_tax(message: Message, state: FSMContext):
    try:
        new_tax = float(message.text.replace(',', '.').replace('%', '').strip())
        user_id = message.from_user.id
        
        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute(
                "UPDATE users SET tax_rate = ? WHERE user_id = ?",
                (new_tax, user_id)
            )
            await conn.commit()
        
        await message.answer(
            f"✅ 세금율이 {new_tax}%로 변경되었습니다!",
            reply_markup=kbd.main_menu_inline()
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ 올바른 숫자를 입력해주세요.")

# --- ISH KUNLARINI TAHRIRLASH ---
@router.callback_query(F.data == "edit_workdays")
async def edit_workdays_start(callback: CallbackQuery):
    user_id = callback.from_user.id
    name, hourly_rate, tax_rate, work_days = await db.get_user_full_info(user_id)
    selected_days = work_days.split(',') if work_days else []
    
    await callback.message.edit_text(
        "📅 근무하는 요일을 선택하세요:",
        reply_markup=kbd.weekdays_inline(selected_days)
    )

@router.callback_query(F.data.startswith("toggle_day_"))
async def toggle_workday(callback: CallbackQuery):
    user_id = callback.from_user.id
    day = callback.data.split("_")[-1]
    
    name, hourly_rate, tax_rate, work_days = await db.get_user_full_info(user_id)
    selected_days = work_days.split(',') if work_days else []
    
    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)
    
    new_work_days = ','.join(selected_days)
    
    async with aiosqlite.connect(db.DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET work_days = ? WHERE user_id = ?",
            (new_work_days, user_id)
        )
        await conn.commit()
    
    await callback.message.edit_reply_markup(
        reply_markup=kbd.weekdays_inline(selected_days)
    )
    await callback.answer()

@router.callback_query(F.data == "save_settings")
async def save_workdays(callback: CallbackQuery):
    await callback.answer("✅ 저장되었습니다!")
    await callback.message.edit_text(
        "원하시는 메뉴를 선택해주세요:",
        reply_markup=kbd.main_menu_inline()
    )

# --- KUNLIK TAHRIRLASH ---
@router.callback_query(F.data == "edit_logs")
async def show_calendar(callback: CallbackQuery):
    now = datetime.now()
    await callback.message.edit_text(
        f"📅 {now.month}월 - 수정할 날짜를 선택하세요:", 
        reply_markup=kbd.edit_days_inline()
    )

@router.callback_query(F.data.startswith("edit_day_"))
async def select_day(callback: CallbackQuery):
    day = callback.data.split("_")[-1]
    await callback.message.edit_text(
        f"📍 {day}일 근무 시간을 선택하세요:", 
        reply_markup=kbd.select_hours_inline(day)
    )

# --- SAQLASH ---
@router.callback_query(F.data.startswith("save_"))
async def save_hours(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.answer("❌ 오류가 발생했습니다.")
        return
    
    _, day, hours = parts
    user_id = callback.from_user.id
    work_date = datetime.now().strftime(f"%Y-%m-{int(day):02d}")

    async with aiosqlite.connect(db.DB_PATH) as conn:
        await conn.execute("""
            INSERT INTO work_logs (user_id, work_date, hours) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, work_date) DO UPDATE SET hours = excluded.hours
        """, (user_id, work_date, float(hours)))
        await conn.commit()

    await callback.answer(f"✅ {day}일 {hours}시간 저장완료!")
    await callback.message.edit_text(
        "수정할 다른 날짜를 선택하세요:", 
        reply_markup=kbd.edit_days_inline()
    )

# --- MANUAL INPUT ---
@router.callback_query(F.data.startswith("manual_edit_"))
async def manual_input_start(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[-1]
    await state.update_data(editing_day=day)
    await callback.message.answer(f"⌨️ {day}일 근무 시간을 입력해주세요 (예: 9.5):")
    await state.set_state(Form.edit_manual_day)

@router.message(Form.edit_manual_day)
async def process_manual_input(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        day = data.get("editing_day")
        hours = float(message.text.replace(',', '.'))
        
        if hours < 0 or hours > 24:
            await message.answer("❌ 0-24 사이의 시간을 입력해주세요.")
            return
        
        user_id = message.from_user.id
        work_date = datetime.now().strftime(f"%Y-%m-{int(day):02d}")

        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute("""
                INSERT INTO work_logs (user_id, work_date, hours) 
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, work_date) DO UPDATE SET hours = excluded.hours
            """, (user_id, work_date, hours))
            await conn.commit()

        await message.answer(
            f"✅ {day}일 {hours}시간 저장완료!", 
            reply_markup=kbd.main_menu_inline()
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ 숫자만 입력해주세요.")

# --- VIEW REPORT ---
@router.callback_query(F.data == "view_report")
async def view_report(callback: CallbackQuery):
    user_id = callback.from_user.id
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
            SELECT hourly_rate, tax_rate FROM users WHERE user_id = ?
        """, (user_id,)) as c:
            settings = await c.fetchone()
            hourly_rate = settings[0] if settings else 12500
            tax_rate = settings[1] if settings else 3.3

    if not rows:
        text = f"📅 {now.month}월 근무 기록이 없습니다."
    else:
        report_lines = [f"📅 {now.month}월 근무 상세 기록\n"]
        total_month_hours = 0
        
        for date_str, hours in rows:
            day_only = date_str.split('-')[-1]
            report_lines.append(f"▫️ {day_only}일: {hours}시간")
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

    try:
        await callback.message.edit_text(
            text, 
            reply_markup=kbd.main_menu_inline(),
            parse_mode=None
        )
    except Exception:
        await callback.answer()
        await callback.message.answer(text, reply_markup=kbd.main_menu_inline(), parse_mode=None)

# --- USER INFO ---
@router.message(F.text == "내 정보")
async def user_info(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "없음"
    full_name = message.from_user.full_name
    
    name, hourly_rate, tax_rate, work_days = await db.get_user_full_info(user_id)
    
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    
    async with aiosqlite.connect(db.DB_PATH) as conn:
        async with conn.execute("""
            SELECT SUM(hours) FROM work_logs 
            WHERE user_id = ? AND work_date LIKE ?
        """, (user_id, f"{current_month}%")) as c:
            result = await c.fetchone()
            total_hours = result[0] if result[0] else 0

    text = f"""👤 내 정보

📱 이름: {full_name}

⚙️ 현재 설정
💰 시급: {hourly_rate:,}원
📉 세금: {tax_rate}%
📅 근무요일: {work_days}

-------------------------------------------
📊 이번 달
⏱ 총 근무시간: {total_hours}시간
💵 예상 실수령액: {(total_hours * hourly_rate * (1 - tax_rate/100)):,.0f}원
-------------------------------------------

"""
    
    await message.answer(text, parse_mode=None)