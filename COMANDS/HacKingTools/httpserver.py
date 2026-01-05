# Ajoyib, shunda men Python server + LocalTunnel + URL faylga yozish + Telegram orqali avtomatik yuborish hammasini birlashtirib, har bir qatorni izoh bilan yozib beraman. Shu bilan:

# Python server avtomatik ishga tushadi.

# LocalTunnel orqali internetga chiqadi.

# Public URL server_url.txt faylga yoziladi.

# Shu URL Telegram orqali sening telefoningga avtomatik keladi.
import os
import subprocess
import time
import requests

# -------------------------------
# Sozlamalar
PORT = 8000  # Python server ishlaydigan port
SUBDOMAIN = "myuniqueserver"  # LocalTunnel subdomain
OUTPUT_FILE = "server_url.txt"  # URL saqlanadigan fayl

# Telegram sozlamalari
TELEGRAM_BOT_TOKEN = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Bot token
TELEGRAM_CHAT_ID = "987654321"  # O'z chat ID
# -------------------------------

# 1️⃣ Python serverni ishga tushirish
print("Python server ishga tushmoqda...")
server_cmd = f"python -m http.server {PORT}"  # Python built-in server
server_process = subprocess.Popen(server_cmd, shell=True)  # Serverni subprocess orqali ishga tushurish

# 2️⃣ Biroz kutish, server tayyor bo‘lsin
time.sleep(2)

# 3️⃣ LocalTunnel ishga tushirish
print("LocalTunnel ishga tushmoqda...")
lt_cmd = f"lt --port {PORT} --subdomain {SUBDOMAIN}"  # LocalTunnel buyruq
lt_process = subprocess.Popen(lt_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # Outputni olish uchun PIPE qo‘shildi

# 4️⃣ URLni olish va faylga yozish
def get_url(process, output_file):
    """
    LocalTunnel terminal chiqishidan public URLni aniqlab,
    faylga yozadi va Telegramga yuboradi.
    """
    while True:
        line = process.stdout.readline()  # Terminal chiqishini qatorma-qator o‘qish
        if not line:
            break
        if "https://" in line:
            url = line.strip()  # URLni olish
            print(f"Public URL: {url}")
            
            # URLni faylga yozish
            with open(output_file, "w") as f:
                f.write(url)
            
            # URLni Telegramga yuborish
            send_telegram_message(url)
            break

# 5️⃣ Telegramga yuborish funksiyasi
def send_telegram_message(message):
    """
    Telegram bot orqali xabar yuborish.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": f"Server URL: {message}"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("URL Telegramga yuborildi!")
        else:
            print(f"Xatolik: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Telegramga yuborishda xatolik: {e}")

# URLni olish va tarqatish
get_url(lt_process, OUTPUT_FILE)

# 6️⃣ Serverni ishga tushurishda davom ettirish
server_process.wait()
lt_process.wait()

########################################################################################3


# Ha, xuddi Telegram kabi email orqali ham URL yuborish mumkin. Python’da buni qilish uchun odatda smtplib kutubxonasidan foydalaniladi. Shu bilan:

# Python server + LocalTunnel ishlaydi.

# Public URL server_url.txt faylga yoziladi.

# Shu URL email orqali o‘ziga yoki boshqa qurilmaga avtomatik yuboriladi.

# Misol: Email orqali yuborish
import smtplib
from email.mime.text import MIMEText

# Email sozlamalari
SMTP_SERVER = "smtp.gmail.com"      # Gmail SMTP server
SMTP_PORT = 587                      # TLS port
EMAIL_ADDRESS = "sizningemail@gmail.com"
EMAIL_PASSWORD = "app_password"      # Gmail App Password (two-factor bo‘lsa)

def send_email(url):
    msg = MIMEText(f"Server URL: {url}")   # Email matni
    msg["Subject"] = "Python Server URL"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = "qabul qiluvchi@email.com"

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # TLS orqali xavfsiz ulanish
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email yuborildi!")
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")

# Misol chaqirish
send_email("https://myuniqueserver.loca.lt")

# Muhim eslatmalar:

# Gmail ishlatayotgan bo‘lsang, “App Password” yaratish kerak (normal parol ishlamaydi, xavfsizlik sababli).

# SMTP orqali boshqa email xizmatlarini ham ishlatish mumkin (Outlook, Yahoo, ProtonMail va h.k.).

# Shu usulni oldingi skriptga qo‘shib, Telegram va Email bir vaqtda yuborish ham mumkin.