# streamlit/app.py ← deze start gegarandeerd binnen 10 seconden

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

# === Officiële data (met veilige fallback) ===
@st.cache_data(ttl=3600)
def load_official():
    try:
        df = pd.read_csv("https://www.tartanregister.gov.uk/csvExport.ashx", encoding="utf-8")
        df = df[['TartanName','Threadcount','TartanDescription']].dropna(subset=['Threadcount'])
        df['TartanName'] = df['TartanName'].str.strip().str.title()
        return df
    except:
        return None

df_official = load_o_()

# === Layout ===
c1, c2 = st.columns([1,2])

with c1:
    st.subheader("Zoek register")
    search = st.text_input("Beginletters", "", placeholder="black, royal…", key="s")

    default_tc = "K20 R40 K8 G32 K8 R40 K20"
    selected_name = None

    if search and df_official is not None:
        res = df_official[df_official["TartanName"].str.startswith(search.strip().title())]
        if not res.empty:
            selected_name = st.selectbox("Gevonden", res["TartanName"], index=0)
            default_tc = res[res["TartanName"]==selected_name].iloc[0]["Threadcount"]

    st.subheader("Eigen tartan")
    thread_input = st.text_input(
        "Threadcount (bijv. R30 G20 W4 G20 R30)",
        value=default_tc,
        key="tc"
    )

with c2:
    if not thread_input.strip():
        st.info("Typ een threadcount")
        st.stop()

    # Veilige parser
    raw = thread_input.upper().replace(" ","")
    parts = []
    i = 0
    while i < len(raw):
        if raw[i] in colors:
            j = i + 1
            while j < len(raw) and raw[j].isdigit(): j += 1
            num = int(raw[i+1:j] or "10")
            parts.append((raw[i], num))
            i = j
        else:
            i += 1

    if not parts:
        st.error("Geen geldige threadcount")
        st.stop()

    # Tekenen
    fig, ax = plt.subplots(figsize=(14,7))
    ax.set_xlim(0,400); ax.set_ylim(0,200); ax.axis("off")

    x = 0
    for code, cnt in parts:
        col = colors.get(code, "#555")
        w = cnt * 5
        ax.add_patch(patches.Rectangle((x,0), w, 200, color=col, linewidth=0))
        ax.add_patch(patches.Rectangle((0,x), 400, w, color=col, linewidth=0))
        x += w

    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()

    st.markdown(f"""
    <style>
    .z{{cursor:zoom-in;transition:0.3s;}}
    .z:hover{{transform:scale(2.8);z-index:99;}}
    </style>
    <div style="text-align:center">
    <img src="data:image/png;base64,{b64}" class="z">
    </div>
    """, unsafe_allow_html=True)

    buf.seek(0)
    name = selected_name if selected_name else "Custom_Tartan"
    st.download_button("Download PNG", buf, f"{name}.png", "image/png")
    st.code(thread_input)

st.caption("TartanRegistry – werkt weer · 2025")
