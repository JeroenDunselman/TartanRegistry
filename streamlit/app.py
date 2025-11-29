import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Tartan Designer", layout="wide")
st.title("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Design Your Own Tartan")

# Kleurenpalet (letter → hex)
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

st.sidebar.header("Threadcount bouwen")
threadcount = st.sidebar.text_area("Threadcount", "R8 G24 B8 K32 Y4", height=100)

symmetry = st.sidebar.selectbox("Symmetry", ["None", "Horizontal", "Vertical", "Both", "Rotational 180°"])
sett_size = st.sidebar.slider("Sett grootte (cm)", 5, 50, 20)

# Parse threadcount
def parse_threadcount(tc):
    parts = tc.upper().split()
    seq = []
    for part in parts:
        if len(part) > 1 and part[0] in color_map and part[1:].isdigit():
            seq.extend([part[0]] * int(part[1:]))
    return seq

seq = parse_threadcount(threadcount)

# Symmetry toepassen
if symmetry == "Horizontal":
    seq = seq + seq[::-1]
elif symmetry == "Vertical":
    seq = seq + seq
elif symmetry == "Both":
    half = seq + seq[::-1]
    seq = half + half
elif symmetry == "Rotational 180°":
    seq = seq + seq[::-1]

# Tekening
fig, ax = plt.subplots(figsize=(14, 4))
x = 0
for letter in seq:
    col = color_map.get(letter, "#808080")
    ax.add_patch(patches.Rectangle((x, 0), 1, 1, color=col))
    x += 1

ax.set_xlim(0, x)
ax.set_ylim(0, 1)
ax.axis('off')
st.pyplot(fig)

if st.button("Download als PNG"):
    fig.savefig("my_tartan.png", dpi=300, bbox_inches='tight')
    with open("my_tartan.png", "rb") as f:
        st.download_button("Download PNG", f, "my_tartan.png", "image/png")

st.caption(f"Sett: {sett_size} cm | Symmetry: {symmetry} | Threads: {len(seq)}")
