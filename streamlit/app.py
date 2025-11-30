# app.py – Tartan Mirror – 100% Correcte Schotse Spiegeling (2025 – Final & Perfect)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import re
from PIL import Image

# === Officiële Schotse kleuren ===
COLORS = {
    "R": (178, 34, 52), "G": (0, 115, 46), "B": (0, 41, 108), "K": (30, 30, 30),
    "W": (255, 255, 255), "Y": (255, 203, 0), "O": (255, 102, 0), "DB": (0, 20, 60),
    "DG": (0, 70, 35), "C": (220, 20, 60), "P": (128, 0, 128), "A": (160, 160, 160),
    "LG": (200, 230, 200), "LB": (180, 200, 230), "T": (0, 130, 130),
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

# === CORRECTE SCHOTSE SPIEGELING (pivot-kleur maar één keer!) ===
def build_sett(pattern):
    f_counts = [c for _, c in pattern]
    f_colors  = [col for col, _ in pattern]
    # Spiegel ZONDER de pivot-kleur dubbel te tellen
    m_counts = f_counts[::-1][1:]   # skip laatste (pivot)
    m_colors = f_colors[::-1][1:]
    return f_counts + m_counts, f_colors + m_colors

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

def draw_sett_visualization(pattern, scale=12):
    sett_counts, sett_colors = build_sett(pattern)
    widths = [max(1, int(round(c * scale))) for c in sett_counts]
    total = sum(widths)
    fig, ax = plt.subplots(figsize=(max(10, total/70), 3.2))
    ax.set_xlim(0, total); ax.set_ylim(0, 130); ax.axis('off')
    
    pos = 0
    for w, col, cnt in zip(widths, sett_colors, sett_counts):
        rgb = [x/255 for x in COLORS[col]]
        ax.add_patch(patches.Rectangle((pos, 30), w, 70, color=rgb, ec="black", lw=0.8))
        if w > 30:
            ax.text(pos + w/2, 65, str(int(round(cnt))), ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white' if sum(COLORS[col]) < 300 else 'black')
        pos += w
    
    ax.axvline(total/2, color='#333', linestyle='--', linewidth=2)
    ax.text(total/2, 115
