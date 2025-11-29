# app.py – Tartan Mirror + Drag & Drop Threadcount Analyse (de toekomst is hier)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import re
from PIL import Image

# === Kleuren (zelfde als voorheen) ===
COLORS = {
    "R": (178, 34, 52), "G": (0, 115, 46), "B": (0, 41, 108), "K": (30, 30, 30),
    "W": (255, 255, 255), "Y": (255, 203, 0), "O": (255, 102, 0), "DB": (0, 20, 60),
    "DG": (0, 70, 35), "LG": (200, 230, 200), "A": (160, 160, 160),
}

# === Threadcount uit afbeelding analyseren ===
def analyze_tartan_image(img):
    img = img.convert("RGB")
    data = np.array(img)
    h, w = data.shape[:2]
    
    # Focus op middelste verticale lijn (meest representatief)
    col = data[h//2, :]
    
    # Detecteer kleurveranderingen
    changes = []
    prev = tuple(col[0])
    count = 1
    for pixel in col[1:]:
        current = tuple(pixel)
        if current != prev:
            changes.append((prev, count))
            prev = current
            count = 1
        else:
            count += 1
    changes.append((prev, count))
    
    # Match met onze COLORS (dichtstbijzijnde)
    def closest_color(rgb):
        min_dist = float('inf')
        best = "K"
        for code, c in COLORS.items():
            dist = sum((a-b)**2 for a,b in zip(rgb, c))
            if dist < min_dist:
                min_dist = dist
                best = code
        return best
    
    # Bouw threadcount string
    tc_parts = []
    for (r,g,b), cnt in changes:
        color_code = closest_color((r,g,b))
        tc_parts.append(f"{color_code}{cnt}")
    
    return " ".join(tc_parts)

# === Rest van de tartan-functies (zelfde als voorheen, ingekort) ===
def parse_threadcount(tc: str): ...  # (jouw bestaande functie)
def build_sett(pattern): ...         # (jouw bestaande functie)
def create_tartan(...): ...          # (jouw bestaande functie met zichtbare draden)

# === UI MET DRAG & DROP BOVENAAN ===
st.set_page_config(page_title="Tartan Mirror + Foto Analyse", layout="centered")
st.title("Tartan Mirror + Sleep een foto → krijg threadcount")

# === DRAG & DROP ZONE ===
uploaded_file = st.file_uploader(
    "Sleep een tartan-foto hierheen (of klik om te kiezen)",
    type=["png", "jpg", "jpeg", "webp"],
    help="Sleep een duidelijke tartan-foto in – liefst recht van voren, goed verlicht"
)

detected_tc = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Jouw foto", use_column_width=True)
    
    with st.spinner("Analyseren van threadcount..."):
        detected_tc = analyze_tartan_image(image)
    
    st.success(f"Threadcount gedetecteerd: `{detected_tc}`")
    st.code(detected_tc, language=None)

# === Normale invoer (nu met auto-fill als er iets gedetecteerd is) ===
default_tc = detected_tc if detected_tc else "R28 W4 R8 Y4 R28 K32"
tc = st.text_input("Threadcount (of pas aan na analyse)", value=default_tc)

col1, col2 = st.columns([3, 1])
with col1:
    pass  # lege ruimte voor balans
with col2:
    thread_width = st.slider("Draad-dikte", 4, 20, 10)
    texture = st.checkbox("Wol-textuur", True)
    twill_strength = st.slider("Twill sterkte", 0.4, 1.0, 0.82, 0.01)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan_with_threads(pattern, size=900, thread_width=thread_width,
                                        texture=texture, twill_strength=twill_strength)
        st.image(img, use_column_width=True)
        
        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download (900×900)", buf,
                           file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

st.caption("Sleep een foto van een kilt, sjaal of stof → krijg direct de threadcount. Werkt het best met duidelijke, rechte tartans.")



