# git_scenario_demo.py
# Git conflict holatini TERMINAL uslubida tushuntiruvchi DEMO
# Hech qanday real git ishlamaydi – faqat ko‘rsatish uchun

import time
import sys

def slow_print(text, delay=0.005):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def header(title):
    print("\n" + "=" * 70)
    print(f"### {title}")
    print("=" * 70)

def show_file(title, content):
    print(f"\n--- mevalar.txt ({title}) ---")
    print(content)
    print("-" * 30)

# BOSHLANG‘ICH HOLAT
github_file = """olma
olcha
qovun
nok
"""

local_file = """olma
olcha
qovun
tarvuz
"""

header("BOSHLANG‘ICH HOLAT")

slow_print("$ git status")
slow_print("On branch main")
slow_print("Your branch and 'origin/main' have diverged\n")

show_file("GitHub (sayt)", github_file)
show_file("Local kompyuter", local_file)

# =========================
# VARIANT A — LOCAL USTUN
# =========================
header("VARIANT A — LOCAL USTUN (git push --force)")

slow_print("$ git add mevalar.txt")
slow_print("$ git commit -m \"tarvuz qo‘shildi\"")
slow_print("[main abc123] tarvuz qo‘shildi\n")

slow_print("$ git push origin main")
slow_print("! [rejected] main -> main (fetch first)")
slow_print("error: failed to push some refs\n")

slow_print("$ git push origin main --force")
slow_print("Enumerating objects: 5, done.")
slow_print("To github.com:user/repo.git")
slow_print(" + nok -> tarvuz (forced update)\n")

show_file("YAKUNIY HOLAT (GitHub va Local)", local_file)

# =========================
# VARIANT B — SAYT USTUN
# =========================
header("VARIANT B — SAYT USTUN (local o‘zgarish tashlanadi)")

slow_print("$ git restore mevalar.txt")
slow_print("Local o‘zgarishlar bekor qilindi\n")

slow_print("$ git pull origin main")
slow_print("Updating abc123..def456")
slow_print("Fast-forward\n")

show_file("YAKUNIY HOLAT (GitHub va Local)", github_file)

# =========================
# VARIANT C — IKKALASI SAQLANADI
# =========================
header("VARIANT C — IKKALASI SAQLANADI (stash + merge)")

slow_print("$ git stash")
slow_print("Saved working directory and index state\n")

slow_print("$ git pull origin main")
slow_print("Updating abc123..def456\n")

slow_print("$ git stash pop")
slow_print("CONFLICT (content): Merge conflict in mevalar.txt\n")

conflict_file = """olma
olcha
qovun
<<<<<<< HEAD
nok
=======
tarvuz
>>>>>>> stash
"""

show_file("CONFLICT HOLATI", conflict_file)

merged_file = """olma
olcha
qovun
nok
tarvuz
"""

slow_print("# conflict qo‘lda to‘g‘irlandi")

show_file("TO‘G‘IRLANGAN FAYL", merged_file)

slow_print("$ git add mevalar.txt")
slow_print("$ git commit -m \"nok va tarvuz birlashtirildi\"")
slow_print("[main fed999] nok va tarvuz birlashtirildi\n")

slow_print("$ git push origin main")
slow_print("To github.com:user/repo.git")
slow_print("   def456..fed999  main -> main\n")

show_file("YAKUNIY HOLAT (GitHub va Local)", merged_file)

print("\n✅ DEMO TUGADI")
print("Qaysi variant qachon ishlatilishini endi aniq ko‘rding 👍")
