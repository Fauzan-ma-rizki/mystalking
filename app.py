import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from io import BytesIO
import requests

# --- FUNGSI LOGIKA AMAN ---

def get_gps_data(image_bytes):
    try:
        # Membuka gambar dari bytes agar lebih stabil di Streamlit
        image = Image.open(BytesIO(image_bytes))
        exif = image._getexif()
        
        if not exif:
            return None, None
        
        # Ambil informasi perangkat secara aman
        info_hp = {}
        for (idx, tag) in TAGS.items():
            val = exif.get(idx) # Menggunakan .get() agar tidak KeyError
            if val is not None:
                info_hp[tag] = val
        
        # Ambil informasi GPS secara mendalam
        gps_info = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                # Bagian ini yang sering bikin KeyError, sekarang diproteksi .get()
                gps_data = exif.get(idx)
                if gps_data and isinstance(gps_data, dict):
                    for (key, val) in GPSTAGS.items():
                        if key in gps_data:
                            gps_info[val] = gps_data[key]
                    return gps_info, info_hp
        
        return None, info_hp
    except Exception as e:
        # Jika ada error tak terduga, aplikasi tidak akan mati
        return None, None

def convert_to_degrees(value):
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except (TypeError, IndexError, ZeroDivisionError):
        return None

# --- ANTARMUKA STREAMLIT ---

st.set_page_config(page_title="Mata Fauzan Pro", page_icon="👁️")

# Custom CSS untuk Header
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>👁️ Mata Fauzan</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Analisis Lokasi Foto & Pelacakan IP</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Menu Utama")
    mode = st.radio("Pilih Mode:", ["📸 Deteksi Foto", "🌐 Lacak IP"])
    st.divider()
    st.caption("Aplikasi ini didesain untuk mendeteksi metadata asli (Original File).")

# --- MODE FOTO ---
if mode == "📸 Deteksi Foto":
    st.subheader("📸 Mode Deteksi Foto GPS")
    uploaded_file = st.file_uploader("Upload Foto Asli (Kirim via Document WA)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        file_bytes = uploaded_file.read()
        gps, info_hp = get_gps_data(file_bytes)
        
        st.image(file_bytes, use_container_width=True)
        
        if info_hp:
            st.success("Metadata Terdeteksi!")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Merk HP:** {info_hp.get('Make', 'Tidak Diketahui')}")
            with c2:
                st.write(f"**Model:** {info_hp.get('Model', 'Tidak Diketahui')}")
            
            if gps:
                lat = convert_to_degrees(gps.get('GPSLatitude'))
                lon = convert_to_degrees(gps.get('GPSLongitude'))
                
                if lat is not None and lon is not None:
                    # Menyesuaikan arah mata angin
                    if gps.get('GPSLatitudeRef') != 'N': lat = -lat
                    if gps.get('GPSLongitudeRef') != 'E': lon = -lon
                    
                    st.divider()
                    st.subheader("📍 Lokasi Ditemukan!")
                    st.code(f"Lat: {lat}, Lon: {lon}")
                    st.map({"lat": [lat], "lon": [lon]})
                    st.markdown(f"[🌍 Buka Langsung di Google Maps](https://www.google.com/maps?q={lat},{lon})")
                else:
                    st.warning("⚠️ Data koordinat tidak lengkap.")
            else:
                st.warning("⚠️ Tidak ditemukan data lokasi GPS pada foto ini.")
        else:
            st.error("❌ File tidak memiliki metadata EXIF (Kemungkinan screenshot atau sudah dikompres).")

# --- MODE IP ---
elif mode == "🌐 Lacak IP":
    st.subheader("🌐 Mode Pelacakan IP")
    ip_address = st.text_input("Masukkan Alamat IP:", placeholder="8.8.8.8")
    
    if st.button("Lacak Lokasi IP"):
        if ip_address:
            try:
                res = requests.get(f"http://ip-api.com/json/{ip_address}").json()
                if res['status'] == 'success':
                    st.success(f"Lokasi: {res['city']}, {res['country']}")
                    st.write(f"**ISP:** {res['isp']}")
                    st.map({"lat": [res['lat']], "lon": [res['lon']]})
                else:
                    st.error("IP tidak ditemukan.")
            except:
                st.error("Gagal menghubungi server pelacak.")

st.divider()
st.caption("Mata Fauzan v3.3 | Stable Release")
