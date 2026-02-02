from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

# Pastki doimiy tugmalar
def main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="내 정보")]
        ],
        resize_keyboard=True
    )

# 1. Asosiy Inline menyu
def main_menu_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 내 근무표", callback_data="view_report"))
    builder.row(InlineKeyboardButton(text="✏️ 근무표 수정", callback_data="edit_logs"))
    builder.row(InlineKeyboardButton(text="⚙️ 설정", callback_data="settings"))
    return builder.as_markup()

# 2. Sozlamalar menyusi
def settings_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💰 시급 수정", callback_data="edit_rate"))
    builder.row(InlineKeyboardButton(text="📉 세금 수정", callback_data="edit_tax"))
    builder.row(InlineKeyboardButton(text="📅 근무요일 수정", callback_data="edit_workdays"))
    builder.row(InlineKeyboardButton(text="⬅️ 메인으로", callback_data="main_menu"))
    return builder.as_markup()

# 3. Hafta kunlarini tanlash (Checkbutton uslubida)
def weekdays_inline(selected_days_list):
    days = ["월", "화", "수", "목", "금", "토", "일"]
    builder = InlineKeyboardBuilder()
    for d in days:
        status = "✅" if d in selected_days_list else "❌"
        builder.button(text=f"{d} {status}", callback_data=f"toggle_day_{d}")
    builder.adjust(4, 3)
    builder.row(InlineKeyboardButton(text="💾 저장 완료", callback_data="save_settings"))
    builder.row(InlineKeyboardButton(text="⬅️ 메인으로", callback_data="main_menu"))
    return builder.as_markup()

# 4. Kunlarni tahrirlash uchun inline keyboard (oyning kunlari)
def edit_days_inline():
    """Oyning kunlarini 7x5 formatda ko'rsatish"""
    builder = InlineKeyboardBuilder()
    
    # Joriy oy va yilni olish
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Oyning oxirgi kunini aniqlash
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    from datetime import timedelta
    last_day = (next_month - timedelta(days=1)).day
    
    # Kunlarni qo'shish (7 tadan 5 qator)
    current_day = now.day
    buttons = []
    
    for day in range(1, last_day + 1):
        # Joriy kunni belgilash
        if day == current_day:
            text = f"📍 {day}"
        else:
            text = str(day)
        
        buttons.append(InlineKeyboardButton(
            text=text, 
            callback_data=f"edit_day_{day}"
        ))
    
    # 7 tadan guruplash
    for i in range(0, len(buttons), 7):
        builder.row(*buttons[i:i+7])
    
    # Orqaga qaytish tugmasi
    builder.row(InlineKeyboardButton(text="⬅️ 메인으로", callback_data="main_menu"))
    
    return builder.as_markup()

# 5. Soatlarni tanlash uchun inline keyboard
def select_hours_inline(day):
    """Oddiy soat variantlari va qo'lda kiritish"""
    builder = InlineKeyboardBuilder()
    
    # Standart soatlar
    standard_hours = [10,10.5,11]
    for hours in standard_hours:
        builder.button(
            text=f"{hours}시간", 
            callback_data=f"save_{day}_{hours}"
        )
    
    builder.adjust(3, 2)  # 3+2 formatda
    
    # Qo'lda kiritish va orqaga
    builder.row(
        InlineKeyboardButton(text="⌨️ 직접 입력", callback_data=f"manual_edit_{day}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ 뒤로", callback_data="edit_logs")
    )
    
    return builder.as_markup()

# 6. Tasdiqlash uchun inline keyboard
def confirm_inline(action, value=None):
    """Umumiy tasdiqlash tugmalari"""
    builder = InlineKeyboardBuilder()
    
    if value:
        callback_yes = f"confirm_{action}_{value}"
    else:
        callback_yes = f"confirm_{action}"
    
    builder.row(
        InlineKeyboardButton(text="✅ 예", callback_data=callback_yes),
        InlineKeyboardButton(text="❌ 아니오", callback_data="main_menu")
    )
    
    return builder.as_markup()