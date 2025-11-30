# app.py – Terug naar de pure, perfecte versie (geen foto-upload)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# === Kleuren ===
COLORS = {
    "R": (178, 34, 52), "G": (0, 115, 46), "B": (0, 41, 108), "K": (30, 30, 30),
    "W": (255, 255, 255), "Y": (255, 203, 0), "O": (255, 102, 0), "DB": (0, 20, 60),
    "DG": (0, 70, 35), "LG": (200, 230, 200), "A": (160, 160, 160), "P": (128, 0, 128),
}

def parse_threadcount(tc: str):
    parts = tc.strip().upper().replace(',', ' ').split()
    pattern = []
    for part in parts:
        if not part: continue
        color = None
        num_str = part
        for c in sorted(COLORS.keys(), key=len, reverse=True):
            if part.startswith(c): color = c; num_str = part[len(c):]; break
            if part.endswith(c): color = c; num_str = part[:-len(c)]; break
        if color is None: st.error(f"Kleur niet herkend: '{part}'"); return None
        count = 1.0 if not num_str else (int(num_str.split('/')[1])/2 if '/' in num_str else float(num_str))
        pattern.append((color, count))
    return pattern

def build_sett(pattern):
    f_counts = [c for _, c in pattern]
    f_colors  = [col for col, _ in pattern]
    return f_counts + f_counts[::-1][1:], f_colors + f_colors[::-1][1:]

def create_tartan(pattern, size=900, thread_width=12, texture=True, twill_strength=0.85):
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

    # Sterke, zichtbare 2/2 twill
    h, w = tartan.shape[:2]
    y, x = np.indices((h, w))
    mask = ((x + y) % 4 < 2)
    img_f = tartan.astype(np.float32)
    shadow = img_f * (1.0 - twill_strength)
    highlight = np.clip(img_f * (1.0 + twill_strength * 2.0), 0, 255)
    twill = np.where(mask[..., np.newaxis], highlight, shadow)

    # Draadranden
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
st.set_page_config(page_title="Tartan Mirror – Pure & Perfect", layout="centered")
st.title("Tartan Mirror – Pure Threadcount Edition")

tc = st.text_input("Threadcount", value="R28 W4 R8 Y4 R28 K32", help="bijv. DB4 G28 DB4 G6 DB28 K6")

col1, col2 = st.columns([3, 1])
with col2:
    thread_width = st.slider("Draad-dikte", 4, 25, 12)
    texture = st.checkbox("Wol-textuur", True)
    twill_strength = st.slider("Twill sterkte", 0.4, 1.0, 0.85, 0.01)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, thread_width=thread_width,
                           texture=texture, twill_strength=twill_strength)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download tartan 900×900", buf,
                           file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

st.caption("Geen foto’s. Geen poespas. Alleen pure tartan-magie.")
