"""
TOKEN:

  8311185221:AAGgB0brk1SGmhyCVDIoPlKYn6Wce96FV_M

  LangMaster Bot — Project Specification (for VSCode)


1️⃣ LOYIHA MAQSADI

“LangMaster Bot” — bu foydalanuvchining o‘rganayotgan tillari bo‘yicha:
- shaxsiy lug‘atlarini
- grammatika ro‘yxatlarini
- mashq va testlarini
- audio / PDF / topshiriqlarni
- statistikasini
- va barcha jarayonni boshqarishni

avtomatlashtiriladigan, moslashtiriladigan, GitHub bilan bog‘langan universal
til o‘rganish bot.

Bot bir nechta rejimda ishlaydi:
- Global Mode → hamma foydalanuvchilarning umumiy lug‘ati bilan ishlaydi
- Local Mode → faqat o‘sha userning o‘z lug‘ati

Admin esa:
- barcha userlarni
- barcha tillar bo‘yicha statistikani
- fayllarni
- Global lug‘atni
- va bot faoliyatini to‘liq boshqara oladi.

2️⃣ ASOSIY FUNKSIYALAR

A. User taraf funksiyalari

1. Til tanlash
- Foydalanuvchi start bosadi → til tanlaydi
- Korean / English / Japanese / French / Custom

2. Lug‘at bilan ishlash
Global yoki Local mode tanlanadi
- Global dict (hammaga umumiy)
- Local dict (shaxsiy)

Quyidagi amallar mavjud:
- Word qo‘shish
- Word o‘chirish
- Word tahrirlash
- Word qidirish
- Word list ko‘rish
- Word statistikasi (eng ko‘p xato / eng ko‘p ishlatilgan)

3. Grammatik listlar
- Grammatik mavzular ro‘yxati
- Har bir mavzuga misollar
- Testlar bilan mustahkamlash

4. Quiz turlari
- So‘z → ma’no
- Ma’no → so‘z
- Multiple choice
- Fill in the blank
- Listening quiz (audio bilan)
- Writing quiz (쓰기)

5. Ko‘p formatli materiallar
Har bir til bo‘yicha:
- PDF savollar (testlar)
- PDF javob varaqalari
- Audio fayllar (듣기)
- Materiallar ro‘yxati (download qilinadi)

6. Stats (user stat)
- umumiy savollar soni
- to‘g‘ri / noto‘g‘ri javoblar
- eng qiyin so‘zlar
- eng ko‘p ishlatilgan so‘zlar
- umumiy progress foizi
- oxirgi mashq vaqti

B. Admin taraf funksiyalari

1. Userlarni boshqarish
- Foydalanuvchi ro‘yxatini ko‘rish
- Har bir userni:
  - qaysi tilni o‘rganayotgani
  - qaysi rejimda (global/local)
  - stats
- Userni bloklash / unblock
- User lug‘atini eksport qilish

2. Global lug‘atni boshqarish
- Umumiy lug‘atni ko‘rish
- So‘z qo‘shish / o‘chirish / tahrirlash
- Grammatik ro‘yxatni boshqarish
- Testlar va mashqlarni qo‘shish

3. GitHub bilan ishlash
Bot:
- GitHubdan faylni yuklaydi
- o‘zgartiradi
- commit + push qiladi

Tahrirlanadigan fayllar:
- dict.json
- grammar.json
- tasks.json
- media/audio/
- media/pdf/

4. Bot statistikasi (global)
- Eng faol userlar
- Eng dangasa userlar
- Eng ko‘p o‘rganilgan til
- Har bir til bo‘yicha:
  - lug‘at o‘sishi
  - mashq bajarilish soni
  - eng ko‘p o‘qilgan fayllar

3️⃣ FOLDER STRUCTURE (KENG, TUSHUNARLI)

project/
│
├── bot/
│   ├── main.py                 # Bot ishga tushishi
│   ├── config.py               # Tokenlar, GitHub sozlamalari
│   ├── loader.py               # Dispatcher, bot instance
│   ├── github_api.py           # GitHubga ulanish, fetch/push
│   ├── states.py               # FSM holatlari
│   │
│   ├── handlers/
│   │   ├── start.py            # Start bo‘limi
│   │   ├── language_select.py  # Til tanlash
│   │   ├── dict_manage.py      # Global/local lug‘at
│   │   ├── grammar.py          # Grammatik bo‘lim
│   │   ├── quiz.py             # Testlar
│   │   ├── materials.py        # PDF, audio fayllar
│   │   └── admin_panel.py      # Admin uchun maxsus bo‘limlar
│   │
│   ├── utils/
│   │   ├── file_manager.py     # JSON o‘qish/saqlash
│   │   ├── dict_manager.py     # Lug‘at logikasi
│   │   ├── stats_manager.py    # Statistika hisoblash
│   │   └── mode_manager.py     # Global / Local switch
│   │
│   └── keyboards/
│       ├── user_kb.py
│       └── admin_kb.py
│
├── languages/
│   ├── korean/
│   │   ├── dict.json
│   │   ├── grammar.json
│   │   ├── tasks.json
│   │   ├── audio/
│   │   └── pdf/
│   ├── english/
│   ├── japanese/
│   └── custom/                 # User o‘zi yaratgan til
│
├── userdata/
│   └── {user_id}.json          # User stats, local dict
│
└── logs/
    └── bot.log                 # Loglar

4️⃣ ALGORTIM (ISH JARAYONI BOSQICHMA-BOSQICH)

1. User START bosadi

Show: "Tilni tanlang"
User selects → selected_language
Load language folder → dict/grammar/tasks
Set user.mode = "local" or "global"

2. User MENU

1) My Dictionary
2) Grammar
3) Quiz
4) Materials (audio, pdf)
5) My Stats
6) Settings

3. Dictionary Module

Local / Global switch:

if user.mode == global:
    load languages/<lang>/dict.json
else:
    load userdata/<id>.json["dict"]

Allowed actions:

Add word
Edit word
Delete word
Search word
Show list
Show statistics

Har tahrir → GitHub repo update (global bo‘lsa).

4. Grammar Module

grammar.json ni yuklaydi
mavzular ro‘yxatini chiqaradi
har bir mavzu → misollar + mashq

5. Quiz Module

Algoritm:

Load dictionary (global/local)
Random 1 word
Choose quiz type
Send question
Check answer
Update stats
Repeat

6. Materials Module

Userga fayllarni chiqaradi:

languages/<lang>/audio/*.mp3
languages/<lang>/pdf/*.pdf

Download sifatida yuboriladi.

7. Stats Module

Hisoblaydi:

user.correct
user.wrong
accuracy %
study streak
difficult_words (xato bo‘lganlar)

8. Admin Panel Algorithm

1) Users list
     - id, name, selected lang, stats
2) Block / Unblock user
3) Global dictionary editor
4) Global grammar editor
5) Test & tasks editor
6) Upload Files (audio/pdf)
7) Bot global stats

5️⃣ GLOBAL & LOCAL MODE ALGORITMI

A) User Global Mode tanlasa:

dictionary_path = languages/<lang>/dict.json

→ barcha so‘zlar umumiy
→ admin monitoringi ko‘rinadi
→ foydalanuvchilar bir lug‘atdan foydalanadi

B) Local Mode tanlasa:

dictionary_path = userdata/<user_id>.json

→ shaxsiy lug‘at
→ sirli
→ mustaqil

Switch:

Settings → Choose mode → apply

6️⃣ LOYIHA UCHUN 1 TA SODDA QOIDA

Hammasi JSON + GitHub asosida.
Serverda faqat ishlovchi bot kodlari turadi.
"""