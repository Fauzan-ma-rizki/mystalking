import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests

# --- LOGIKA FOTO ---
def get_gps_data(image):
    exif = image._getexif()
    if not exif: return None
    gps_info = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    gps_info[val] = exif[idx][key]
    return gps_info

def convert_to_degrees(value):
    try:
        d, m, s = float(value[0]), float(value[1]), float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except: return 0.0

def get_lat_lon(gps_info):
    try:
        lat = convert_to_degrees(gps_info['GPSLatitude'])
        if gps_info.get('GPSLatitudeRef') != 'N': lat = -lat
        lon = convert_to_degrees(gps_info['GPSLongitude'])
        if gps_info.get('GPSLongitudeRef') != 'E': lon = -lon
        return lat, lon
    except: return None

# --- UI ---
st.set_page_config(page_title="Mata Fauzan Pro", page_icon="👁️")
st.title("👁️ Mata Fauzan - Tracking Mode")

mode = st.sidebar.radio("Pilih Mode:", ["📸 Foto GPS", "🌐 IP Tracker"])

if mode == "📸 Foto GPS":
    st.header("Pelacakan Foto")
    up = st.file_uploader("Upload Foto Asli (Document)", type=["jpg", "jpeg", "png"])
    if up:
        img = Image.open(up)
        st.image(img, width=400)
        exif = img._getexif()
        if exif:
            gps = get_gps_data(img)
            info_hp = {TAGS.get(i): exif.get(i) for i in exif}
            st.write(f"**HP:** {info_hp.get('Make')} {info_hp.get('Model')}")
            if gps:
                coords = get_lat_lon(gps)
                st.success(f"Lokasi: {coords[0]}, {coords[1]}")
                st.map({"lat": [coords[0]], "lon": [coords[1]]})
            else: st.warning("Tidak ada data GPS.")
        else: st.error("Metadata tidak ditemukan.")

elif mode == "🌐 IP Tracker":
    st.header("Lacak Alamat IP")
    ip_in = st.text_input("Masukkan IP:")
    if st.button("Lacak") and ip_in:
        res = requests.get(f"http://ip-api.com/json/{ip_in}").json()
        if res['status'] == 'success':
            st.write(f"**Kota:** {res['city']}, {res['country']}")
            st.write(f"**ISP:** {res['isp']}")
            st.map({"lat": [res['lat']], "lon": [res['lon']]})

st.sidebar.caption("Mata Fauzan")
