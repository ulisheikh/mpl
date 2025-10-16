
# ==============================
#  GITHUB CLI KOMANDALARI
# ==============================

# 🎯 GITHUB CLI LOGIN - GitHub hisobiga autentifikatsiya qilish
gh auth login

# 📂 REPOSITORY NOMINI O'ZGARTIRISH - GitHub repository nomini o'zgartirish
gh repo edit --name YANGI_REPO

# 📂 O'ZGARTIRISHNI YANGI REPOSITORY NOMI BILAN - Boshqa repository nomini o'zgartirish
gh repo edit --repo YOUR_USERNAME/ESKI_REPO --name YANGI_REPO

# 🎮 REPOSITORY KLONLASH - GitHub repository'sini lokalga klonlash
gh repo clone REPO_NOMI

# 🔧 YANGI REPOSITORY YARATISH - Yangi repository yaratish
gh repo create REPO_NOMI --public or --private

# 🗑️ REPOSITORY O'CHIRISH - GitHub repository'sini o'chirish
gh repo delete REPO_NOMI

# 🔄 REPOSITORY FORK QILISH - Repository'ni forking qilish
gh repo fork REPO_NOMI

# 🗂️ REPOSITORY RO'YXATINI KO'RISH - GitHubdagi barcha repository'larni ko'rish
gh repo list

# 🔍 REPOSITORY HAQIDA MA'LUMOT - Repository haqidagi ma'lumotlarni ko'rsatish
gh repo view REPO_NOMI

# 🔄 REPOSITORY NOMINI O'ZGARTIRISH - Repository nomini o'zgartirish
gh repo rename REPO_NOMI

# 🗂️ REPOSITORY ARCHIVE QILISH - Repository'ni archive qilish
gh repo archive REPO_NOMI

# 🔓 REPOSITORY UNARCHIVE QILISH - Repository'ni unarchive qilish
gh repo unarchive REPO_NOMI

# 🔄 REPOSITORY SINKRONIZATSIYA QILISH - Repository'ni GitHub bilan sinkronizatsiya qilish
gh repo sync REPO_NOMI

# 🏆 DEFAULT REPOSITORY SOZLASH - GitHub'da default repository sifatida sozlash
gh repo set-default REPO_NOMI

# 📑 GITHUB ISSUES YARATISH - Yangi issue yaratish
gh issue create --title "ISSUE_TITLE" --body "ISSUE_DESCRIPTION"

# 📝 GITHUB PULL REQUEST YARATISH - Yangi pull request yaratish
gh pr create --title "PR_TITLE" --body "PR_DESCRIPTION"

# 🔄 GITHUB PULL REQUESTNI MERGE QILISH - Pull requestni merge qilish
gh pr merge PR_NUMBER

# ==============================
#  GITHUB API BILAN REPOSITORY NOMINI O'ZGARTIRISH
# ==============================

# 🎯 GITHUB API YORDAMIDA REPOSITORY NOMINI O'ZGARTIRISH - GitHub API yordamida repository nomini o'zgartirish
curl -X PATCH -H "Authorization: token YOUR_GITHUB_TOKEN" \
-H "Accept: application/vnd.github.v3+json" \
https://api.github.com/repos/YOUR_USERNAME/OLD_REPO_NAME \
-d '{"name": "NEW_REPO_NAME"}'

# ==============================
#  GIT KOMANDALARI (REPOSITORY URL O'ZGARTIRISH)
# ==============================

# 🔄 GIT REMOTE URL'NI KO'RISH - Git remote URL'ni ko'rish
git remote -v

# 🔧 GIT REMOTE URL'NI YANGILASH - Git remote URL'ni yangi repository nomi bilan yangilash
git remote set-url origin https://github.com/YOUR_USERNAME/YANGI_REPO.git

# 🔄 YANGILANGAN REMOTE URL'NI TEKSHIRISH - Yangi URL'ni tekshirish
git remote -v

# 📝 GIT COMMIT QILISH - O'zgartirishlarni commit qilish
git commit -m "COMMIT_MESSAGE"

# 📤 GIT PUSH QILISH - O'zgartirishlarni remote repository'ga yuborish
git push origin BRANCH_NAME

# 📥 GIT PULL QILISH - O'zgarishlarni remote repository'dan olish
git pull origin BRANCH_NAME

# 🔄 GIT BRANCH YARATISH - Yangi branch yaratish
git checkout -b NEW_BRANCH_NAME

# 📄 GIT BRANCH NI O'ZGARTIRISH - Branchni o'zgartirish
git checkout BRANCH_NAME

# 🔄 GIT STATUS - Repositorydagi o'zgarishlarni ko'rish
git status

# 🔍 GIT LOG - Commitlar tarixini ko'rish
git log

# 🗑️ GIT RESET - O'zgarishlarni qaytarish
git reset --hard

# ==============================
#  GIT TAGLAR BILAN ISHLASH
# ==============================

# 🎯 GIT TAG YARATISH - Yangi tag yaratish
git tag -a TAG_NAME -m "TAG_MESSAGE"

# 📤 GIT TAG PUSH QILISH - Tag'ni remote repository'ga yuborish
git push origin TAG_NAME

# ==============================
#  GIT MERGE BILAN ISHLASH
# ==============================

# 🔄 GIT MERGE - Branchlarni birlashtirish
git merge BRANCH_NAME

# 📄 GIT MERGE CONFLICTS - Merge conflictlarni ko'rish
git diff

# Cache fayllarni o‘chirish (misol uchun: __pycache__)
git rm -r --cached __pycache__

# Git reposida barcha cache fayllarni o‘chirish
git rm -r --cached .
git add .
git commit -m "Git cache tozalandi va qayta kuzatish boshlandi"
git push origin main


# Barcha o‘chirilgan fayllarni saqlash
git commit -m "Removed cache files"

# O‘zgarishlarni GitHub-ga yuborish
git push origin main
