# app.py – Tartan Mirror + Drag & Drop Foto → Threadcount + Zichtbare Draden
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import re
from PIL import Image

# === Kleuren ===
COLORS = {
    "R": (178, 34, 52), "G": (0, 115, 46), "B": (0, 41, 108), "K": (30, 30, 30),
    "W": (255, 255, 255), "Y": (255, 203, 0), "O": (255, 102, 0), "DB": (0, 20, 60),
    "DG": (0, 70, 35), "LG": (200, 230, 200), "A": (160, 160, 160),
}

def parse_threadcount(tc: str):
    cleaned = re.sub(r'[,\s]+', ' ', tc.strip())
    parts = cleaned.upper().split()
    pattern = []
    for part in parts:
        if not part: continue
        color = None
        num_str = part
        for c in sorted(COLORS.keys(), key=len, reverse=True):
            if part.startswith(c):
                color = c; num_str = part[len(c):]; break
            if part.endswith(c):
                color = c; num_str = part[:-len(c)]; break
        if color is None:
            st.error(f"Kleur niet herkend: '{part}'"); return None
        count = 1.0 if not num_str else (int(num_str.split('/')[1])/2 if '/' in num_str else float(num_str))
        pattern.append((color, count))
    return pattern

def build_sett(pattern):
    f_counts = [c for _, c in pattern]
    f_colors  = [col for col, _ in pattern]
    return f_counts + f_counts[::-1][1:], f_colors + f_colors[::-1][1:]

# === Foto analyseren → Threadcount ===
def analyze_tartan_image(img):
    img = img.convert("RGB")
    data = np.array(img)
    h, w = data.shape[:2]
    col = data[h//2, :]
    
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
    
    def closest_color(rgb):
        min_dist = float('inf')
        best = "K"
        for code, c in COLORS.items():
            dist = sum((a-b)**2 for a,b in zip(rgb, c))
            if dist < min_dist:
                min_dist = dist
                best = code
        return best
    
    tc_parts = []
    for (r,g,b), cnt in changes:
        if cnt > 2:  # negeer ruis
            color_code = closest_color((r,g,b))
            tc_parts.append(f"{color_code}{cnt}")
    
    return " ".join(tc_parts) if tc_parts else "K100"

# === Tartan met zichtbare draden (jouw gewenste look) ===
def create_tartan_with_threads(pattern, size=900, thread_width=10, texture=True, twill_strength=0.82):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(3, int(round(c * thread_width))) for c in sett_counts]
    sett_w = sum(widths)
    repeats = max(2, (size // sett_w) + 2)

    tile = np.zeros((sett_w * repeats, sett_w * repeats, 3), dtype=np.uint16)
    x = 0
    for _ in range(repeats):
        for w, col in zip(widths, sett_colors):
            tile[:, x:x+w] = COLORS[col]
            x += w

    weft = tile.copy().transpose(1, 0, 2)
    tartan = np.minimum(tile + weft, 255).astype(np.uint8)

    # Sterke 2/2 twill + draadranden
    h, w = tartan.shape[:2]
    y, x = np.indices((h, w))
    mask = ((x + y) % 4 < 2)

    img_f = tartan.astype(np.float32)
    shadow = img_f * (1.0 - twill_strength)
    highlight = np.clip(img_f * (1.0 + twill_strength * 2.0), 0, 255)
    twill = np.where(mask[..., np.newaxis], highlight, shadow)

    # Sterke draadranden
    edges = np.zeros_like(twill)
    edges[1:,:] += np.abs(twill[1:,:] - twill[:-1,:]).astype(np.int16)
    edges[:,1:] += np.abs(twill[:,1:] - twill[:,:-1]).astype(np.int16)
    edges = np.clip(edges.sum(axis=2, keepdims=True), 0, 90)
    twill = np.clip(twill.astype(np.int16) + edges * 1.4, 0, 255).astype(np.uint8)

    if texture:
        noise = np.random.randint(-18, 24, twill.shape, dtype=np.int16)
        twill = np.clip(twill.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    start = (twill.shape[0] - size) // 2
    return twill[start:start+size, start:start+size]

# === UI ===
st.set_page_config(page_title="Tartan Foto → Threadcount", layout="centered")
st.title("Sleep een tartan-foto → krijg direct de threadcount")

# === DRAG & DROP ===
uploaded_file = st.file_uploader(
    "Sleep een tartan-foto hier (of klik)",
    type=["png", "jpg", "jpeg", "webp", "bmp"],
    help="Hoe scherper en rechter de foto, hoe beter de analyse"
)

detected_tc = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Jouw foto", use_column_width=True)
    with st.spinner("Analyseren..."):
        detected_tc = analyze_tartan_image(image)
    st.success(f"Gedetecteerde threadcount: `{detected_tc}`")
    st.code(detected_tc)

# === Invoer ===
default_tc = detected_tc if detected_tc else "R28 W4 R8 Y4 R28 K32"
tc = st.text_input("Threadcount (bewerk gerust)", value=default_tc)

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
        st.download_button("Download (900×900)", buf,
                           file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

st.success("Sleep een foto → krijg threadcount → zie je tartan. De toekomst is hier.")
