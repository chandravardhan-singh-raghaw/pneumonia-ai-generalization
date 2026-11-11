"""Chord diagram of model family (left half) against input modality (right half)
for the reviewed pneumonia imaging studies. Run from the repository root:
    python scripts/make_chord.py   -> figures/fig_chord.pdf / .png
A study with several input modalities is counted once per modality.
"""
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Wedge

plt.rcParams.update({"font.family": "serif",
                     "font.serif": ["Times New Roman", "TeX Gyre Termes", "Nimbus Roman", "Liberation Serif"]})

FAMILIES = [("Custom CNN", "#0072B2"), ("Transfer learning", "#E69F00"), ("Transformer", "#009E73"),
            ("Hybrid/ensemble", "#D55E00"), ("State-space model", "#56B4E9"), ("Generative", "#CC79A7"),
            ("Multimodal / VLM", "#8C6D1F"), ("Handcrafted & other", "#999999")]
FAM_MAP = {"Transfer learning (CNN)": "Transfer learning", "Multimodal fusion": "Multimodal / VLM",
           "Vision-language/LLM": "Multimodal / VLM", "Handcrafted/radiomics": "Handcrafted & other",
           "Other (spiking)": "Handcrafted & other"}
MODS = [("CXR", "#4D4D4D"), ("CT", "#7A7A7A"), ("Ultrasound", "#A3A3A3"), ("Text / clinical", "#C8C8C8")]

def modalities(m):
    out = []
    if "CXR" in m: out.append("CXR")
    if "CT" in m: out.append("CT")
    if "US" in m: out.append("Ultrasound")
    if "text" in m or "clinical" in m: out.append("Text / clinical")
    return out

rows = list(csv.DictReader(open("catalog/catalog.csv", encoding="utf-8")))
fams = [f for f, _ in FAMILIES]; mods = [m for m, _ in MODS]
M = np.zeros((len(fams), len(mods)), int)
for r in rows:
    f = FAM_MAP.get(r["family"], r["family"])
    for m in modalities(r["modality"]):
        M[fams.index(f), mods.index(m)] += 1

total = M.sum()
gap = np.deg2rad(2.2)
n_arcs = len(fams) + len(mods)
avail = 2 * np.pi - gap * (n_arcs + 2)  # extra gaps separate the two halves
scale = avail / (2 * total)
# families on the left half (top -> bottom, counter-clockwise from 90deg), modalities on the right half
arcs = {}
theta = np.pi / 2 + gap
for i, f in enumerate(fams):
    w = M[i].sum() * scale; arcs[("f", i)] = (theta, theta + w); theta += w + gap
theta += gap
for j, m in enumerate(mods):
    w = M[:, j].sum() * scale; arcs[("m", j)] = (theta, theta + w); theta += w + gap

fig, ax = plt.subplots(figsize=(3.5, 3.5))
ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15); ax.set_aspect("equal"); ax.axis("off")
R, W = 1.0, 0.07

def pt(a, r=R): return np.array([r * np.cos(a), r * np.sin(a)])

# ribbons
fpos = {i: arcs[("f", i)][0] for i in range(len(fams))}
mpos = {j: arcs[("m", j)][0] for j in range(len(mods))}
for i in range(len(fams)):
    for j in range(len(mods)):
        v = M[i, j]
        if not v: continue
        a0, a1 = fpos[i], fpos[i] + v * scale; fpos[i] = a1
        b0, b1 = mpos[j], mpos[j] + v * scale; mpos[j] = b1
        verts = [pt(a0), pt(a1)]  # along family arc (approximated by Bezier through arc)
        path = Path([pt(a0), pt((a0 + a1) / 2, R / np.cos((a1 - a0) / 2)), pt(a1),
                     (0, 0), pt(b0),
                     pt((b0 + b1) / 2, R / np.cos((b1 - b0) / 2)), pt(b1),
                     (0, 0), pt(a0), pt(a0)],
                    [Path.MOVETO, Path.CURVE3, Path.CURVE3,
                     Path.CURVE3, Path.CURVE3,
                     Path.CURVE3, Path.CURVE3,
                     Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY])
        ax.add_patch(PathPatch(path, facecolor=FAMILIES[i][1], alpha=0.55, edgecolor="white", linewidth=0.4))

# outer arcs and labels
for (kind, k), (t0, t1) in arcs.items():
    col = FAMILIES[k][1] if kind == "f" else MODS[k][1]
    ax.add_patch(Wedge((0, 0), R + 0.02 + W, np.degrees(t0), np.degrees(t1), width=W,
                       facecolor=col, edgecolor="black", linewidth=0.5))
    mid = (t0 + t1) / 2
    lab = (fams[k] if kind == "f" else mods[k])
    cnt = M[k].sum() if kind == "f" else M[:, k].sum()
    x, y = pt(mid, R + 0.16)
    deg = np.degrees(mid) % 360
    rot = deg - 180 if 90 < deg < 270 else deg
    ha = "right" if 90 < deg < 270 else "left"
    ax.text(x, y, f"{lab} ({cnt})", rotation=rot, rotation_mode="anchor", ha=ha, va="center", fontsize=7.4)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("figures/fig_chord.pdf", bbox_inches="tight", pad_inches=0.02); fig.savefig("figures/fig_chord.png", dpi=250, bbox_inches="tight", pad_inches=0.02)
print(M, M.sum())
