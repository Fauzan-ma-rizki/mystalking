import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from io import BytesIO
import requests

# --- FUNGSI LOGIKA (VERSI AMAN) ---
def get_gps_data(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes))
        exif = image._getexif()
        if not exif:
            return None, None
        
        # Ambil info HP dengan aman
        info_hp = {}
        for (idx, tag) in TAGS.items():
            val = exif.get(idx)
            if val:
                info_hp[tag] = val
        
        # Ambil info GPS dengan aman (Cegah KeyError)
        gps_info = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                gps_data = exif.get(idx) # Gunakan .get() biar gak crash
                if gps_data and isinstance(gps_data, dict):
                    for (key, val) in GPSTAGS.items():
                        if key in gps_data:
                            gps_info[val] = gps_data[key]
                    return gps_info, info_hp
        return None, info_hp
    except Exception as e:
        return None, None

def convert_to_degrees(value):
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except:
        return None

# --- UI MATA FAUZAN ---
st.set_page_config(page_title="Mata Fauzan Pro", page_icon="👁️", layout="centered")

st.markdown("<h1 style='text-align: center;'>👁️ Mata Fauzan</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>OSINT Tool: Photo & IP Tracker</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Navigasi")
    mode = st.radio("Pilih Mode Pelacakan:", ["📸 Foto GPS", "🌐 IP Tracker"])
    st.markdown("---")
    st.caption("Tips: Kirim foto via 'Document' WhatsApp agar metadata tidak hilang.")

# --- MODE 1: FOTO ---
if mode == "📸 Foto GPS":
    st.subheader("📸 Analisis Metadata Foto")
    up = st.file_uploader("Upload Foto (.jpg, .jpeg, .png)", type=["jpg", "jpeg", "png"])
    
    if up:
        file_bytes = up.read()
        gps, info_hp = get_gps_data(file_bytes)
        
        st.image(file_bytes, use_container_width=True)
        
        if info_hp:
            st.success("✅ Metadata Berhasil Dibaca")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**📱 Merk:** {info_hp.get('Make', 'N/A')}")
            with col2:
                st.info(f"**📱 Model:** {info_hp.get('Model', 'N/A')}")
            
            if gps:
                lat = convert_to_degrees(gps.get('GPSLatitude'))
                lon = convert_to_degrees(gps.get('GPSLongitude'))
                
                if lat is not None and lon is not None:
                    # Cek arah (N/S, E/W)
                    if gps.get('GPSLatitudeRef') != 'N': lat = -lat
                    if gps.get('GPSLongitudeRef') != 'E': lon = -lon
                    
                    st.subheader("📍 Lokasi Ditemukan")
                    st.write(f"Koordinat: `{lat}, {lon}`")
                    st.map({"lat": [lat], "lon": [lon]})
                    st.markdown(f"[🔗 Buka di Google Maps](https://www.google.com/maps?q={lat},{lon})")
                else:
                    st.warning("⚠️ Koordinat GPS tidak lengkap atau rusak.")
            else:
                st.warning("⚠️ Foto ini tidak mengandung data lokasi (GPS).")
        else:
            st.error("❌ Gagal mengambil metadata. Pastikan file bukan hasil screenshot.")

# --- MODE 2: IP ---
elif mode == "🌐 IP Tracker":
    st.subheader("🌐 Pelacakan Alamat IP")
    ip_in = st.text_input("Masukkan IP Target:", placeholder="Contoh: 114.124.xxx.xxx")
    
    if st.button("Lacak IP") and ip_in:
        try:
            res = requests.get(f"http://ip-api.com/json/{ip_in}", timeout=10).json()
            if res.get('status') == 'success':
                st.success(f"📍 IP Berasal dari {res['city']}, {res['country']}")
                
                c1, c2 = st.columns(2)
                c1.write(f"**ISP:** {res.get('isp')}")
                c2.write(f"**Timezone:** {res.get('timezone')}")
                
                st.map({"lat": [res['lat']], "lon": [res['lon']]})
            else:
                st.error("❌ IP tidak valid atau tidak terdaftar.")
        except:
            st.error("❌ Gagal menghubungkan ke server pelacak.")

st.markdown("---")
st.caption("Mata Fauzan")
