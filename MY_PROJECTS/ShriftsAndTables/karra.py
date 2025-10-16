import os

# Faylni saqlash joyi
path = "/home/ulee/Desktop/Karra_jadvali.py"

# Katalog mavjudligini tekshirish va yaratish
os.makedirs(os.path.dirname(path), exist_ok=True)

sonlar = list(range(2, 11))  # 2 dan 10 gacha sonlar

# Faylni ochish
with open(path, "w", encoding="utf-8") as file:
    for a in range(2, 11, 3):  # 3 ustunlik sikl (1, 4, 7, 10)
        for son in sonlar:
            line = ""  # Har bir qator uchun bo‘sh string
            for i in range(a, min(a + 3, 11)):  # 3 ustun (1-3, 4-6, 7-9, 10)
                natija = i * son
                line += f"  {i} x {son} = {natija}".ljust(18)  # Har bir ustunni tekislash
            file.write(line + "\n")  # Yangi qatordan yozish
        file.write("\n")  # Har bir blok orasiga bo‘sh qator

print(f"Karra jadvali saqlandi: {path}")
