Siz uchun grep va sed buyruqlarining eng foydali va ko'p ishlatiladigan funksiyalarini main.py bot faylingiz misolida tushuntirib beraman. Bu ma'lumotlarni o'zingizning qo'llanmangizga (chapter-2) qo'shib qo'yishingiz mumkin.

1. grep — Matn qidirish va tahlil qilish
grep fayl ichidan kerakli qatorlarni topish uchun eng yaxshi vositadir.

Matnni sanash (-c): Faylda ma'lum bir so'z necha marta qatnashganini ko'rsatadi.

Misol: grep -c "get_text" main.py

Ma'nosi: "Faylda nechtadir get_text funksiyasi borligini sanab ber."

Qator raqami bilan chiqarish (-n): So'z qaysi qatorda turganini ko'rsatadi.

Misol: grep -n "ALL_TEXTS" main.py

Ma'nosi: "ALL_TEXTS lug'ati nechanchi qatorda ekanini top."

Katta-kichik harfni farqlamaslik (-i): Harf qanday yozilishidan qat'i nazar topadi.

Misol: grep -i "command" main.py

Ma'nosi: "Command, command yoki COMMAND so'zlarining hammasini top."

Faqat so'zning o'zini sanash (-o | wc -l): Bitta qatorda bir nechta so'z bo'lsa hammasini sanaydi.

Misol: grep -o "lang" main.py | wc -l

Ma'nosi: "Faylda jami necha marta lang so'zi ishlatilganini aniq sanab ber."

Inkor qidirish (-v): Berilgan so'z yo'q qatorlarni ko'rsatadi.

Misol: grep -v "#" main.py

Ma'nosi: "Izohlar (comment) bo'lmagan barcha kodlarni ko'rsat."

2. sed — Matnni tahrirlash va manipulyatsiya
sed faylni ochmasdan turib uning ichidagi matnlarni o'zgartirish, o'chirish yoki qo'shish imkonini beradi.

Almashtirish (s/.../.../g): So'zlarni boshqasiga almashtiradi.

Misol: sed 's/get_game_text/get_text/g' main.py

Ma'nosi: "Eski funksiya nomini yangisiga almashtirib terminalda ko'rsat."

Faylni joyida o'zgartirish (-i): O'zgarishni faylning o'zida saqlaydi.

Misol: sed -i 's/ko/kr/g' main.py

Ma'nosi: "Fayldagi barcha ko kodlarini kr ga o'zgartir va saqla."

Qatorni o'chirish (d): Ma'lum bir so'z bor qatorni butunlay o'chiradi.

Misol: sed -i '/print/d' main.py

Ma'nosi: "Koddagi barcha print() qatorlarini (debug ma'lumotlarini) o'chirib tashla."

Yangi qator qo'shish (a - append): Mos kelgan qatorning pastidan yangi matn qo'shadi.

Misol: sed -i '/import logging/a\import os' main.py

Ma'nosi: "import logging qatoridan keyin yangi import os qatorini qo'sh."

Qatorning tepasidan qo'shish (i - insert): Mos kelgan qatorning tepasidan matn qo'shadi.

Misol: sed -i '1i #!/usr/bin/python3' main.py

Ma'nosi: "Faylning eng birinchi qatoriga Python shebang-ni qo'sh."

Sizning lug'atingiz uchun tayyor matn (To'ldirilgan variant):
JSON

"sed": "Matnni avtomatik tahrirlash (Stream Editor). Qidirish, almashtirish va o‘chirish uchun. (ex: `sed 's/old/new/g' main.py`)",
"sed -i": "Faylni bevosita o'zida o'zgartirish. (ex: `sed -i 's/get_game_text/get_text/g' main.py`)",
"sed -d": "Belgilangan qatorni o'chirish. (ex: `sed -i '/test/d' main.py` — 'test' so'zi bor qatorlarni o'chiradi)",
"sed -a": "Qator ostiga yangi matn qo'shish (Append). (ex: `sed -i '/pattern/a\\new_text' file.py`)",
"sed -i 'num1,num2d'": "Ma'lum diapazondagi qatorlarni o'chirish. (ex: `sed -i '5,10d' main.py` — 5 dan 10-qatorgacha o'chiradi)",
"grep": "Fayl ichidan matn qidirish. (ex: `grep 'bot' main.py`)",
"grep -c": "Topilgan qatorlar sonini sanash. (ex: `grep -c 'def' main.py` — funksiyalar sonini ko'rsatadi)",
"grep -n": "Topilgan matnning qator raqamini ko'rsatish. (ex: `grep -n 'error' bot.log`)",
"grep -v": "Berilgan so'z qatnashmagan qatorlarni ko'rsatish. (Invert search)",
"grep -r": "Papka ichidagi barcha fayllardan qidirish (Recursive)."
Navbatdagi qadam:
Ushbu buyruqlar yordamida main.py faylingizni yana bir bor tahlil qilib ko'rmoqchimisiz? Masalan, kodingizda qaysi funksiya eng ko'p ishlatilganini aniqlashimiz mumkin. Shuni bajarib ko'ramizmi?