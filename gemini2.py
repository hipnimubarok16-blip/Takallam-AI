import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Takallam AI - Pelatihan Maharah Kalam",
    page_icon="💬",
    layout="centered"
)

# --- CSS KUSTOM UNTUK DESAIN GRAFIS & TATA LETAK ---
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#1B5E20, #4CAF50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666666;
        text-align: center;
        margin-bottom: 25px;
        font-style: italic;
    }
    .arabic-text {
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', 'Traditional Arabic', serif;
        font-size: 1.4rem;
        color: #1B5E20;
        margin-bottom: 8px;
        line-height: 1.8;
    }
    .indonesia-text {
        direction: ltr;
        text-align: left;
        font-size: 1rem;
        color: #444444;
        background-color: #F1F8E9;
        padding: 8px 12px;
        border-left: 4px solid #8BC34A;
        border-radius: 4px;
        margin-bottom: 5px;
    }
    .teacher-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin-bottom: 20px;
    }
    div[data-testid="stChatMessage"] {
        background-color: #F9F9F9;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT ENGINE (AUDIO TTS & REAL-TIME STT) ---
# Berfungsi menjembatani mikrofon browser langsung ke elemen teks input Streamlit
components.html("""
    <script>
    // Fungsi Suara Guru (Text to Speech)
    window.speakArabic = function(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Hentikan suara sebelumnya jika ada
            var msg = new SpeechSynthesisUtterance(text);
            msg.lang = 'ar-SA'; 
            msg.pitch = 1.0;
            msg.rate = 0.85; // Kecepatan ideal untuk anak MA
            window.speechSynthesis.speak(msg);
        } else {
            alert("Browser Anda tidak mendukung fitur suara.");
        }
    };

    // Fungsi Perekam Suara Siswa (Speech to Text)
    window.aktifkanPerekaman = function() {
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'ar-SA'; 
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            var statusDiv = window.parent.document.getElementById("stt-indicator");
            if(statusDiv) statusDiv.innerHTML = "🔴 <b>Mendengarkan... Silakan berbicara dalam Bahasa Arab sekarang!</b>";
        };

        recognition.onerror = function(event) {
            var statusDiv = window.parent.document.getElementById("stt-indicator");
            if(statusDiv) statusDiv.innerHTML = "❌ Gagal merekam. Pastikan izin mikrofon aktif. (Error: " + event.error + ")";
        };

        recognition.onresult = function(event) {
            var hasilTeks = event.results[0][0].transcript;
            
            // Masukkan teks suara langsung ke dalam text area input chat Streamlit
            var stInput = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (stInput) {
                stInput.value = hasilTeks;
                stInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                var statusDiv = window.parent.document.getElementById("stt-indicator");
                if(statusDiv) statusDiv.innerHTML = "✅ Berhasil mengubah suara menjadi teks! Silakan klik tombol kirim di kolom chat.";
            } else {
                alert("Gagal menemukan kolom chat. Silakan ketik manual hasil ini: " + hasilTeks);
            }
        };

        recognition.start();
    };
    </script>
""", height=0)

# --- INITIALIZATION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = ""

# --- PROMPT MATERIAL & PERSONA ---
PROMPT_USTADZ = {
    "Ust Hipni Mubarok S.Pd": "Nama Anda adalah Ust Hipni Mubarok S.Pd. Gaya mengajar Anda sangat suportif, interaktif, memotivasi, dan fokus pada penerapan kaidah tata bahasa (qowaid) praktis.",
    "Ustadzah Fatimah Lc": "Nama Anda adalah Ustadzah Fatimah Lc. Anda adalah lulusan universitas Timur Tengah. Gaya mengajar Anda anggun, fasih, menggunakan aksen (lahjah) standar yang tinggi, dan berfokus pada kelancaran kosakata."
}

BASE_PROMPT = """
Anda adalah tutor bahasa Arab virtual untuk melatih 'Maharah Kalam' siswa kelas 10 Madrasah Aliyah (MA). 

FORMAT ATURAN MERESPONS (WAJIB):
Setiap kali Anda memberikan respons, pisahkan dengan tegas menjadi dua bagian menggunakan tanda hubung (---):
1. Bagian Bahasa Arab (Baris Atas): Tulis teks bahasa Arab yang fasih berharakat lengkap.
2. Bagian Terjemahan & Evaluasi (Baris Bawah): Tulis terjemahan Indonesia beserta umpan balik/evaluasi lembut terhadap jawaban siswa.

Contoh Format:
[Teks Arab berharakat]
---
[Terjemahan dan koreksi bahasa Indonesia]
"""

MODE_PROMPTS = {
    "التعارف (Perkenalan Diri)": "Topik perkenalan diri, hobi, tempat tinggal, dan cita-cita siswa kelas 10 MA.",
    "الحياة اليومية في المدرسة (Kehidupan di Sekolah)": "Aktivitas di Madrasah Aliyah, fasilitas madrasah, dan mata pelajaran favorit.",
    "النشاطات في العطلة (Aktivitas Liburan)": "Kegiatan produktif saat libur sekolah atau tempat wisata yang dikunjungi.",
    "الهواية والتطلعات (Hobi dan Cita-cita)": "Membahas hobi yang bermanfaat dan cita-cita profesi masa depan.",
    "الأسرة والبيت (Keluarga dan Rumah)": "Menceritakan tentang keadaan rumah dan kedekatan dengan anggota keluarga."
}

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🔑 Akses & Akun</div>", unsafe_allow_html=True)
    username = st.text_input("Username Siswa:", key="username_input", placeholder="Nama Lengkap")
    api_key = st.text_input("Gemini API Key:", type="password", placeholder="AIzaSy...")
    
    st.markdown("---")
    st.markdown("<div class='sidebar-title'>👨‍🏫 Pilih Guru Pendamping</div>", unsafe_allow_html=True)
    pilihan_guru = st.radio("Pilih Ustadz/Ustadzah:", options=list(PROMPT_USTADZ.keys()))
    
    st.markdown("---")
    st.markdown("<div class='sidebar-title'>📚 Topik Materi MA</div>", unsafe_allow_html=True)
    selected_mode = st.selectbox("Pilih Materi Kalam:", options=list(MODE_PROMPTS.keys()))
    
    st.markdown("---")
    if st.button("🔄 Reset Sesi Belajar", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- FUNGSI CORE ENGINE API ---
def panggil_gemini_api(key_user, prompt_text):
    clean_key = key_user.strip()
    genai.configure(api_key=clean_key)
    daftar_model = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-pro']
    
    for nama_model in daftar_model:
        try:
            model = genai.GenerativeModel(nama_model)
            response = model.generate_content(prompt_text)
            return response.text
        except:
            continue 
    raise Exception("Gagal terhubung dengan API. Periksa kembali validitas Key Anda.")

# --- HALAMAN UTAMA ---
st.markdown("<div class='main-title'>💬 Takallam AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Teman Praktik Bicara Bahasa Arab Kelas 10 MA</div>", unsafe_allow_html=True)

# Proteksi Login
if not username or not api_key:
    st.warning("👋 Selamat datang! Silakan tentukan **Username**, masukkan **API Key**, dan pilih **Guru Pendamping** di menu sebelah kiri untuk memulai kelas.")
    st.stop()

# Tampilan Info Mentor Atas
st.markdown(f"""
<div class='teacher-card'>
    🎯 <b>Guru Pendamping:</b> {pilihan_guru} | 📖 <b>Materi:</b> {selected_mode}
</div>
""", unsafe_allow_html=True)

# Otomatis reset chat jika murid ganti guru/materi
if st.session_state.current_mode != f"{selected_mode}_{pilihan_guru}":
    st.session_state.current_mode = f"{selected_mode}_{pilihan_guru}"
    st.session_state.messages = []

# Sapaan Pembuka Otomatis Saat Pertama Masuk Kelas
if len(st.session_state.messages) == 0:
    with st.spinner("Menghubungkan dengan Ustadz..."):
        try:
            system_instruction = f"{BASE_PROMPT}\nPersona Guru: {PROMPT_USTADZ[pilihan_guru]}\nTopik Bahasan: {MODE_PROMPTS[selected_mode]}"
            prompt_awal = f"{system_instruction}\n\nSapa murid bernama {username} dengan ramah. Ajukan pertanyaan pembuka pertama mengenai topik {selected_mode} menggunakan format wajib!"
            
            pembuka_text = panggil_gemini_api(api_key, prompt_awal)
            st.session_state.messages.append({"role": "assistant", "content": pembuka_text})
            
            # Putar audio otomatis di browser
            bagian_arab = pembuka_text.split("---")[0].strip().replace("`","'").replace("\n"," ")
            components.html(f"<script>window.parent.speakArabic(`{bagian_arab}`);</script>", height=0)
        except Exception as e:
            st.error("Koneksi gagal. Periksa kembali API Key Anda.")
            st.stop()

# --- MENAMPILKAN RIWAYAT CHAT (RTL ARAB & LTR INDONESIA) ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            parts = msg["content"].split("---")
            arab_part = parts[0].strip()
            indo_part = parts[1].strip() if len(parts) > 1 else ""
            
            st.markdown(f"<div class='arabic-text'>{arab_part}</div>", unsafe_allow_html=True)
            if indo_part:
                st.markdown(f"<div class='indonesia-text'>{indo_part}</div>", unsafe_allow_html=True)
            
            # FITUR BARU: Tombol Speaker Interaktif per Jawaban Guru
            clean_arab_speech = arab_part.replace("`","'").replace("\n"," ")
            if st.button(f"🔊 Dengarkan Pelafalan Guru", key=f"btn_{idx}"):
                components.html(f"<script>window.parent.speakArabic(`{clean_arab_speech}`);</script>", height=0)
        else:
            # Sisi Chat Siswa
            st.markdown(f"<div class='arabic-text' style='color:#0D47A1;'>{msg['content']}</div>", unsafe_allow_html=True)

# --- PANEL FITUR MIKROFON / VOICE NOTE ---
st.markdown("---")
st.write("🎙️ **Pelatihan Kelancaran Lisan (Voice Note):**")

# Wadah Indikator Status Perekaman Suara Real-time HTML
st.markdown("<div id='stt-indicator' style='color: #2E7D32; font-weight: bold; margin-bottom: 10px;'>Status: Siap Menerima Suara</div>", unsafe_allow_html=True)

if st.button("🔴 Mulai Rekam Suara Anda", use_container_width=True):
    components.html("<script>window.parent.aktifkanPerekaman();</script>", height=0)

# --- KOLOM INPUT UTAMA ---
user_input = st.chat_input("Tulis atau gunakan mikrofon untuk menjawab...")

if user_input:
    # Tampilkan input teks/suara siswa ke layar
    with st.chat_message("user"):
        st.markdown(f"<div class='arabic-text' style='color:#0D47A1;'>{user_input}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Kirim ke AI dan dapatkan respons balasan
    with st.chat_message("assistant"):
        with st.spinner("Ustadz sedang menyimak & menganalisis makhraj..."):
            try:
                system_instruction = f"{BASE_PROMPT}\nPersona Guru: {PROMPT_USTADZ[pilihan_guru]}\nTopik Bahasan: {MODE_PROMPTS[selected_mode]}"
                full_context = system_instruction + "\n\n"
                for m in st.session_state.messages[:-1]:
                    full_context += f"{m['role']}: {m['content']}\n"
                full_context += f"user ({username}): {user_input}\nassistant:"
                
                balasan_text = panggil_gemini_api(api_key, full_context)
                
                parts = balasan_text.split("---")
                arab_part = parts[0].strip()
                indo_part = parts[1].strip() if len(parts) > 1 else ""
                
                # Tampilkan Teks Arab Kanan & Indonesia Kiri
                st.markdown(f"<div class='arabic-text'>{arab_part}</div>", unsafe_allow_html=True)
                if indo_part:
                    st.markdown(f"<div class='indonesia-text'>{indo_part}</div>", unsafe_allow_html=True)
                
                # Simpan ke memori sesi
                st.session_state.messages.append({"role": "assistant", "content": balasan_text})
                
                # Picu audio otomatis untuk respons terbaru
                clean_arab_auto = arab_part.replace("`","'").replace("\n"," ")
                components.html(f"<script>window.parent.speakArabic(`{clean_arab_auto}`);</script>", height=0)
                st.rerun() # Refresh agar tombol dengarkan di chat terbaru langsung muncul
                
            except Exception as e:
                st.error(f"Koneksi terputus: {e}")