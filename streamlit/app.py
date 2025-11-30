# app.py – Jouw ultieme Tartan Mirror (2025 – jouw exacte eisen)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import re

# === VOLLEDIGE KLEUREN (inclusief C voor Crimson) ===
COLORS = {
    "R": (178, 34, 52), "DR": (120, 0, 0), "G": (0, 115, 46), "DG": (0, 70, 35),
    "B": (0, 41, 108), "DB": (0, 20, 60), "K": (30, 30, 30), "W": (255, 255, 255),
    "Y": (255, 203, 0), "O": (255, 102, 0), "P": (128, 0, 128), "C": (220, 20, 60),
    "LG": (200, 230, 200), "LB": (180, 200, 230), "A": (160, 160, 160), "T": (0, 130, 130),
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
            if part.startswith(c): color = c; num_str = part[len(c):]; break
            if part.endswith(c): color = c; num_str = part[:-len(c)]; break
        if color is None: st.error(f"Onbekende kleur: '{part}'"); return None
        count = 1.0 if not num_str else (int(num_str.split('/')[1])/2 if '/' in num_str else float(num_str))
        pattern.append((color, count))
    return pattern

def build_sett(pattern):
    f_counts = [c for _, c in pattern]
    f_colors  = [col for col, _ in pattern]
    return f_counts + f_counts[::-1][1:], f_colors + f_colors[::-1][1:]

def create_tartan(pattern, size=900, thread_width=8):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [min(200, max(1, int(round(c * thread_width)))) for c in sett_counts]
    sett_w = sum(widths)
    if sett_w == 0: sett_w = 100
    repeats = max(2, (size // sett_w) + 2)

    tile = np.zeros((sett_w * repeats, sett_w * repeats, 3), dtype=np.uint16)
    x = 0
    for _ in range(repeats):
        for w, col in zip(widths, sett_colors):
            if x + w <= tile.shape[1]:
                tile[:, x:x+w] = COLORS[col]
            x += w

    weft = tile.copy().transpose(1, 0, 2)
    tartan = np.minimum(tile + weft, 255).astype(np.uint8)
    start = (tartan.shape[0] - size) // 2
    return tartan[start:start+size, start:start+size]

def draw_sett_visualization(pattern, thread_width=10):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [min(200, max(1, int(round(c * thread_width)))) for c in sett_counts]
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

# === SESSION STATE VOOR PLAKKEN ===
if "tc" not in st.session_state:
    st.session_state.tc = "G1 K6 B3 R1"

# === UI ===
st.set_page_config(page_title="Tartan Mirror – Jouw Perfecte Versie", layout="centered")
st.title("Tartan Mirror – Jouw Favoriet")

tc = st.text_input(
    "Threadcount (plak met Ctrl+V → genereert direct)",
    value=st.session_state.tc,
    key="tc_input",
    on_change=lambda: st.rerun()  # ← DIT IS DE MAGIE
)

# Halveer knop
col_half, col_normal = st.columns([1, 4])
with col_half:
    if st.button("Halveer alle draden"):
        pattern = parse_threadcount(st.session_state.tc)
        if pattern:
            new_pattern = [(col, count/2) for col, count in pattern]
            new_tc = " ".join(f"{col}{int(round(c)) if c == int(c) else f'{int(round(c*2))}/2'}" for col, c in new_pattern)
            st.session_state.tc = new_tc
            st.rerun()

col1, col2 = st.columns([3, 1])
with col2:
    thread_width = st.slider("Draad-dikte", 1, 30, 8)

if tc.strip():
    st.session_state.tc = tc  # onthoud voor volgende keer
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, thread_width=thread_width)
        st.image(img, use_column_width=True, caption="Klik en sleep om in te zoomen (vergrootglas)")

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download 900×900", buf,
                           file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

        st.markdown("---")
        st.subheader("Volledige symmetrische sett")
        sett_buf, full_sett = draw_sett_visualization(pattern)
        st.image(sett_buf, use_column_width=True)
        st.code(full_sett, language=None)
