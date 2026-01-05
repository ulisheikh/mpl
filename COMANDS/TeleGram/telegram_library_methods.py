# ==============================
#  TELETHON KUTUBXONASI
# ==============================

from telethon.sync import TelegramClient, types

# TelegramClient: Asosiy klient obyekti yaratish
client = TelegramClient('session_name', api_id, api_hash)

# 🔘 KeyboardButton - Tugma yaratish
# Telegram xabarlari uchun tugma yaratadi
button = types.KeyboardButton('Click me')

# 🧩 ReplyKeyboardMarkup - Tugma joylashtirish
# Yaratilgan tugmalarni xabarda joylashtiradi
keyboard = types.ReplyKeyboardMarkup([[button]])

# 📩 send_message() - Xabar yuborish
# Telegram hisobiga xabar yuboradi
client.send_message('username', 'Hello!')

# 📰 get_messages() - Xabarlarni olish
# Guruhdagi yoki shaxsiy yozishmalarni oladi
messages = client.get_messages('group_name', limit=10)
for message in messages:
    print(message.text)


# ==============================
#  PYROGRAM KUTUBXONASI
# ==============================

from pyrogram import Client, types

# Client: Pyrogram klient obyekti yaratish
app = Client("my_account", api_id, api_hash)

# 🔘 InlineKeyboardButton - Tugma yaratish
# Inline tugma yaratadi
button = types.InlineKeyboardButton('Click me', callback_data='click')

# 🧩 InlineKeyboardMarkup - Tugma joylashtirish
# Inline tugmalarni xabarda joylashtiradi
keyboard = types.InlineKeyboardMarkup([[button]])

# 📩 send_message() - Xabar yuborish
# Telegram hisobiga xabar yuboradi
app.send_message('username', 'Hello!')

# 👥 get_chat_members() - Guruh a'zolarini olish
# Guruhdagi barcha a'zolarni oladi
members = app.get_chat_members('group_name')
for member in members:
    print(member.user.first_name)


# ==============================
#  AIOGRAM KUTUBXONASI
# ==============================

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

# Bot: Aiogram bot obyekti yaratish
bot = Bot(token='YOUR_TOKEN')

# Dispatcher: Handlerlarni boshqarish
dp = Dispatcher(bot)

# 🔘 InlineKeyboardButton - Tugma yaratish
# Inline tugma yaratadi
button = InlineKeyboardButton('Click me', callback_data='click')

# 🧩 InlineKeyboardMarkup - Tugma joylashtirish
# Inline tugmalarni xabarda joylashtiradi
keyboard = InlineKeyboardMarkup([[button]])

# 📩 send_message() - Xabar yuborish
# Telegram hisobiga xabar yuboradi
await bot.send_message(chat_id='username', text='Hello!')

# 📝 register_message_handler() - Handlerni ro‘yxatdan o‘tkazish
# Xabarlarni ushlash uchun handlerlarni ro‘yxatdan o‘tkazadi
@dp.message_handler()
async def handler(message: types.Message):
    print(f"New message: {message.text}")


# ==============================
#  TGCRYPTO KUTUBXONASI
# ==============================

import tgcrypto

# 🔒 AESModeECB - Shifrlash
# ECB rejimida ma'lumotni shifrlaydi
aes = tgcrypto.AESModeECB(key)

# 🔓 AESModeCBC - Shifrlash
# CBC rejimida ma'lumotni shifrlaydi
aes = tgcrypto.AESModeCBC(key, iv)

# 📦 encrypt() - Shifrlash
# Ma'lumotni shifrlaydi
encrypted_data = aes.encrypt(data)

# 📥 decrypt() - Deshifrlash
# Shifrlangan ma'lumotni deshifrlaydi
decrypted_data = aes.decrypt(data)


# ==============================
#  PENTESTING METHODS
# ==============================

# Telethon: Guruhdagi yoki shaxsiy yozishmalarni olish
client.get_messages('group_name')

# Pyrogram: Guruh a'zolarini olish
app.get_chat_members('group_id')

# Aiogram: Xabar yuborish
bot.send_message(chat_id, 'message')

