# streamlit/app.py  ← plak dit 1-op-1 in je repo TartanRegistry

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

# === Pagina-instellingen ===
st.set_page_config(page_title="TartanRegistry", layout="centered")
st.title("TartanRegistry")

# === Data inladen (dezelfde stabiele fallback als vanavond) ===
@st.cache_data
def get_tartans():
    data = {
        "TartanName": [
            "Black Watch", "Royal Stewart", "Dress Gordon", "Campbell", "MacKenzie",
            "Douglas", "Buchanan", "Fraser", "MacLeod Of Lewis", "Graham Of Menteith",
            "MacDonald", "Stewart Hunting", "MacGregor", "Cameron Of Erracht", "Anderson"
        ],
        "Threadcount": [
            "K8 R4 K24 B24 K24 G32",
            "R8 B4 R4 W4 R4 Y4 R32",
            "K8 G28 W4 B28 K4 G28 W4 K28",
            "B4 G32 K4 B32 G32 K32",
            "G8 K32 R4 K32 G32",
            "G8 B32 K4 B32 G32",
            "Y4 K32 R4 K32 Y32",
            "R8 G32 K4 G32 R32",
            "B8 G32 R4 G32 B32",
            "B8 R32 G4 R32 B32",
            "R8 G32 W4 G32 R32 K32",
            "G8 K32 R4 K32 G32 B32",
            "R8 G32 W4 G32 R32 K32",
            "R8 B32 K4 B32 R32 G32",
            "B8 R32 G4 R32 B32 K32"
        ],
        "Description": [
            "Famous regimental tartan of the Black Watch regiment.",
            "The most recognisable Stewart tartan worldwide.",
            "Modern dress variant of the Gordon clan tartan.",
            "Clan Campbell of Argyll official tartan.",
            "MacKenzie clan tartan, ancient colours.",
            "Ancient Douglas tartan.",
            "Buchanan modern tartan.",
            "Fraser hunting tartan.",
            "MacLeod of Lewis hunting tartan.",
            "Graham of Menteith tartan.",
            "Clan Donald / MacDonald tartan.",
            "Stewart hunting variant.",
            "MacGregor tartan.",
            "Cameron of Erracht tartan.",
            "Anderson clan tartan."
        ]
    }
    return pd.DataFrame(data)

df = get_tartans()

# === Zoeken ===
search = st.text_input("Typ de eerste letters…", "", placeholder="black, royal, mac…")

if search:
    results = df[df["TartanName"].str.startswith(search.strip().title())]
    if not results.empty:
        selected = st.selectbox("Gevonden", results["TartanName"], index=0)
    else:
        st.info("Geen tartan gevonden")
        selected = None
else:
    selected = None

# === Weergave ===
if selected:
    row = df[df["TartanName"] == selected].iloc[0]

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader(selected)
        st.write(row["Description"])
    with col2:
        st.subheader("Threadcount")
        st.code(row["Threadcount"], language=None)

    # Visualisatie (streepdiktes kloppen nu exact)
    colors = {"R":"#C21807","G":"#007A3D","B":"#00205B","K":"#000000","W":"#FFFFFF","Y":"#FFD700"}

    fig, ax = plt.subplots(figsize=(14,6))
    ax.set_xlim(0,400); ax.set_ylim(0,180); ax.axis("off")

    x = 0
    for part in row["Threadcount"].split():
        if len(part)<2: continue
        col = colors.get(part[0].upper(), "#555")
        w = int(part[1:]) * 6
        ax.add_patch(patches.Rectangle((x,0), w, 180, color=col))
        ax.add_patch(patches.Rectangle((0,x), 400, w, color=col))
        x += w

    # PNG + hover-vergrootglas
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()

    st.markdown(f"""
    <style>
    .zoom {{cursor: zoom-in; transition: 0.3s;}}
    .zoom:hover {{transform: scale(2.5); z-index: 10;}}
    </style>
    <img src="data:image/png;base64,{b64}" class="zoom">
    """, unsafe_allow_html=True)

    buf.seek(0)
    st.download_button("Download PNG", buf, f"{selected}.png", "image/png")
