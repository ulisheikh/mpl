# ============================================
#        OVOZ ORQALI SHAXSNI ANIQLASH
#       KUTUBXONALAR VA ULARNING VAZIFASI
# ============================================

# 🔹 1. SPEECHBRAIN
# - Open-source kutubxona (PyTorch asosida)
# - Speaker recognition, ASR (speech-to-text), emotion recognition, va boshqalarni qo‘llaydi
# - Juda kuchli pretrained model: "ecapa-voxceleb"
# - Real audio fayllarni solishtirib, bir odammi yoki yo‘qmi degan natija beradi

# 📦 O‘rnatish:
# pip install speechbrain

# 🔧 Asosiy metod/funksiyalar:
# ➤ from speechbrain.pretrained import SpeakerRecognition
# ➤ model = SpeakerRecognition.from_hparams(...)
# ➤ score, prediction = model.verify_files("file1.wav", "file2.wav")

# ✅ Vazifasi:
# — 2 ta ovoz faylini taqqoslab, ularning bitta odamga tegishli ekanligini aniqlaydi
# — score: o‘xshashlik darajasi (float)
# — prediction: True/False (bir odam yoki yo‘q)


# 🔹 2. PYANNOTE-AUDIO
# - Juda kuchli speaker diarization (qachon kim gapirganini aniqlash)
# - Gapni vaqt bo‘yicha bo‘lib, turli odamlarni ajratadi (multi-speaker audio uchun)
# - Deep learning asosida, Hugging Face modelarini qo‘llaydi

# 📦 O‘rnatish:
# pip install pyannote-audio

# 🔧 Asosiy metod/funksiyalar:
# ➤ from pyannote.audio import Pipeline
# ➤ pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
# ➤ diarization = pipeline("audio.wav")

# ✅ Vazifasi:
# — Audio ichidagi gapiruvchilarni vaqtga qarab ajratadi
# — Har bir segmentga shaxs ID (SPEAKER_00, SPEAKER_01) biriktiradi


# 🔹 3. RESPEAKER + LIBROSA + SKLEARN (custom)
# - MFCC xususiyatlar chiqarib, o‘zingiz klassifikator (SVM, KNN, CNN) yasaysiz
# - Ko‘proq moslashtirilgan (custom) tizimlar uchun

# 📦 O‘rnatish:
# pip install librosa scikit-learn numpy

# 🔧 Asosiy metod/funksiyalar:
# ➤ librosa.load("audio.wav")          # Audio faylni yuklaydi
# ➤ librosa.feature.mfcc(...)         # MFCC xususiyatlarini ajratadi
# ➤ sklearn.model.fit(X, y)           # Klassifikatorni o‘qitadi
# ➤ sklearn.model.predict(X_test)     # Kiritilgan ovozga ID beradi

# ✅ Vazifasi:
# — Ovozdan MFCC (numerik belgi) chiqarish
# — O‘zingizga mos model yaratish (tasniflash)


# 🔹 4. TORCHAUDIO + WAV2VEC2.0
# - Self-supervised model, Facebook AI tomonidan
# - Juda chuqur (deep) ovoz tahlil qilish imkonini beradi
# - wav2vec2 model speaker recognition uchun xususiylashtirilgan variantlarga ega

# 📦 O‘rnatish:
# pip install torchaudio transformers

# 🔧 Asosiy metod/funksiyalar:
# ➤ from transformers import Wav2Vec2ForXxx
# ➤ from torchaudio import load
# ➤ model(input_audio) → embedding → similarity

# ✅ Vazifasi:
# — Ovozdan embedding (raqamli ko‘rinish) olish
# — Bu embedding speaker tanish uchun taqqoslanadi


# 🔹 5. DEEPVOICE / REALTIME SYSTEMS (advanced)
# - Realtime identifikatsiya uchun ishlatiladi
# - Asosan TensorFlow yoki PyTorch bilan
# - Raspberry Pi yoki mobil tizimlarga ham joylashtiriladi

# ❗ Bu tizimlar ko‘pincha: MFCC + RNN/CNN + similarity scoring orqali ishlaydi
# ❗ Ovoz tanib olish uchun latency (kechikish) kam bo‘lishi kerak

# 📌 Tavsiya:
# — Oddiy holat uchun: SPEECHBRAIN
# — Ko‘p odamli suhbatlar uchun: PYANNOTE-AUDIO
# — O‘zingiz model o‘qitmoqchi bo‘lsangiz: LIBROSA + SKLEARN
# — Real-time system: Wav2Vec2.0 yoki DeepStream bilan integratsiya

