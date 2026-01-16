# -*- coding: utf-8 -*-
"""
🚀 GIT & GITHUB ULTIMATE MANAGER
1. Repozitoriya va papkalarni boshqarish
2. Terminal orqali GitHub repo yaratish (CLI)
"""

import os

# ============================================================
# 1-BO'LIM: LOKAL REPO VA PAPKA AMALLARI
# ============================================================
git_operations = {
    "1. YANGI REPOZITORIYA OCHISH": {
        "git init": "Hozirgi papkani Git loyihasiga aylantirish.",
        "git clone <url>": "Mavjud repozitoriyani GitHub'dan ko'chirib olish.",
        "git remote add origin <url>": "Lokal papkani masofaviy GitHub repo bilan bog'lash."
    },
    "2. PAPKA VA FAYLLARNI QO'SHISH": {
        "mkdir <nom>": "Yangi papka yaratish (Linux/Terminal buyrug'i).",
        "touch <fayl>": "Yangi bo'sh fayl yaratish.",
        "git add <papka_nomi>/": "Butun bir papkani Gitga qo'shish.",
        "git add .": "Barcha yangi fayl va papkalarni staging'ga olish."
    },
    "3. O'CHIRISH (DELETE) AMALLARI": {
        "git rm <fayl>": "Faylni ham Gitdan, ham diskdan o'chiradi.",
        "git rm -r <papka>": "Papkani ham Gitdan, ham diskdan butunlay o'chiradi.",
        "git rm --cached <fayl>": "Faylni GitHub'dan o'chiradi, lekin kompyuterda qoldiradi.",
        "git rm -r --cached <papka>/": "Papkani GitHub'dan o'chiradi, lekin lokalda qoldiradi.",
        "rm -rf .git": "Lokal papkadagi Git tarixini butunlay o'chirib, uni oddiy papkaga aylantirish."
    },
    "4. KO'CHIRISH VA NOMINI O'ZGARTIRISH": {
        "git mv <eski_nom> <yangi_nom>": "Fayl yoki papka nomini o'zgartirish (Git buni darhol sezadi).",
        "git mv <fayl> <papka>/": "Faylni bir papkadan boshqasiga ko'chirish."
    },
    "5. REPOZITORIYANI TOZALASH (RESET)": {
        "git reset --hard origin/main": "Lokal kodingizni GitHub'dagi holat bilan bir xil qiladi (hamma o'zgarishlar o'chadi).",
        "git clean -fd": "Gitda yo'q bo'lgan barcha ortiqcha papka va fayllarni o'chirib tashlash."
    }
}

# ============================================================
# 2-BO'LIM: GITHUB CLI VA REMOTE CREATOR
# ============================================================
github_cli_guide = {
    "1. GH CLI ORQALI (TAVSIYA ETILADI)": {
        "gh auth login": "GitHub akkauntingizga terminaldan kirish.",
        "gh repo create <nom> --public": "Yangi ochiq repo yaratish.",
        "gh repo create <nom> --private": "Yangi yopiq (shaxsiy) repo yaratish.",
        "gh repo create <nom> --clone": "Yaratish va darhol kompyuterga ko'chirib olish."
    },
    "2. CURL (API) ORQALI (PROGRAMMISTLAR UCHUN)": {
        "curl -u 'USER' https://api.github.com/user/repos -d '{\"name\":\"NOM\"}'": "API orqali yangi repo ochish."
    },
    "3. LOKALNI MASOFAVIYGA ULASH": {
        "git remote add origin <url>": "Lokalni yangi ochilgan repo bilan bog'lash.",
        "git branch -M main": "Asosiy branch nomini 'main'ga o'zgartirish.",
        "git push -u origin main": "Kodni birinchi marta yuklash (ulash)."
    },
    "4. REPOZITORIYANI O'CHIRISH (CLI)": {
        "gh repo delete <user/repo>": "GitHub saytiga kirmasdan reponi o'chirib tashlash."
    }
}

def display_git_info():
    # Terminalni tozalash
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 1-Jadvalni chiqarish
    print("="*85)
    print("🛠  1-BO'LIM: GIT REPO VA PAPKA BOSHQARUVI")
    print("="*85)
    for section, commands in git_operations.items():
        print(f"\n📂 {section}")
        for cmd, info in commands.items():
            print(f"  🔘 {cmd.ljust(35)} | {info}")
            
    print("\n" + "—"*85 + "\n")

    # 2-Jadvalni chiqarish
    print("="*85)
    print("🌐 2-BO'LIM: GITHUB TERMINAL COMMANDS (CREATE & DELETE REPO)")
    print("="*85)
    for section, commands in github_cli_guide.items():
        print(f"\n📁 {section}")
        for cmd, info in commands.items():
            print(f"  ⭐ {cmd.ljust(45)} | {info}")

    print("\n" + "="*85)
    print("💡 MASLAHAT: 'gh' (GitHub CLI) orqali saytga kirmay repo ochish eng tezkor yo'ldir.")
    print("="*85)

if __name__ == "__main__":
    display_git_info()