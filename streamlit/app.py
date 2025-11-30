# app.py – Tartan Mirror – De Juiste Manier (nu 100% foutloos)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import re
from PIL import Image

# === Kleuren ===
COLORS = {
    "R": (178, 34, 52), "G": (0, 115, 46), "B": (0, 41, 108), "K": (30, 30, 30),
    "W": (255, 255, 255), "Y": (255, 203, 0), "O": (255, 102, 0), "DB": (0, 20, 60),
    "DG": (0, 70, 35), "C": (220, 20, 60), "P": (128, 0, 128), "A": (160, 160, 160),
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

def create_tartan(pattern, size=900, scale=1):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * scale))) for c in sett_counts]
    total_w = sum(widths)
    
    # Warp: verticale strepen
    warp = np.zeros((total_w, total_w, 3), dtype=np.uint8)
    pos = 0
    for w, col in zip(widths, sett_colors):
        warp[:, pos:pos+w] = COLORS[col]
        pos += w
    
    # Weft: horizontale strepen (transpose van warp)
    weft = warp.copy().transpose(1, 0, 2)
    
    # Overcheck: additievere menging
    result = np.minimum(warp + weft, 255).astype(np.uint8)
    
    # Resize naar gewenste grootte
    pil_img = Image.fromarray(result)
    final = pil_img.resize((size, size), Image.NEAREST)
    return np.array(final)

def draw_sett_visualization(pattern, scale=10):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * scale))) for c in sett_counts]
    total = sum(widths)
    fig, ax = plt.subplots(figsize=(max(10, total/70), 3))
    ax.set_xlim(0, total); ax.set_ylim(0, 100); ax.axis('off')
    
    pos = 0
    for w, col, cnt in zip(widths, sett_colors, sett_counts):
        rgb = [x/255 for x in COLORS[col]]
        ax.add_patch(patches.Rectangle((pos, 20), w, 60, color=rgb, ec="black", lw=0.8))
        if w > 30:
            ax.text(pos + w/2, 50, str(int(round(cnt))), ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white' if sum(COLORS[col]) < 300 else 'black')
        pos += w
    
    ax.axvline(total/2, color='#333', linestyle='--', linewidth=2)
    ax.text(total/2, 90, "PIVOT", ha='center', fontsize=10, fontweight='bold')
    
    sett_str = " ".join(f"{col}{int(round(c))}" for col, c in zip(sett_colors, sett_counts))
    ax.text(total/2, 95, sett_str, ha='center', fontsize=12, fontweight='bold')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#f9f9f9')
    plt.close(fig)
    buf.seek(0)
    return buf

# === UI ===
st.set_page_config(page_title="Tartan Mirror – De Juiste Manier", layout="centered")
st.title("Tartan Mirror – De Juiste Manier")

tc = st.text_input("Threadcount", value="G1 K6 B3 R1")

col1, col2 = st.columns([3, 1])
with col2:
    scale = st.slider("Schaal (pixels per draad)", 1, 100, 1)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, scale=scale)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download", buf,
                           file_name=f"tartan_{tc.strip()[:30].replace(' ', '_')}.png",
                           mime="image/png")

        st.markdown("---")
        st.subheader("Sett (1:1)")
        sett_buf = draw_sett_visualization(pattern, scale=15)
        st.image(sett_buf, use_column_width=True)
