# streamlit/app.py  ← plak dit exact over je huidige versie heen

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

st.set_page_config(page_title="TartanRegistry", layout="centered")
st.title("TartanRegistry")

# === Kleuren ===
colors = {
    "R": "#C21807", "G": "#007A3D", "B": "#00205B", "K": "#000000",
    "W": "#FFFFFF", "Y": "#FFD700", "O": "#FF6600", "P": "#7D287D",
    "A": "#964B00", "L": "#87CEEB", "N": "#808080"
}

# === Officiële database ===
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
            default_thread = results[results["TartanName"] == selected_name].iloc[0]["Threadcount"]
            default_desc = results[results["TartanName"] == selected_name].iloc[0]["TartanDescription"]
        else:
            selected_name = None
            default_thread = ""
            default_desc = ""
    else:
        selected_name = None
        default_thread = ""
        default_desc = ""

    st.subheader("Of maak je eigen tartan")
    threadcount_input = st.text_input(
        "Threadcount (bijv. R20 K40 G20 Y4 R20)",
        value=default_thread or "K20 R40 K8 G32 K8 R40 K20",
        key="custom_thread",
        help="Letters + aantal draden, bijv. R30 G20 W4 G20 R30"
    )

with col2:
    if threadcount_input.strip():
        # Parse
        parts = threadcount_input.upper().replace(" ", "").split()
        parts = [p for p in parts if len(p) >= 2 and p[0] in colors]

        if not parts:
            st.error("Geen geldige threadcount")
        else:
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_xlim(0, 400)
            ax.set_ylim(0, 200)
            ax.axis("off")

            x = 0
            for part in parts:
                col = colors.get(part[0], "#555555")
                try
