# app.py – Tartan Mirror + Jouw Exacte "---+++ → +---++" Keperbinding
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import re

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

# === JOUW EXACTE KEPERBINDING: ---+++ → +---++ (naadloos!) ===
def add_twill_pattern(img, twill_type="2/2 (klassiek)", strength=0.65):
    if strength <= 0 or twill_type == "Platbinding (geen keper)":
        return img.copy()

    h, w = img.shape[:2]
    y, x = np.indices((h, w))

    if twill_type == "Jouw Custom (---+++ → +---++)":
        # Jouw exacte 6×6 patroon – naadloos herhalend
        custom_pattern = np.array([
            [0,0,0,1,1,1],  # ---+++
            [0,0,1,1,1,0],  # --+++-
            [0,1,1,1,0,0],  # -+++--
            [1,1,1,0,0,0],  # +++---
            [1,1,0,0,0,1],  # ++---+
            [1,0,0,0,1,1]   # +---++
        ], dtype=bool)
        mask = np.tile(custom_pattern, (h//6 + 1, w//6 + 1))[:h, :w]

    else:
        # Overige bindingen (zoals eerder)
        if twill_type == "1/1 (zeer steil)":         mask = (x + y) % 2 == 0
        elif twill_type == "2/1 (scherp)":           mask = (x + y) % 3 < 2
        elif twill_type == "2/2 (klassiek)":         mask = (x + y) % 4 < 2
        elif twill_type == "3/1 (breed)":            mask = (x + y) % 4 < 3
        elif twill_type == "Herringbone":           block = 32; bx = x//block; by = y//block; dir = ((bx+by)%2)*2-1
                                                     local = (x%block + y%block) * dir; mask = (local % 8 < 4)
        else:                                        mask = (x + y) % 4 < 2

    img_f = img.astype(np.float32)
    shadow    = img_f * (1.0 - strength)
    highlight = np.clip(img_f * (1.0 + strength * 1.8), 0, 255)
    result = np.where(mask[..., np.newaxis], highlight, shadow)

    # Randversterking voor extra diepte
    diff_y = np.diff(result.astype(np.int16), axis=0, prepend=result[:1])
    diff_x = np.diff(result.astype(np.int16), axis=1, prepend=result[:, :1])
    edges = np.abs(diff_y) + np.abs(diff_x)
    edges = np.clip(edges.sum(axis=2, keepdims=True), 0, 70)
    result = np.clip(result + edges * 0.9, 0, 255)

    return result.astype(np.uint8)

def create_tartan(pattern, size=900, thread_width=7, texture=True, twill_type="2/2 (klassiek)", twill_strength=0.65):
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

    tartan = add_twill_pattern(tartan, twill_type=twill_type, strength=twill_strength)

    if texture:
        noise = np.random.randint(-22, 28, tartan.shape, dtype=np.int16)
        tartan = np.clip(tartan.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    start = (tartan.shape[0] - size) // 2
    return tartan[start:start+size, start:start+size]

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
st.set_page_config(page_title="Tartan + Jouw ---+++ → +---++ Keper", layout="centered")
st.title("Tartan Mirror + Jouw Custom Keperbinding")

col1, col2 = st.columns([3, 1])
with col1:
    tc = st.text_input("Threadcount", value="R28 W4 R8 Y4 R28 K32")
with col2:
    thread_width = st.slider("Draad-dikte", 1, 15, 7)
    texture = st.checkbox("Wol-textuur", True)

    twill_options = [
        "Platbinding (geen keper)",
        "1/1 (zeer steil)",
        "2/1 (scherp)",
        "2/2 (klassiek)",
        "3/1 (breed)",
        "Jouw Custom (---+++ → +---++)",   # JOUW BINDING!
        "Herringbone (visgraat)"
    ]
    twill_type = st.select_slider("Keperbinding", options=twill_options, value="Jouw Custom (---+++ → +---++)")
    twill_strength = st.slider("Twill sterkte", 0.0, 0.90, 0.68, 0.01)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, thread_width=thread_width,
                           texture=texture, twill_type=twill_type, twill_strength=twill_strength)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download stof", buf,
                           file_name=f"tartan_your_custom_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

        st.markdown("---")
        st.subheader("Volledige symmetrische sett")
        sett_buf, full_sett = draw_sett_visualization(pattern)
        st.image(sett_buf, use_column_width=True)
        st.code(full_sett, language=None)

st.success("Jouw binding ---+++ → +---++ is nu live. Niemand anders ter wereld heeft dit.")
