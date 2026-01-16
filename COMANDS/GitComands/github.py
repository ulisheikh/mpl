# -*- coding: utf-8 -*-
"""
🚀 GIT & GITHUB ENCYCLOPEDIA (FULL VERSION)
Dasturchi uchun jamiiki Git buyruqlari jamlanmasi.
"""

import os

git_encyclopedia = {
    "1. LOYIHA BOSHLASH VA SOZLAMALAR": {
        "git init": "Yangi lokal repozitoriya ochish.",
        "git clone <url>": "GitHub'dagi loyihani kompyuterga ko'chirib olish.",
        "git config --global user.name 'Ism'": "Git foydalanuvchi nomini sozlash.",
        "git config --global user.email 'email'": "Git foydalanuvchi emailini sozlash."
    },
    "2. KODLARNI NAZORAT QILISH (WORKING AREA)": {
        "git status": "O'zgargan fayllar ro'yxatini ko'rish.",
        "git add <file>": "Faylni keshga olish (staging).",
        "git add .": "Barcha o'zgarishlarni keshga olish.",
        "git commit -m 'xabar'": "O'zgarishlarni xotiraga muhrlash.",
        "git commit --amend": "Oxirgi commit xabarini yoki kodini o'zgartirish."
    },
    "3. O'CHIRISH VA TOZALASH (CLEANING)": {
        "git rm --cached <file>": "Faylni GitHub'dan o'chirib, lokalda qoldirish.",
        "git rm -rf --cached .": "Barcha fayllarni keshdan chiqarish (.gitignore yangilash uchun).",
        "git clean -fd": "Gitga kiritilmagan barcha vaqtinchalik fayllarni o'chirish.",
        "git checkout -- <file>": "Faylni oxirgi commit holatiga qaytarish (o'zgarishlar o'chadi)."
    },
    "4. MASOFAVIY OMBOR (REMOTE/GITHUB)": {
        "git remote add origin <url>": "Lokalni GitHub bilan bog'lash.",
        "git push origin <branch>": "Kodni GitHub'ga yuborish.",
        "git pull origin <branch>": "GitHub'dagi kodni yuklab olish va merge qilish.",
        "git fetch": "GitHub'dagi o'zgarishlarni yuklamasdan ko'rib chiqish.",
        "git remote -v": "Ulangan GitHub manzillarini ko'rish."
    },
    "5. BRANCH (SHOXLANISH) VA MERGE": {
        "git branch": "Branchlar ro'yxatini ko'rish.",
        "git checkout -b <nom>": "Yangi branch ochish va unga o'tish.",
        "git checkout <nom>": "Boshqa branchga o'tish.",
        "git merge <nom>": "Boshqa branch kodini hozirgisiga qo'shish.",
        "git branch -d <nom>": "Branch'ni o'chirib tashlash."
    },
    "6. LOG VA TARIXNI KO'RISH (HISTORY)": {
        "git log": "Commitlar tarixini to'liq ko'rish.",
        "git log --oneline": "Commitlarni qisqa (bir qatorli) ko'rish.",
        "git log -p <file>": "Fayl ichidagi o'zgarishlar tarixini ko'rish.",
        "git blame <file>": "Faylning har bir qatorini kim yozganini ko'rish."
    },
    "7. VAQTINCHA SAQLASH (STASHING)": {
        "git stash": "Chala ishlarni vaqtincha xotiraga berkitish.",
        "git stash list": "Berkitilgan ishlar ro'yxati.",
        "git stash pop": "Berkitilgan ishlarni qaytarib olish va ro'yxatdan o'chirish.",
        "git stash apply": "Qaytarib olish (lekin ro'yxatda saqlab qolish)."
    },
    "8. REVERT VA RESET (ORQAGA QAYTISH)": {
        "git revert <commit_id>": "Xatoni tuzatish uchun yangi qarama-qarshi commit ochish.",
        "git reset --soft HEAD~1": "Oxirgi commitni o'chirish, kodlarni saqlab qolish.",
        "git reset --hard HEAD~1": "Oxirgi commitni ham, kodlarni ham butunlay yo'q qilish.",
        "git reflog": "Gitda qilingan barcha amallar (hatto o'chganlar) tarixini topish."
    },
    "9. VERSALASH VA TAGLAR": {
        "git tag v1.0": "Lokalda versiya belgilash.",
        "git push origin --tags": "Barcha taglarni GitHub'ga yuborish."
    }
}

def display_all():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*85)
    print("💎 JAMIYKI GIT BUYRUQLARI ENSIKLOPEDIYASI v2.0")
    print("="*85)
    
    for section, commands in git_encyclopedia.items():
        print(f"\n🔥 {section}")
        for cmd, info in commands.items():
            print(f"  ⚡️ {cmd.ljust(35)} | {info}")

    print("\n" + "="*85)
    print("🚨 CONFLICT QANDAY HAL QILINADI?")
    print("1. git pull qilganda conflict bo'lsa, faylni oching.")
    print("2. <<<< HEAD (Sizniki) va >>>> incoming (GitHubniki) orasidan bittasini tanlang.")
    print("3. Ortiqcha >>>, ===, <<< belgilarini o'chirib, faylni saqlang.")
    print("4. git add .  ->  git commit -m 'Fixed'  ->  git push")
    print("="*85)


if __name__ == "__main__":
    display_all()