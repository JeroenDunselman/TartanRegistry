import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random

st.set_page_config(page_title="Tartan Designer", layout="wide")
st.title("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Tartan Designer")

# Kleurenmap (letter → hex)
color_map = {
    "K": "#000000",  # Black
    "R": "#C00000",  # Red
    "G": "#006000",  # Green
    "B": "#000080",  # Blue
    "Y": "#FFC000",  # Yellow
    "W": "#FFFFFF",  # White
    "P": "#800080",  # Purple
    "O": "#FF8000",  # Orange
    "A": "#808080",  # Grey
    "Gold": "#D4AF37"
}

# ─── Sidebar ───
st.sidebar.header("Threadcount")
manual = st.sidebar.text_area("Handmatig (bijv. R8 G24 B8 K32 Y4)", "R8 G24 B8 K32 Y4", height=100)

if st.sidebar.button("🎲 Random tartan"):
    letters = list("KRGBYWPOA")
    parts = [random.choice(letters) + str(random.randint(2, 36)) for _ in range(random.randint(4, 10))]
    manual = " ".join(parts)
    st.sidebar.code(manual)

if st.sidebar.button("🧮 Fractal tartan (Mandelbrot)"):
    def mandelbrot_line(width=256, max_iter=80):
        x = np.linspace(-2.0, 1.0, width)
        escape = np.zeros(width, dtype=int)
        for i in range(width):
            c = x[i]
            z = 0j
            for n in range(max_iter):
                if abs(z) > 2:
                    escape[i] = n
                    break
                z = z*z + c
        thickness = 1 + (escape // 4).astype(int)
        colors = ["R", "G", "B", "Y", "P", "K", "O", "A"]
        parts = []
        for t, col in zip(thickness, np.random.choice(colors, width)):
            if t > 0:
                parts.append(f"{col}{t}")
        manual = " ".join(parts[:random.randint(6, 12)])
    st.sidebar.code(manual)

threadcount = st.sidebar.text_area("Huidige threadcount", manual, height=100, key="current")

symmetry = st.sidebar.selectbox("Symmetry", ["None", "Horizontal", "Vertical", "Both", "Rotational 180°"])
sett_size = st.sidebar.slider("Sett grootte (cm)", 5, 50, 20)

# ─── Parse threadcount ───
def parse_threadcount(tc):
    parts = tc.upper().split()
    seq = []
    for part in parts:
        if len(part) > 1 and part[0] in color_map and part[1:].isdigit():
            seq.extend([part[0]] * int(part[1:]))
    return seq

seq = parse_threadcount(threadcount)

# ─── Symmetry toepassen ───
if symmetry == "Horizontal":
    seq = seq + seq[::-1]
elif symmetry == "Vertical":
    seq = seq + seq
elif symmetry == "Both":
    half = seq + seq[::-1]
    seq = half + half
elif symmetry == "Rotational 180°":
    seq = seq + seq[::-1]

# ─── Tekening ───
fig, ax = plt.subplots(figsize=(16, 4))
x = 0
for letter in seq:
    col = color_map.get(letter, "#808080")
    ax.add_patch(patches.Rectangle((x, 0), 1, 1, color=col))
    x += 1

ax.set_xlim(0, x)
ax.set_ylim(0, 1)
ax.axis('off')
ax.set_aspect('equal')
st.pyplot(fig)

# ─── Download ───
if st.button("💾 Download als PNG (kilt-ready)"):
    fig.savefig("my_tartan.png", dpi=300, bbox_inches='tight', facecolor="#111111")
    with open("my_tartan.png", "rb") as f:
        st.download_button("Download PNG", f, "my_tartan.png", "image/png")

st.caption(f"Sett: {sett_size} cm | Symmetry: {symmetry} | Threads: {len(seq)}")
