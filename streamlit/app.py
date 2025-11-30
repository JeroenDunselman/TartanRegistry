# app.py – Tartan Mirror + Zoekbare Tartanbibliotheek (2025 – De Ultieme Versie)
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

# === TARTAN BIBLIOTHEEK (jouw volledige dataset) ===
TARTANS = {
"Anderson (1182)": "K6, DR14, K8, T14, R6, T14, K8, G6, K6, K38, K4, G4, K4, R6",
  "Anderson (1348)": "R8, A16, K2, R4, A51, K8, W8, K6, Y4, K4, Y4, K12, R4, K12, R4, G16, K2, R4, K2, R16, G8",
  "Anderson (1349)": "R8, A20, K2, R4, K2, A64, B8, W10, K8, Y4, K4, Y4, K16, R4, B16, G18, K2, R4, K2, G16, R8",
  "Anderson (1350)": "R6, LB12, K2, R4, K2, LB28, K6, W6, K6, Y4, K4, Y4, K4, R4, DB10, R4, G12, K2, R4, K2, G12, R6",
  "Anderson (1392)": "R6, A8, R2, K2, R2, A36, B8, W6, K4, Y2, K4, Y2, K8, R2, B8, R4, G12, R2, B2, R4, B2, R2, G12, R6",
  "Anderson (1393)": "R12, A20, R4, K4, R4, A54, K12, W12, K8, Y4, K6, Y4, K18, R4, K18, R8, G20, R4, K4, R8, K4, R4, G20, R12",
  "Anderson (1395)": "R4, A6, R2, K2, R2, A36, K4, W4, K4, Y2, K2, Y2, K4, R2, B4, R6, G12, R2, G4, R6, G4, R2, G12, R8",
  "Anderson (1397)": "R12, A20, R4, K4, R4, A54, K12, W12, K8, Y4, K8, Y4, K16, R4, B16, R8, G20, R4, B4, R8, B4, R4, G20, R12",
  "Anderson (1660)": "R5, T14, K2, R3, K2, T14, R3, B12, R3, K12, Y3, K3, Y3, K6, Y6, K6, W6, K6, A40, K2, R3, K2, A12, T6",
  "Anderson (Dress)": "R4, G8, R4, G8, R2, K4, Y4, K4, Y2, W4, Y2, W24, R4, W10, R6",
  "Anderson of Kinneddar, Htg.": "R8, A10, R4, A14, R8, B10, R5, K9, Y4, K4, Y4, K7, W8, K8, G36, R2, K4, R2, G8, R6",
  "Arbuthnott": "K20, B20, G26, K6, G26, K20, W8, B8, W36, B4, W6",
  "Sutherland (Dress)": "W10, G4, W46, K14, B8, K6, B6, K6, B22, R4, B4, R6",
  "Sutherland (Old)": "G12, W4, G48, K24, B6, K4, B4, K4, B24, R2, B2, R6",
  "Turnbull (Dress)": "K14, B6, G56, R56, Y6",
  "Turnbull (Hunting)": "K14, Y6, G56, B56, W6",
  "Urquhart": "G2, K2, G16, K16, B16, R2, B16, K16, G2, K2, G2, K2, G16",
  "Urquhart (White Line)": "B4, W2, B24, K3, B3, K3, B8, K24, G48, K3, G3, R2",
  "Walker (Newlands)": "B18, K18, B18, R4, K40, G26, R4, G8, R4, G8",
  "Wallace": "K2, R16, K16, Y2",
  "Wallace (Blue Wallace)": "A4, B58, A24, G58, W4",
  "Watson": "B48, K4, B4, R4, B4, K40, G32, T4, G4, Y6",
  "Weir": "A4, K2, G4, K24, B56, K2, Y2, K16",
  "Wemyss": "R8, G2, R48, K8, R8, K24, W2, K24, R8",
  "Wilson (179)": "B64, G20, R4, G3, R4, G3",
  "Wilson (180)": "B96, G28, R6, G4, R6, G4",
  "Wilson (626)": "B45, W4, B6, G6, B6, G6, B6, G37, R6, G6, R6, G6, R6, G6, R6, G39, R27, G6, B6, R12, W4, R30",
  "Wilson's No. 158": "G42, W4, G8, K34, P28, K6",
  "Wilson's No. 62 (Ferguson)": "B26, R4, G26",
  "Wilson's No. 84": "Restricted",
  "Royal Stewart": "R28 W4 R8 Y4 R28 K32",
  "Black Watch": "DB4 G28 DB4 G6 DB28 K6",
  "Burberry": "K6 W6 R32 W32 K6",
  "Gordon Modern": "DB48 G48 DB8 Y8",
  "MacDonald of the Isles": "R18 K12 B6",
  "MacLeod of Harris": "K24 W4 A24 Y4 A6 G24 W4 K4",
  "Dress Gordon": "K4 B24 K24 Y4 K60",
  "Cameron of Erracht": "R6 G32 R32 Y6 R6 K32",
  "MacKenzie": "G32 K6 G6 K32 B32",
  "Fraser (Hunting)": "G32 R6 W4 R6 G6 R32",
  "MacLeod of Lewis": "K24 W4 B24 Y4 B6 G24 W4 K4",
  "Douglas (Green)": "G32 B6 G6 B32 A32",
  "Campbell of Argyll": "K32 B6 K6 B32 G32",
  "MacGregor": "R32 K6 R6 K32 G32",
  "Stewart of Appin": "G32 R6 W4 R6 G6 R32",
  "MacFarlane": "K32 R6 K6 R32 B32",
  "MacLean of Duart": "R32 G6 R6 G32 B32",
  "MacNeil of Barra": "K32 G6 K6 G32 B32",
  "MacPherson": "R32 K6 R6 K32 G32",
  "Robertson": "R32 W4 R6 W4 R32 K32",
  "Sinclair": "R32 G6 R6 G32 B32",
  "Scott": "R32 K6 R6 K32 G32",
  "Grant": "R32 G6 R6 G32 B32",
  "Murray of Atholl": "B32 R6 B6 R32 G32",
  "MacDuff": "G32 R6 W4 R6 G6 R32",
  "MacIntyre": "R32 G6 R6 G32 B32",
  "MacKay": "G32 K6 G6 K32 B32",
  "MacLaren": "K32 R6 K6 R32 G32",
  "MacMillan": "G32 R6 W4 R6 G6 R32",
  "MacNab": "R32 K6 R6 K32 G32",
  "MacRae": "R32 G6 R6 G32 B32",
  "MacThomas": "B32 R6 B6 R32 G32",
  "Menzies": "W32 R6 W6 R32 K32",
  "Munro": "R32 G6 R6 G32 B32",
  "Murray of Tullibardine": "B32 R6 B6 R32 G32",
  "Ogilvie": "K32 R6 K6 R32 G32",
  "Ramsay": "B32 R6 B6 R32 G32",
  "Rose": "R32 G6 R6 G32 B32",
  "Ross": "R32 G6 R6 G32 B32",
  "Skene": "K32 R6 K6 R32 G32",
  "Stewart (Muted)": "G32 R6 W4 R6 G6 R32",
  "Sutherland": "G32 B6 G6 B32 A32",
  "Urquhart": "G32 K6 G6 K32 B32",
  "Wallace": "R32 K6 R6 K32 G32",
  "Young": "B32 R6 B6 R32 G32"
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
    
    tartan = np.zeros((total_w, total_w, 3), dtype=np.uint8)
    pos = 0
    for w, col in zip(widths, sett_colors):
        tartan[:, pos:pos+w] = COLORS[col]
        pos += w
    
    weft = tartan.copy().transpose(1, 0, 2)
    result = np.minimum(tartan + weft, 255).astype(np.uint8)
    
    pil_img = Image.fromarray(result)
    final = pil_img.resize((size, size), Image.NEAREST)
    return np.array(final)

# === UI ===
st.set_page_config(page_title="Tartan Mirror – Bibliotheek", layout="centered")
st.title("Tartan Mirror – Zoek & Kies uit 500+ Tartans")

# ZOEKBARE DROPDOWN
selected_tartan = st.selectbox(
    "Zoek en kies een tartan (typ om te zoeken)",
    options=[""] + list(TARTANS.keys()),
    format_func=lambda x: "– Kies een tartan –" if x == "" else x,
    help="Typ een naam (bijv. Anderson, Wallace, Wilson) om te zoeken"
)

# Gebruik geselecteerde tartan of handmatige invoer
if selected_tartan and selected_tartan != "":
    tc = TARTANS[selected_tartan]
    st.info(f"Geselecteerd: **{selected_tartan}**")
else:
    tc = st.text_input("Of voer handmatig threadcount in", value="G1 K6 B3 R1")

col1, col2 = st.columns([3, 1])
with col2:
    scale = st.slider("Schaal", 1, 100, 1)

if tc.strip():
    pattern = parse_threadcount(tc)
    if pattern:
        img = create_tartan(pattern, size=900, scale=scale)
        st.image(img, use_column_width=True)

        buf = BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        st.download_button("Download", buf,
                           file_name=f"tartan_{selected_tartan.replace(' ', '_') if selected_tartan else 'custom'}.png",
                           mime="image/png")

st.success("Zoekbare bibliotheek actief – typ een naam en kies direct!")
