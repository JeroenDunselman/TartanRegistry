import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import re

st.set_page_config(page_title="Tartan Designer", layout="wide")
st.title("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Tartan Designer – Adjacent Zone Blending")

# Kleuren
color_map = {
    "K": "#000000", "R": "#C00000", "G": "#006000", "B": "#000080",
    "Y": "#FFC000", "W": "#FFFFFF", "P": "#800080", "O": "#FF8000",
    "A": "#808080", "Gold": "#D4AF37"
}

# Sidebar
st.sidebar.header("Threadcount")
threadCs = st.sidebar.text_area("Threadcount", "R8 G24 B8 K32 Y4 R8 G24 B8 K32 Y4", height=120)

symmetry = st.sidebar.selectbox("Symmetry", ["None", "Horizontal", "Vertical", "Both", "Rotational 180°"])
blend_strength = st.sidebar.slider("Blend strength tussen zones", 0.0, 1.0, 0.6, 0.05)
zones = st.sidebar.slider("Aantal zones", 2, 6, 4)

# Parse threadcount → list van (letter, count)
def parse_tc(tc):
    #parts = tc.upper().split()
    # Vervang komma's door spaties en splits daarna
    cleaned = re.sub(r'[,\s]+', ' ', tc.strip())   # ← dit is de magie
    parts = cleaned.upper().split()
    seq = []
    for part in parts:
        if len(part) > 1 and part[0] in color_map and part[1:].isdigit():
            seq.append((part[0], int(part[1:])))
    return seq

seq = parse_tc(threadCs)

# Symmetry toepassen (eerst, zodat blend op symmetrische sett gebeurt)
if symmetry in ["Horizontal", "Rotational 180°"]:
    seq = seq + seq[::-1]
elif symmetry == "Vertical":
    seq = seq + seq
elif symmetry == "Both":
    half = seq + seq[::-1]
    seq = half + half

# Splits in zones
total_threads = sum(count for _, count in seq)
zone_size = total_threads // zones
zones_list = []
start = 0
for i in range(zones):
    end = start + zone_size if i < zones - 1 else total_threads
    zones_list.append(seq[start:end])
    start = end

# Blend adjacent zones
blended_seq = zones_list[0].copy()
for i in range(1, zones):
    zone_a = zones_list[i-1]
    zone_b = zones_list[i]
    blend_steps = max(1, int(len(zone_a) * blend_strength * 0.5))
    for j in range(blend_steps):
        if j < len(zone_a) and j < len(zone_b):
            # Lineair interpoleren tussen kleuren (hex → RGB → lerp → hex)
            col_a = color_map[zone_a[-1-j][0]]
            col_b = color_map[zone_b[j][0]]
            r_a, g_a, b_a = int(col_a[1:3],16), int(col_a[3:5],16), int(col_a[5:7],16)
            r_b, g_b, b_b = int(col_b[1:3],16), int(col_b[3:5],16), int(col_b[5:7],16)
            t = j / blend_steps
            r = int(r_a + (r_b - r_a) * t)
            g = int(g_a + (g_b - g_a) * t)
            b = int(b_a + (b_b - b_a) * t)
            blended_color = f"#{r:02x}{g:02x}{b:02x}"
            blended_seq.append(("custom", 1, blended_color))
    blended_seq.extend(zone_b)

# Tekening
fig, ax = plt.subplots(figsize=(16, 4))
x = 0
for item in blended_seq:
    if len(item) == 2:  # normale thread
        letter, count = item
        col = color_map.get(letter, "#808080")
        for _ in range(count):
            ax.add_patch(patches.Rectangle((x, 0), 1, 1, color=col))
            x += 1
    else:  # blended thread
        _, count, col = item
        for _ in range(count):
            ax.add_patch(patches.Rectangle((x, 0), 1, 1, color=col))
            x += 1

ax.set_xlim(0, x)
ax.set_ylim(0, 1)
ax.axis("off")
st.pyplot(fig)

if st.button("Download als PNG"):
    fig.savefig("blended_tartan.png", dpi=300, bbox_inches="tight", facecolor="#111")
    with open("blended_tartan.png", "rb") as f:
        st.download_button("Download PNG", f, "blended_tartan.png", "image/png")

st.caption(f"Zones: {zones} | Blend strength: {blend_strength:.2f} | Symmetry: {symmetry}")