# ============================================
# TAYYOR DASHBOARD, BOT YOKI SERVIS QURMOQCHI BO‘LSANGIZ —
# AYTING, SHUNGA MOS STRUKTURA VA KOD YARATIB BERAMAN
# ============================================



########################################################################################

# Zo‘r! Demak sizga kerak:

# Ovozdan kim gapirayotganini aniqlash (speaker recognition)

# Telefon qo‘ng‘irog‘i bo‘lsa ham, ovozdan shaxsni tanish

# Ovoz yozish, tahlil qilish va natijani chiqarish

# (Ixtiyoriy) Real-time yoki avtomatik tarzda ishlashi

# Shuni bosqichma-bosqich loyiha sifatida tayyorlab bersam bo‘ladimi? Quyida siz uchun to‘liq yo‘l xaritasi:

# ✅ 1-BO‘LIM: Ovoz yozish va saqlash
# record_voice.py:
# python
# Copy
# Edit
# import sounddevice as sd
# from scipy.io.wavfile import write

# def record(filename="voice.wav", duration=5, fs=16000):
#     print(f"🎙 {duration} soniya davomida yozilmoqda...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
#     sd.wait()
#     write(filename, fs, recording)
#     print(f"✅ Saqlandi: {filename}")

# # Foydalanish
# record("my_voice.wav", duration=5)
# ✅ 2-BO‘LIM: 2 ta odamning ovozini taqqoslab, bir odammi-yo‘qmi aniqlash
# compare_voices.py:
# python
# Copy
# Edit
# from speechbrain.pretrained import SpeakerRecognition

# def compare_voices(file1, file2):
#     model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_model")
#     score, prediction = model.verify_files(file1, file2)
#     print(f"Taqqoslash: {file1} vs {file2}")
#     print(f"✅ Natija: {'Bir odam' if prediction else 'Boshqa odam'} (score: {score:.3f})")

# # Misol
# compare_voices("my_voice.wav", "reference_voice.wav")
# 📦 O‘rnatish uchun:

# bash
# Copy
# Edit
# pip install speechbrain
# ✅ 3-BO‘LIM: Telefon orqali ovozni olish (VoIP integratsiya)
# Variantlar:
# 🔹 Asterisk + Python:
# Asterisk telefonga kelgan qo‘ng‘iroqni yozib oladi.

# Asterisk AGI orqali Python scriptga uzatadi.

# Siz compare_voices() bilan kimligini aniqlaysiz.

# 🔹 VoIP SIP yozuv:
# Agar sizda SIP tizim bo‘lsa (Zoiper, Linphone, FreePBX), barcha telefon suhbati .wav fayl sifatida saqlanadi — shu faylni avtomatik compare_voices() funksiyasiga yuborasiz.

# ❗ Bu qism texnikroq, agar telefonga real ulashmoqchi bo‘lsangiz — ayting, shunga mos Asterisk konfiguratsiyasini ham tayyorlab beraman.

# ✅ 4-BO‘LIM: Tanilgan shaxsni chiqarish (ID)
# Siz har bir odamni reference_voice_*.wav deb nomlab qo‘yasiz va quyidagicha tekshirasiz:

# identify_speaker.py:
# python
# Copy
# Edit
# import os
# from speechbrain.pretrained import SpeakerRecognition

# def identify_speaker(input_file, reference_dir="voices/"):
#     model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_model")
    
#     best_score = -1
#     best_match = None

#     for ref_file in os.listdir(reference_dir):
#         ref_path = os.path.join(reference_dir, ref_file)
#         score, pred = model.verify_files(input_file, ref_path)
#         if score > best_score:
#             best_score = score
#             best_match = ref_file

#     print(f"🎯 Bu odam ehtimol: {best_match} (score: {best_score:.3f})")

# # Misol
# identify_speaker("my_voice.wav", "voices/")
# ✅ Yakuniy loyiha struktura misoli:
# Copy
# Edit
# project/
# ├── record_voice.py
# ├── compare_voices.py
# ├── identify_speaker.py
# ├── voices/
# │   ├── ulugbek.wav
# │   ├── sardor.wav
# │   └── dilshod.wav
# ❓ Keyingi qadam:
# Sizdan aniqlashtirmoqchi edim:

# Real telefon qo‘ng‘irog‘ini ushlab olish xohlayapsizmi? (Asterisk + SIP)

# Real-time aniqlash kerakmi? (Gapirayotgan zahoti tanish)

# Ovoz fayldan bo‘ladimi, yoki mikrofon orqali har safar yozib olinadimi?

# Shunga qarab kodni keyingi bosqichga tayyorlayman. Tayyor bo‘lsa — tar.gz holida ham barchasini beraman.


# Ask ChatGPT
