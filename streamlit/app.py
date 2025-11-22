import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

st.set_page_config(page_title="TartanRegistry", layout="centered")
st.title("TartanRegistry")

# === Kleurenpalet ===
colors = {
    "R": "#C21807", "G": "#007A3D", "B": "#00205B", "K": "#000000",
    "W": "#FFFFFF", "Y": "#FFD700", "O": "#FF6600", "P": "#7D287D",
    "A": "#964B00", "L": "#87CEEB", "N": "#808080"
}

# === Officiële database (fallback blijft) ===
@st.cache_data(ttl=3600)
def load_official():
    try:
        df = pd.read_csv("https://www.tartanregister.gov.uk/csvExport.ashx")
        df = df[['TartanName', 'Threadcount', 'TartanDescription']].dropna(subset=['Threadcount'])
        df['TartanName'] = df['TartanName'].str.strip().str.title()
        return df
    except:
        return None

df_official = load_official()

# === Layout ===
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Zoek in register")
    search = st.text_input("Begin met typen…", "", placeholder="black, royal, mac…", key="search")

    if search and df_official is not None:
        results = df_official[df_official["TartanName"].str.startswith(search.strip().title())]
        if not results.empty:
            selected_name = st.selectbox("Gevonden tartans", results["TartanName"], index=0, key="select")
            threadcount_input = results[results["TartanName"] == selected_name].iloc[0]["Threadcount"]
            description = results[results["TartanName"] == selected_name].iloc[0]["TartanDescription"]
        else:
            selected_name = None
            threadcount_input = ""
            description = ""
    else:
        selected_name = None
        threadcount_input = ""
        description = ""

    st.subheader("Of maak je eigen tartan")
    threadcount_input = st.text_input(
        "Threadcount (bijv. R20 K40 G20 Y4 R20)",
        value=threadcount_input or "K20 R40 K8 G32 K8 R40 K20",
        key="custom_thread",
        help="Gebruik letters R,G,B,K,W,Y,W,O,P,A,L,N + aantal draden"
    )

    if st.button("Genereer tartan"):
        pass  # Enter werkt al via on_change, maar knop als extra

with col2:
    if threadcount_input.strip():
        # Parse threadcount
        parts = threadcount_input.upper().replace(" ", "").split()
        parts = [p for p in parts if len(p) >= 2 and p[0] in colors]

        if not parts:
            st.error("Geen geldige threadcount gevonden")
        else:
            # Visualisatie
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_xlim(0, 400)
            ax.set_ylim(0, 200)
            ax.axis("off")

            x = 0
            for part in parts:
                col = colors.get(part[0], "#555555")
                try:
                    w = int(part[1:])
                except:
                    w = 10
                w_scaled = w * 5
                # Horizontaal + verticaal
                ax.add_patch(patches.Rectangle((x, 0), w_scaled, 200, color=col, linewidth=0))
                ax.add_patch(patches.Rectangle((0, x), 400, w_scaled, color=col, linewidth=0))
                x += w_scaled

            plt.tight_layout()

            # PNG + hover zoom
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode()

            st.markdown(f"""
            <style>
            .zoom {{cursor: zoom-in; transition: 0.3s ease;}}
            .zoom:hover {{transform: scale(2.8); transform-origin: center; z-index: 99;}}
            </style>
            <
