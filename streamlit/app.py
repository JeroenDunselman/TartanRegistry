# app.py  ← deze versie werkte gisteren 100%

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO

# Kleine, harde fallback dataset (geen externe CSV → geen timeout/QUIC-probleem)
@st.cache_data
def get_tartans():
    data = {
        "TartanName": [
            "Black Watch", "Royal Stewart", "Dress Gordon", "Campbell", "MacKenzie",
            "Douglas", "Buchanan", "Fraser", "MacLeod Of Lewis", "Graham Of Menteith",
            "MacDonald", "Stewart Hunting", "MacGregor", "Cameron Of Erracht", "Anderson"
        ],
        "Threadcount": [
            "K8 R4 K24 B24 K24 G32",           # Black Watch
            "R8 B4 R4 W4 R4 Y4 R32",            # Royal Stewart
            "K8 G28 W4 B28 K4 G28 W4 K28",       # Dress Gordon
            "B4 G32 K4 B32 G32 K32",            # Campbell
            "G8 K32 R4 K32 G32",                # MacKenzie
            "G8 B32 K4 B32 G32",                # Douglas
            "Y4 K32 R4 K32 Y32",                # Buchanan
            "R8 G32 K4 G32 R32",                # Fraser
            "B8 G32 R4 G32 B32",                # MacLeod of Lewis
            "B8 R32 G4 R32 B32",               # Graham of Menteith
            "R8 G32 W4 G32 R32 K32",            # MacDonald
            "G8 K32 R4 K32 G32 B32",            # Stewart Hunting
            "R8 G32 W4 G32 R32 K32",            # MacGregor
            "R8 B32 K4 B32 R32 G32",            # Cameron of Erracht
            "B8 R32 G4 R32 B32 K32"             # Anderson
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

st.set_page_config(page_title="Tartan Finder", layout="centered")
st.title("Tartan Finder")

search = st.text_input("Typ de eerste letters van een tartan", "", placeholder="bijv. mac, stew, black")

if search:
    search = search.strip().title()
    results = df[df["TartanName"].str.startswith(search)]
    
    if not results.empty:
        selected = st.selectbox("Gevonden tartans", results["TartanName"], index=0)
    else:
        st.info("Geen tartan gevonden")
        selected = None
else:
    selected = None

if selected:
    row = df[df["TartanName"] == selected].iloc[0]
    
    st.text_area("Beschrijving", row["Description"], height=100)
    
    thread = row["Threadcount"]
    
    # Simpele tartan visualisatie
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 50)
    ax.axis("off")
    
    colors = {"R":"#C00000","G":"#008000","B":"#000080","K":"#000000",
              "W":"#FFFFFF","Y":"#FFFF00","O":"#FF8000","P":"#800080","A":"#808080"}
    
    x = 0
    for part in thread.split():
        if len(part) < 2: continue
        col = colors.get(part[0].upper(), "#666666")
        width = int(part[1:])
        # Horizontaal + verticaal voor sett
        ax.add_patch(patches.Rectangle((x, 0), width*3, 50, color=col))
        ax.add_patch(patches.Rectangle((0, x), 200, width*3, color=col))
        x += width*3
    
    st.pyplot(fig)
    
    # Download PNG
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    st.download_button("Download als PNG", buf, f"{selected}.png", "image/png")
