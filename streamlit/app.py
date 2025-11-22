# streamlit/app.py  ← exact over je huidige bestand heen plakken

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

st.set_page_config(page_title="TartanRegistry", layout="centered")
st.title("TartanRegistry")

# Kleurenpalet
colors = {
    "R": "#C21807", "G": "#007A3D", "B": "#00205B", "K": "#000000",
    "W": "#FFFFFF", "Y": "#FFD700", "O": "#FF6600", "P": "#7D287D",
    "A": "#964B00", "L": "#87CEEB", "N": "#808080"
}

# Officiële database met fallback
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

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Zoek in register")
    search = st.text_input("Begin met typen…", "", placeholder="black, royal, mac…", key="search")

    default_thread = "K20 R40 K8 G32 K8 R40 K20"
    selected_name = None

    if search and df_official is not None:
        results = df_official[df_official["TartanName"].str.startswith(search.strip().title())]
        if not results.empty:
            selected_name = st.selectbox("Gevonden tartans", results["TartanName"], index=0, key="select")
            default_thread = results[results["TartanName"] == selected_name].iloc[0]["Threadcount"]

    st.subheader("Of maak je eigen tartan")
    threadcount_input = st.text_input(
        "Threadcount (bijv. R30 G20 W4 G20 R30)",
        value=default_thread,
        key="custom_thread",
        help="Letters + aantal draden, spaties worden genegeerd"
    )

with col2:
    if threadcount_input.strip():
        # Parse threadcount
        raw = threadcount_input.upper().replace(" ", "")
        parts = []
        i = 0
        while i < len(raw):
            if raw[i] in colors:
                j = i + 1
                while j < len(raw) and raw[j].isdigit():
                    j += 1
                num = int(raw[i+1:j] or "10")
                parts.append((raw[i], num))
                i = j
            else:
                i += 1

        if not parts:
            st.error("Geen geldige threadcount gevonden")
        else:
            # Visualisatie
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_xlim(0, 400)
            ax.set_ylim(0, 200)
            ax.axis("off")

            x = 0
            for code, count in parts:
                col = colors.get(code, "#555555")
                w = count * 5
                ax.add_patch(patches.Rectangle((x, 0), w, 200, color=col, linewidth=0))
                ax.add_patch(patches.Rectangle((0,x), 400, w, color=col, linewidth=0))
                x += w

            plt.tight_layout()

            # PNG + hover zoom
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode()

            st.markdown(f"""
            <style>
            .zoom {{cursor: zoom-in; transition: transform 0.3s ease;}}
            .zoom:hover {{transform: scale(2.8); transform-origin: center; z-index: 99;}}
            </style>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{img_b64}" class="zoom">
            </div>
            """, unsafe_allow_html=True)

            buf.seek(0)
            name = selected_name if selected_name else "Custom_Tartan"
            st.download_button("Download als PNG", buf, f"{name}.png", "image/png")

            st.code(threadcount_input.strip(), language=None)
    else:
        st.info("Typ een threadcount om te beginnen")

st.markdown("---")
st.caption("TartanRegistry – officiële Schotse tartans + eigen ontwerpen · 2025")
