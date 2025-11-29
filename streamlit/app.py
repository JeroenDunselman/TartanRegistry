# app.py – Echte Tartan Mirror + Super Realistische Twill (2025)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import re

# === Authentieke Schotse kleuren ===
COLORS = {
    "R": (178, 34, 52), "DR": (120, 0, 0), "G": (0, 115, 46), "DG": (0, 70, 35),
    "B": (0, 41, 108), "DB": (0, 20, 60), "K": (30, 30, 30), "W": (255, 255, 255),
    "Y": (255, 203, 0), "O": (255, 102, 0), "P": (128, 0, 128), "LG": (200, 230, 200),
    "LB": (180, 200, 230), "A": (160, 160, 160), "T": (0, 130, 130),
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

# === SUPER REALISTISCHE TWILL (dit is wat je wilde!) ===
def add_twill_pattern(img, strength=0.50):
    if strength <= 0:
        return img.copy()

    h, w = img.shape[:2]
    y, x = np.indices((h, w))
    twill_mask = ((x + y) % 4 < 2)  # 2/2 keperbinding

    img_f = img.astype(np.float32)

    # Sterke schaduw waar draad onder ligt
    shadow = img_f * (1.0 - strength)
    # Krachtige highlight waar draad boven ligt
    highlight = np.clip(img_f * (1.0 + strength * 1.5), 0, 255)

    # Combineer
    result = np.where(twill_mask[..., np.newaxis], highlight, shadow)

    # Subtiele "draad-rand" voor extra diepte (maakt het echt levensecht)
    edge = np.abs(np.diff(result.astype(np.int16), axis=0, prepend=0))
    edge += np.abs(np.diff(result.astype(np.int16), axis=1, prepend=0))
    edge = np.clip(edge.sum(axis=2, keepdims=True), 0, 50)
    result = np.clip(result + edge * 0.7, 0, 255)

    return result.astype(np.uint8)

# === Tartan genereren ===
def create_tartan(pattern, size=900, thread_width=5, texture=True, twill=True, twill_strength=0.50):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * thread_width))) for c in sett_counts]
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

    if twill:
        tartan = add_twill_pattern(tartan, twill_strength)
    if texture:
        noise = np.random.randint(-20, 25, tartan.shape, dtype=np.int16)
        tartan = np.clip(tartan.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    start = (tartan.shape[0] - size) // 2
    return tartan[start:start+size, start:start+size]

# === Sett-visualisatie ===
def draw_sett_visualization(pattern, thread_width=8):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * thread_width))) for c in sett_counts]
    total = sum(widths)
    fig, ax = plt.subplots(figsize=(max(10, total/70), 3.2))
    ax.set_xlim(0, total); ax.set_ylim(0, 130); ax.axis('off')

    pos = 0
    for w, col, cnt in zip(widths, sett_colors, sett_counts):
        rgb = [x/255 for x in COLORS[col]]
        ax.add_patch(patches.Rectangle((pos, 30), w, 70, color=rgb, ec="black", lw=0.8))
        if w > 25:
            ax.text(pos + w/2, 65, str(int(round(cnt))), ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white' if sum(COLORS[col]) < 300 else 'black')
        pos += w

    pivot_x = total / 2
    ax.axvline(pivot_x, color='#333', linestyle='--', linewidth=2)
    ax.text(pivot_x, 115, "PIVOT", ha='center', va='top', fontsize=10, fontweight='bold')

    sett_str = " ".join(f"{col}{int(round(c))}" for col, c in zip(sett_colors, sett_counts))
    ax.text(total/2, 125, sett_str, ha='center', va='top', fontsize=12, fontweight='bold')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#f9f9f9')
    plt.close(fig)
    buf.seek(0)
    return buf, sett_str

# === UI ===
st.set_page_config(page_title="Echte Tartan + Krachtige Twill", layout="centered")
st.title("Echte Tartan Mirror + Krachtige Keperbinding")

col1, col2 = st.columns([3, 1])
with col1:
    tc = st.text_input("Threadcount (spaties of komma's)", value="R18 K12 B6")
with col2:
    thread_width = st.slider("Draad-dikte", 1, 12, 6)
    texture = st.checkbox("Wol-textuur", True)
    show_twill = st.checkbox("2/2 Twill (keper) zichtbaar", True)
    twill_strength = st.slider("Twill sterkte", 0.0, 0.80, 0.52, 0.01) if show_twill else 0.0

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, thread_width=thread_width,
                           texture=texture, twill=show_twill, twill_strength=twill_strength)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download stof (900×900)", buf,
                           file_name=f"tartan_strong_twill_{tc.strip()[:30].replace(' ', '_').replace(',', '_')}.png",
                           mime="image/png")

        st.markdown("---")
        st.subheader("Volledige symmetrische sett")
        sett_buf, full_sett = draw_sett_visualization(pattern)
        st.image(sett_buf, use_column_width=True)
        st.code(full_sett, language=None)

st.success("Probeer: **Royal Stewart** → R28 W4 R8 Y4 R28 K32 (met twill op 0.55 = perfect!)")
