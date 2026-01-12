"""
GIT CHEAT SHEET
Holatlar:
1) SAYT HAQIQAT (GitHub ustun)
2) LOCAL HAQIQAT (kompyuter ustun)
3) IKKALASI HAM MUHIM (conflict bilan)
"""

# ===============================
# 1️⃣ SAYT HAQIQAT (LOCALNI TASHLAYSAN)
# ===============================

"""
Bu holat qachon?
- GitHub'dagi kod to‘g‘ri
- Local buzilgan
- Local o‘zgarishlar kerak emas
"""

"""
$ git fetch origin
# GitHub'dagi eng oxirgi holatni olib keladi (lekin qo‘llamaydi)

$ git reset --hard origin/main
# LOCALNI TO‘LIQ O‘CHIRIB
# GitHub holatiga 1:1 qilib qo‘yadi

⚠️ OG'OHLANTIRISH:
Localdagi HAMMA o‘zgarish YO‘QOLADI
"""

# ===============================
# 2️⃣ LOCAL HAQIQAT (SAYTNI BOSIB KETASAN)
# ===============================

"""
Bu holat qachon?
- Local kod to‘g‘ri
- GitHub'dagi kod xato
- Localni majburan yuklamoqchisan
"""

"""
$ git add .
# Barcha fayllarni qo‘shadi

$ git commit -m "local is truth"
# Local o‘zgarishni saqlaydi

$ git push --force origin main
# GitHub'dagi kodni MAJBURAN almashtiradi

⚠️ OG'OHLANTIRISH:
GitHub'dagi eski commitlar YO‘QOLADI
"""

# ===============================
# 3️⃣ IKKALASI HAM MUHIM (CONFLICT)
# ===============================

"""
Bu holat qachon?
- GitHub'da ham o‘zgarish bor
- Localda ham o‘zgarish bor
- IKKALASI HAM KERAK
"""

"""
$ git pull origin main
# GitHub + Localni birlashtirmoqchi bo‘ladi
# Agar bir xil joy o‘zgargan bo‘lsa → CONFLICT chiqadi
"""

"""
CONFLICT chiqqanda fayl ichi shunday bo‘ladi:

<<<<<<< HEAD
olma
o‘rik
=======
olma
olcha
>>>>>>> origin/main
"""

"""
NIMA QILASAN?
- <<<<<<< HEAD  → LOCAL qismi
- =======       → ajratuvchi
- >>>>>>>       → GITHUB qismi

KERAKLISINI QOLDIRASAN
KERAKSIZINI O‘CHIRASAN
BELGILARNI HAM O‘CHIRASAN
"""

"""
MASALAN IKKALASI HAM KERAK BO‘LSA:

olma
o‘rik
olcha
"""

"""
KEYIN:

$ git add fruits.txt
# Conflict hal bo‘lganini aytasan

$ git commit -m "resolve conflict fruits.txt"
# Kelishuvni saqlaysan

$ git push
# GitHub'ga yuborasan
"""

# ===============================
# 4️⃣ VAQTINCHA SAQLAB TURISH (STASH)
# ===============================

"""
Bu holat qachon?
- Localda yarim ish bor
- Pull qilish kerak
- Hozir commit qilging kelmaydi
"""

"""
$ git stash
# Local o‘zgarishni yashirib turadi

$ git pull
# GitHub kodini olasan

$ git stash pop
# Yashirilgan o‘zgarishni qaytaradi
"""

# ===============================
# 5️⃣ TEZ TEKSHIRUV KOMANDALARI
# ===============================

"""
$ git status
# Hozirgi holat

$ git log --oneline --graph --all
# Kim qachon nima qilganini ko‘rish

$ git diff
# O‘zgarishlarni ko‘rish
"""

# ===============================
# ASL SABOQ
# ===============================

"""
❌ BOT ICHIDAN git pull + restart XAVFLI
✅ Avval terminalda tekshir, keyin botga qo‘sh
"""
