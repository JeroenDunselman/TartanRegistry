import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Tartan Mirror", layout="centered")
st.title("🧵 Tartan Mirror")

# Kleuren
colors = {
    "r": "#c00000", "g": "#006000", "b": "#000080", "k": "#000000",
    "y": "#ffc000", "w": "#ffffff", "p": "#800080", "o": "#ff8000",
    "a": "#808080"
}

# Input
tc = st.text_input("Threadcount (bijv. r8 k12 b6)", "r8 k12 b6").lower()

# Parse naar lijst van kleuren
def parse(tc):
    parts = tc.split()
    seq = []
    for part in parts:
        if len(part) > 1 and part[0] in colors and part[1:].isdigit():
            seq.extend([colors[part[0]]] * int(part[1:]))
    return seq

seq = parse(tc)

# Spiegelen voor echte tartan (warp = weft = seq + gespiegeld)
full = seq + seq[::-1]

# Threadcount-balk (boven)
fig1, ax1 = plt.subplots(figsize=(10, 1))
for i, col in enumerate(seq):
    ax1.add_patch(patches.Rectangle((i, 0), 1, 1, color=col))
ax1.set_xlim(0, len(seq))
ax1.set_ylim(0, 1)
ax1.axis("off")
st.pyplot(fig1)
st.caption("Threadcount (warp/weft voor spiegeling)")

# Tartan (onder) – 20×20 repeats
repeats = 20
fig2, ax2 = plt.subplots(figsize=(10, 10))
for y in range(repeats):
    for x in range(repeats):
        for i, col in enumerate(full):
            ax2.add_patch(patches.Rectangle((x*len(full) + i, y*len(full)), 1, len(full), color=full[i]))
ax2.set_xlim(0, repeats * len(full))
ax2.set_ylim(0, repeats * len(full))
ax2.set_aspect("equal")
ax2.axis("off")
st.pyplot(fig2)
st.caption(f"Echte tartan – {repeats}×{repeats} repeats (warp = weft = gespiegeld)")

# Download
if st.button("Download tartan als PNG"):
    fig2.savefig("my_tartan.png", dpi=300, bbox_inches='tight', facecolor="#111111")
    with open("my_tartan.png", "rb") as f:
        st.download_button("Download", f, "my_tartan.png", "image/png")
