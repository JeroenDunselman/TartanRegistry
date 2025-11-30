# app.py – Jouw Definitieve Tartan Mirror (2025 – Final Edition)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import re

# === VOLLEDIGE OFFICIËLE SCHOTSE KLEUREN (inclusief C voor Crimson) ===
COLORS = {
    "R": (178, 34, 52),   # Red
    "DR": (120, 0, 0),    # Dark Red
    "G": (0, 115, 46),    # Green
    "DG": (0, 70, 35),    # Dark Green
    "B": (0, 41, 108),    # Blue
    "DB": (0, 20, 60),    # Dark Blue / Navy
    "K": (30, 30, 30),    # Black
    "W": (255, 255, 255), # White
    "Y": (255, 203, 0),   # Yellow / Gold
    "O": (255, 102, 0),   # Orange
    "P": (128, 0, 128),   # Purple
    "C": (220, 20, 60),   # Crimson ← TOEGEVOEGD (officieel!)
    "LG": (200, 230, 200),# Light Green
    "LB": (180, 200, 230),# Light Blue
    "A": (160, 160, 160), # Azure / Grey
    "T": (0, 130, 130),   # Teal
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
                color = c
                num_str = part[len(c):]
                break
            if part.endswith(c):
                color = c
                num_str = part[:-len(c)]
                break
        if color is None:
            st.error(f"Onbekende kleur: '{part}'")
            return None
        count = 1.0 if not num_str else (int(num_str.split('/')[1]) / 2 if '/' in num_str else float(num_str))
        pattern.append((color, count))
    return pattern

def build_sett(pattern):
    f_counts = [c for _, c in pattern]
    f_colors  = [col for col, _ in pattern]
    m_counts  = f_counts[::-1][1:]
    m_colors  = f_colors[::-1][1:]
    return f_counts + m_counts, f_colors + m_colors

def create_tartan(pattern, size=900, thread_width=4):
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
    start = (tartan.shape[0] - size) // 2
    return tartan[start:start+size, start:start+size]

def draw_sett_visualization(pattern, thread_width=8):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * thread_width))) for c in sett_counts]
    total = sum(widths)
    fig, ax = plt.subplots(figsize=(max(10, total/70), 3.2))
    ax.set_xlim(0, total)
    ax.set_ylim(0, 130)
    ax.axis('off')

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
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#f8f8f8')
    plt.close(fig)
    buf.seek(0)
    return buf, sett_str

# === UI ===
st.set_page_config(page_title="Tartan Mirror – Jouw Final", layout="centered")
st.title("Tartan Mirror – Jouw Definitieve Versie")

c1, c2 = st.columns([3, 1])
with c1:
    tc = st.text_input("Threadcount", value="G1 K6 B3 R1")
with c2:
    tw = st.slider("Draad-dikte", 1, 20, 6)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, thread_width=tw)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button(
            "Download 900×900",
            buf,
            file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
            mime="image/png"
        )

        st.markdown("---")
        st.subheader("Volledige symmetrische sett")
        sett_buf, full_sett = draw_sett_visualization(pattern, thread_width=10)
        st.image(sett_buf, use_column_width=True)
        st.code(full_sett, language=None)

st.caption("C = Crimson | Geen wol-textuur | Jouw favoriete versie")
