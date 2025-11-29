# app.py – Tartan Foto → Threadcount + Kleine foto met zoom
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import re
from PIL import Image

# === Kleuren & functies (zelfde als voorheen) ===
COLORS = {
    "R": (178, 34, 52), "G": (0, 115, 46), "B": (0, 41, 108), "K": (30, 30, 30),
    "W": (255, 255, 255), "Y": (255, 203, 0), "O": (255, 102, 0), "DB": (0, 20, 60),
    "DG": (0, 70, 35), "LG": (200, 230, 200), "A": (160, 160, 160),
}

def parse_threadcount(tc: str): ...  # (jouw bestaande functie)
def build_sett(pattern): ...         # (jouw bestaande functie)

def analyze_tartan_image(img): ...   # (jouw bestaande functie)

def create_tartan_with_threads(...): ...  # (jouw bestaande functie met zichtbare draden)

# === UI ===
st.set_page_config(page_title="Tartan Foto → Threadcount", layout="centered")
st.title("Sleep een tartan-foto → krijg threadcount")

# === DRAG & DROP ===
uploaded_file = st.file_uploader(
    "Sleep een tartan-foto hier",
    type=["png", "jpg", "jpeg", "webp", "bmp"],
    help="Hoe scherper en rechter, hoe beter"
)

detected_tc = None
zoomed_image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Kleine thumbnail (max 300px breed)
    display_img = image.copy()
    display_img.thumbnail((300, 1000), Image.Resampling.LANCZOS)
    
    # Zoom slider
    zoom = st.slider("Zoom foto", 100, 500, 150, 10, help="150% = mooi detail")
    zoomed_width = int(display_img.width * zoom / 100)
    zoomed_height = int(display_img.height * zoom / 100)
    zoomed_image = display_img.resize((zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
    
    st.image(zoomed_image, caption="Jouw foto (zoombaar)", use_column_width=True)
    
    with st.spinner("Analyseren van threadcount..."):
        detected_tc = analyze_tartan_image(image)
    st.success(f"Gedetecteerd: `{detected_tc}`")
    st.code(detected_tc)

# === Threadcount invoer ===
default_tc = detected_tc if detected_tc else "R28 W4 R8 Y4 R28 K32"
tc = st.text_input("Threadcount (pas aan indien nodig)", value=default_tc)

col1, col2 = st.columns([3, 1])
with col2:
    thread_width = st.slider("Draad-dikte", 4, 25, 12)
    texture = st.checkbox("Wol-textuur", True)
    twill_strength = st.slider("Twill sterkte", 0.4, 1.0, 0.85, 0.01)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan_with_threads(pattern, size=900, thread_width=thread_width,
                                        texture=texture, twill_strength=twill_strength)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download tartan", buf,
                           file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

st.caption("Zoom in op je foto om te controleren of de analyse klopt – en pas de threadcount handmatig aan als dat nodig is.")
