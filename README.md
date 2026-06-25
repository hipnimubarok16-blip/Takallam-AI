# Takallam-AI
Teman berbicara anda ketika belajar bahasa arab 
# 💬 Takallam AI - Pelatihan Maharah Kalam Virtual

Takallam AI adalah aplikasi berbasis web interaktif yang dirancang khusus sebagai tutor virtual untuk melatih **Maharah Kalam** (keterampilan berbicara) siswa kelas 10 Madrasah Aliyah (MA). Aplikasi ini terintegrasi langsung dengan Google Gemini API dan menggunakan pendekatan interaktif berbasis teks serta suara (*multimodal*).

## 🌟 Fitur Utama
* **Antarmuka Interaktif:** Desain spatial dengan penulisan Arab otomatis rata kanan (RTL) dan evaluasi bahasa Indonesia rata kiri (LTR).
* **Pilihan Mentor Persona:** Siswa dapat memilih belajar bersama **Ust. Hipni Mubarok, S.Pd.** atau **Ustadzah Fatimah, Lc.** dengan gaya mengajar yang unik.
* **Integrasi Audio (Text-to-Speech):** Setiap respons dari guru dapat didengarkan langsung pelafalan makhrajnya yang fasih melalui tombol speaker.
* **Fitur Voice Note (Multimodal Speech-to-Text):** Siswa dapat menjawab langsung menggunakan mikrofon (rekaman suara), dan Ustadz/Ustadzah akan mengevaluasi serta merespons audio tersebut.
* **5 Mode Pembelajaran Kelas 10 MA:**
  1. التعارف (Perkenalan Diri)
  2. الحياة اليومية في المدرسة (Kehidupan di Sekolah)
  3. النشاطات في العطلة (Aktivitas Liburan)
  4. الهواية والتطلعات (Hobi dan Cita-cita)
  5. الأسرة والبيت (Keluarga dan Rumah)

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Prasyarat (Prerequisites)
Pastikan perangkat Anda sudah terinstal Python (versi 3.9 ke atas direkomendasikan).

### 2. Kloning atau Siapkan Folder Proyek
Pastikan file utama Anda diberi nama `gemini.py`.

### 3. Instalasi Library Dependensi
Buka Terminal / Command Prompt (CMD) di folder proyek tersebut, lalu instal pustaka wajib berikut:
```bash
pip install streamlit google-generativeai streamlit-tts streamlit-mic-recorder
