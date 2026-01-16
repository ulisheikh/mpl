# -*- coding: utf-8 -*-
"""
MATNLAR - IKKI TIL
O'zbek va Koreys tillarida barcha matnlar
"""

TEXTS = {
    'uz': {
        # ASOSIY
        'welcome': '👋 Korean-O\'zbek Lug\'at Botiga xush kelibsiz!',
        'enter_password': '🔐 Botdan foydalanish uchun parolni kiriting:',
        'password_correct': '✅ Xush kelibsiz!',
        'password_wrong': '❌ Noto\'g\'ri parol. Qayta urinib ko\'ring.',
        'password_blocked': '🚫 Siz 5 daqiqaga bloklangansiz.',
        
        # TUGMALAR
        'btn_sections': '📂 BO\'LIMLAR',
        'btn_settings': '⚙️ SOZLAMALAR',
        'btn_export_json': '📥 JSON',
        'btn_export_python': '🐍 PYTHON',
        'btn_back': '« Orqaga',
        
        # SOZLAMALAR
        'settings_menu': '⚙️ SOZLAMALAR',
        'btn_system_status': '📊 Tizim holati',
        'btn_users': '👥 Foydalanuvchilar',
        'btn_language': '🌐 Tilni o\'zgartirish',
        'btn_reset_password': '🔐 Parolni o\'zgartirish',
        'btn_about': 'ℹ️ Bot haqida',
        
        # TIL
        'select_language': '🌐 Tilni tanlang:',
        'language_changed': '✅ Til o\'zgartirildi!',
        
        # BO'LIMLAR
        'topics_list': '📂 MAVJUD TOPIKLAR:',
        'no_topics': '❌ Lug\'at bo\'sh',
        'select_topic': '💡 Topikni tanlash uchun bosing',
        'topic_selected': '📌 {topic_num}-TOPIK',
        'select_section': '💡 Bo\'limni tanlash uchun bosing',
        
        # ADMIN
        'admin_panel': '👑 ADMIN PANEL',
        'users_list': '👥 FOYDALANUVCHILAR:',
        'no_users': '❌ Hozircha foydalanuvchilar yo\'q',
        'user_details': '📊 USER {user_id} MA\'LUMOTLARI',
        'user_topics': '📚 Topiklar: {count} ta',
        'user_words': '📖 So\'zlar: {count} ta',
        'user_file_size': '💾 Fayl hajmi: {size}',
        'btn_download_file': '📥 Faylni yuklash',
        'btn_details': '📂 Tafsilotlar',
        
        # TIZIM
        'system_status': '📊 TIZIM HOLATI',
        'uptime': '⏱ Ishlash vaqti: {time}',
        'battery': '🔋 Batareya: {percent}%',
        'temperature': '🌡 Harorat: {temp}°C',
        'battery_status': '⚡ Holat: {status}',
        'battery_unavailable': '🔋 Batareya: Termux API yo\'q',
        'ram_usage': '🧠 RAM: {percent}%',
        'ram_size': '💾 RAM hajmi: {used}MB / {total}MB',
        'dict_size': '📦 Lug\'at hajmi: {size}',
        
        # EXPORT
        'export_json_caption': '📥 Lug\'at fayli (JSON format)',
        'export_python_caption': '🐍 Lug\'at fayli (Python format)',
        'export_empty': '❌ Lug\'at bo\'sh',
        
        # SO'ZLAR
        'word_added': '✅ {count} ta so\'z saqlandi!',
        'word_saved_location': '📍 Manzil: {topic} > {section} > {question}',
        'word_deleted': '🗑 So\'z o\'chirildi: {word}',
        'word_restored': '✅ So\'z tiklandi!',
        'word_not_found': '❌ Lug\'atda bunday so\'z topilmadi',
        'word_updated': '📝 Yangilandi: {old} → {new}',
        
        # XATOLAR
        'error_no_location': '⚠️ Avval topik va bo\'lim tanlang\n\nMisol: >35r',
        'error_format': '❌ Format xato!',
        'error_not_found': '❌ Topilmadi',
        
        # YORDAM
        'help_title': '📚 LUG\'AT BOT | YO\'RIQNOMA',
        'help_create': '1️⃣ BO\'LIM YARATISH\n👉 >35 r,w,l',
        'help_add_word': '2️⃣ SO\'Z QO\'SHISH\n👉 1 (savol)\n👉 안녕 salom',
        'help_delete': '3️⃣ O\'CHIRISH (rm.)\n🗑 rm.35r33 (savol)\n🗑 rm.so\'z (so\'z)',
        'help_restore': '4️⃣ TIKLASH (rs.)\n🔄 rs.35r33\n🔄 rs.so\'z',
        'help_search': '5️⃣ QIDIRUV & MANZIL\n🔍 s.so\'z | 📍 %l',
        'help_system': '⚙️ TIZIM: /status',
        'help_tip': '💡 Buyruqni nusxalash uchun ustiga bosing.',
        
        # BOT HAQIDA
        'about_bot': 'ℹ️ BOT HAQIDA\n\n'
                     '📚 Korean-O\'zbek Lug\'at Bot\n'
                     '🤖 Versiya: 2.0\n'
                     '👨‍💻 Yaratuvchi: sir🤫\n\n'
                     '📝 Tavsif:\n'
                     'Bu bot koreys tilini o\'rganuvchilar uchun shaxsiy lug\'at yaratish imkonini beradi.\n\n'
                     '✨ Xususiyatlar:\n'
                     '• Shaxsiy lug\'at\n'
                     '• Ikki tilda (O\'zbek/Koreys)\n'
                     '• So\'zlarni saqlash va boshqarish\n'
                     '• Export (JSON/Python)\n'
                     '• Admin panel',
        # MAIN MENU TUGMASI
        "home_stats": (
            "📊 <b>Statistika</b>\n\n"
            "👥 Jami foydalanuvchilar: <b>{users}</b>\n"
            "📚 Sizning topiklar: <b>{topics}</b>\n"
            "📝 Sizning so'zlar: <b>{words}</b>\n\n"
            "💡 Kerakli tugmani bosing"
        ),
    
    },
    
    'ko': {
        # ASOSIY
        'welcome': '👋 한국어-우즈베크어 사전 봇에 오신 것을 환영합니다!',
        'enter_password': '🔐 봇을 사용하려면 비밀번호를 입력하세요:',
        'password_correct': '✅ 환영합니다!',
        'password_wrong': '❌ 잘못된 비밀번호입니다. 다시 시도하세요.',
        'password_blocked': '🚫 5분 동안 차단되었습니다.',
        
        # TUGMALAR
        'btn_sections': '📂 섹션',
        'btn_settings': '⚙️ 설정',
        'btn_export_json': '📥 JSON',
        'btn_export_python': '🐍 PYTHON',
        'btn_back': '« 뒤로',
        
        # SOZLAMALAR
        'settings_menu': '⚙️ 설정',
        'btn_system_status': '📊 시스템 상태',
        'btn_users': '👥 사용자',
        'btn_language': '🌐 언어 변경',
        'btn_reset_password': '🔐 비밀번호 변경',
        'btn_about': 'ℹ️ 봇 정보',
        
        # TIL
        'select_language': '🌐 언어를 선택하세요:',
        'language_changed': '✅ 언어가 변경되었습니다!',
        
        # BO'LIMLAR
        'topics_list': '📂 사용 가능한 주제:',
        'no_topics': '❌ 사전이 비어 있습니다',
        'select_topic': '💡 주제를 선택하려면 클릭하세요',
        'topic_selected': '📌 {topic_num}-주제',
        'select_section': '💡 섹션을 선택하려면 클릭하세요',
        
        # ADMIN
        'admin_panel': '👑 관리자 패널',
        'users_list': '👥 사용자:',
        'no_users': '❌ 아직 사용자가 없습니다',
        'user_details': '📊 사용자 {user_id} 정보',
        'user_topics': '📚 주제: {count}개',
        'user_words': '📖 단어: {count}개',
        'user_file_size': '💾 파일 크기: {size}',
        'btn_download_file': '📥 파일 다운로드',
        'btn_details': '📂 자세히',
        
        # TIZIM
        'system_status': '📊 시스템 상태',
        'uptime': '⏱ 가동 시간: {time}',
        'battery': '🔋 배터리: {percent}%',
        'temperature': '🌡 온도: {temp}°C',
        'battery_status': '⚡ 상태: {status}',
        'battery_unavailable': '🔋 배터리: Termux API 없음',
        'ram_usage': '🧠 RAM: {percent}%',
        'ram_size': '💾 RAM 크기: {used}MB / {total}MB',
        'dict_size': '📦 사전 크기: {size}',
        
        # EXPORT
        'export_json_caption': '📥 사전 파일 (JSON 형식)',
        'export_python_caption': '🐍 사전 파일 (Python 형식)',
        'export_empty': '❌ 사전이 비어 있습니다',
        
        # SO'ZLAR
        'word_added': '✅ {count}개 단어가 저장되었습니다!',
        'word_saved_location': '📍 위치: {topic} > {section} > {question}',
        'word_deleted': '🗑 단어가 삭제되었습니다: {word}',
        'word_restored': '✅ 단어가 복원되었습니다!',
        'word_not_found': '❌ 사전에서 단어를 찾을 수 없습니다',
        'word_updated': '📝 업데이트됨: {old} → {new}',
        
        # XATOLAR
        'error_no_location': '⚠️ 먼저 주제와 섹션을 선택하세요\n\n예: >35r',
        'error_format': '❌ 형식 오류!',
        'error_not_found': '❌ 찾을 수 없음',
        
        # YORDAM
        'help_title': '📚 사전 봇 | 사용법',
        'help_create': '1️⃣ 섹션 생성\n👉 >35 r,w,l',
        'help_add_word': '2️⃣ 단어 추가\n👉 1 (질문)\n👉 안녕 salom',
        'help_delete': '3️⃣ 삭제 (rm.)\n🗑 rm.35r33 (질문)\n🗑 rm.단어 (단어)',
        'help_restore': '4️⃣ 복원 (rs.)\n🔄 rs.35r33\n🔄 rs.단어',
        'help_search': '5️⃣ 검색 & 위치\n🔍 s.단어 | 📍 %l',
        'help_system': '⚙️ 시스템: /status',
        'help_tip': '💡 명령을 복사하려면 클릭하세요.',
        
        # BOT HAQIDA
        'about_bot': 'ℹ️ 봇 정보\n\n'
                     '📚 한국어-우즈베크어 사전 봇\n'
                     '🤖 버전: 2.0\n'
                     '👨‍💻 개발자: 비밀🤫\n\n'
                     '📝 설명:\n'
                     '이 봇은 한국어 학습자를 위한 개인 사전을 만들 수 있습니다.\n\n'
                     '✨ 기능:\n'
                     '• 개인 사전\n'
                     '• 두 언어 (우즈베크어/한국어)\n'
                     '• 단어 저장 및 관리\n'
                     '• 내보내기 (JSON/Python)\n'
                     '• 관리자 패널',
        # MAIN MENU TUGMASI
                "home_stats": (
            "📊 <b>통계</b>\n\n"
            "👥 전체 사용자: <b>{users}</b>\n"
            "📚 내 주제: <b>{topics}</b>\n"
            "📝 내 단어: <b>{words}</b>\n\n"
            "💡 버튼을 선택하세요"
        ),
    }
}