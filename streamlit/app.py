import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

st.set_page_config(page_title="TartanRegistry", layout="centered")
st.title("TartanRegistry")

CSV_URL = "https://www.tartanregister.gov.uk/csvExport.ashx"

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv(CSV_URL, encoding="utf-8")
        df = df[['TartanName', 'Threadcount', 'TartanDescription']].dropna(subset=['TartanName', 'Threadcount'])
        df['TartanName'] = df['TartanName'].str.strip().str.title()
        df = df.rename(columns={'TartanDescription': 'Description'})
        return df
    except:
        st.error("Officiële database tijdelijk niet bereikbaar – fallback actief")
        return pd.DataFrame({
            "TartanName": ["Black Watch", "Royal Stewart"],
            "Threadcount": ["K8 R4 K24 B24 K24 G32", "R8 B4 R4 W4 R4 Y4 R32"],
            "Description": ["Famous regimental tartan", "Most famous Stewart tartan"]
        })

df = load_data()

search = st.text_input("Zoek tartan (begint met…)", "", placeholder="bijv. mac, royal, black")

if search:
    results = df[df["TartanName"].str.startswith(search.strip().title())]
    if not results.empty:
        selected = st.selectbox("Gevonden tartans", results["TartanName"], index=0)
    else:
        st.info("Geen tartan gevonden")
        selected = None
else:
    selected = None

if selected:
    row = df[df["TartanName"] == selected].iloc[0]

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(selected)
        st.write(row["Description"])
    with col2:
        st.subheader("Threadcount")
        st.code(row["Threadcount"], language=None)

    # Visualisatie met juiste streepdiktes
    colors = {"R":"#C21807","G":"#007A3D","B":"#00205B","K":"#000000","W":"#FFFFFF",
              "Y":"#FFD700","O":"#FF6600","P":"#7D287D","A":"#964B00","L":"#87CEEB","N":"#808080"}

    thread = row["Threadcount"].replace(" ", "")
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 350)
    ax.set_ylim(0, 175)
    ax.axis("off")

    x = 0
    for part in thread.split():
        if len(part) < 2: continue
        color = colors.get(part[0].upper(), "#555555")
        try:
            width = int(part[1:])
        except:
            width = 4
        # Horizontaal + verticaal
        ax.add_patch(patches.Rectangle((x, 0), width*5, 175, color=color, linewidth=0))
        ax.add_patch(patches.Rectangle((0, x), 350, width*5, color=color, linewidth=0))
        x += width*5

    plt.tight_layout()

    # PNG voor download + base64 voor hover-zoom
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()

    # Hover vergrootglas
    st.markdown(f"""
    <style>
    .zoomimg {{ cursor: zoom-in; transition: transform 0.3s ease; }}
    .zoomimg:hover {{ transform: scale(2.2); z-index: 999; }}
    </style>
    <img src="data:image/png;base64,{img_b64}" class="zoomimg">
    """, unsafe_allow_html=True)

    # Download knop
    buf.seek(0)
    st.download_button(
        "Download als PNG",
        buf,
        file_name=f"{selected.replace(' ', '_')}.png",
        mime="image/png"
    )
