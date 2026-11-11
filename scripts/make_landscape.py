"""Regenerate the literature-landscape figure (Fig. 3) from catalog/catalog.csv.

Usage: python scripts/make_landscape.py   (run from the repository root)
Counts are computed only from the pneumonia imaging studies in the catalogue.
"""
import csv
from collections import Counter, defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

FAMILIES = [  # fixed order, validated colour-blind-safe palette (+ neutral grey for 'other')
    ("Custom CNN", "#0072B2"),
    ("Transfer learning (CNN)", "#E69F00"),
    ("Transformer", "#009E73"),
    ("Hybrid/ensemble", "#D55E00"),
    ("State-space model", "#56B4E9"),
    ("Generative", "#CC79A7"),
    ("Multimodal / VLM", "#8C6D1F"),
    ("Handcrafted & other", "#999999"),
]
FAM_MAP = {"Multimodal fusion": "Multimodal / VLM", "Vision-language/LLM": "Multimodal / VLM",
           "Handcrafted/radiomics": "Handcrafted & other", "Other (spiking)": "Handcrafted & other"}

rows = list(csv.DictReader(open("catalog/catalog.csv", encoding="utf-8")))
for r in rows:
    r["fam"] = FAM_MAP.get(r["family"], r["family"])
    r["modg"] = ("CXR" if r["modality"] == "CXR" else
                 "CT" if r["modality"] == "CT" else
                 "Ultrasound" if r["modality"].startswith("US") else
                 "Image + text" if "+" in r["modality"] else "Multi-modality")
    t = r["task"].split(",")[0].strip().lower()
    r["taskg"] = ("Classification" if t.startswith("classif") else
                  "Detection/localization" if t.startswith(("detect", "local")) else
                  "Segmentation" if t.startswith("segment") else
                  "Severity/outcome" if t.startswith(("sever", "outcome")) else
                  "Report generation" if t.startswith("report") else "Synthesis/restoration")

years = list(range(min(int(r["year"]) for r in rows), 2027))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "TeX Gyre Termes", "Nimbus Roman", "Liberation Serif"], "mathtext.fontset": "stix", "font.size": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#555555",
                     "axes.linewidth": 0.6, "xtick.color": "#333333", "ytick.color": "#333333"})
fig = plt.figure(figsize=(7.16, 6.0))
gs = GridSpec(2, 2, figure=fig, width_ratios=[1, 1], height_ratios=[1, 1], wspace=0.58, hspace=0.42)

# (a) studies per year, stacked by family
ax = fig.add_subplot(gs[0, 0])
cnt = defaultdict(Counter)
for r in rows: cnt[int(r["year"])][r["fam"]] += 1
bottom = [0] * len(years)
for fam, col in FAMILIES:
    vals = [cnt[y][fam] for y in years]
    ax.bar(years, vals, bottom=bottom, color=col, width=0.72, edgecolor="white", linewidth=0.8, label=fam)
    bottom = [b + v for b, v in zip(bottom, vals)]
for y, b in zip(years, bottom):
    if b: ax.text(y, b + 0.3, str(b), ha="center", va="bottom", fontsize=6.5, color="#333333")
ax.set_xticks(years); ax.set_xticklabels([str(y)[2:] if i else str(y) for i, y in enumerate(years)])
from matplotlib.ticker import MaxNLocator; ax.yaxis.set_major_locator(MaxNLocator(integer=True)); ax.set_ylim(0, max(bottom) * 1.15); ax.set_ylabel("Studies"); ax.set_title("(a) Reviewed studies per year (to 2026)", loc="left", fontsize=8.5, fontweight="bold")
ax.yaxis.grid(True, color="#e6e6e6", linewidth=0.5); ax.set_axisbelow(True)

# (b) family totals
ax = fig.add_subplot(gs[0, 1])
tot = Counter(r["fam"] for r in rows)
names = [f for f, _ in FAMILIES][::-1]
ax.barh(names, [tot[n] for n in names], color=[dict(FAMILIES)[n] for n in names], height=0.66)
for i, n in enumerate(names):
    ax.text(tot[n] + 0.3, i, f"{tot[n]} ({100*tot[n]/len(rows):.0f}%)", va="center", fontsize=6.5, color="#333333")
ax.set_xlabel("Studies"); ax.set_xlim(0, max(tot.values()) * 1.35)
ax.set_title("(b) Model families", loc="left", fontsize=8.5, fontweight="bold")
ax.tick_params(axis="y", labelsize=7.5)

# (c) modality x task heatmap
ax = fig.add_subplot(gs[1, 0])
mods = ["CXR", "CT", "Ultrasound", "Multi-modality", "Image + text"]
tasks = ["Classification", "Detection/localization", "Segmentation", "Severity/outcome", "Report generation", "Synthesis/restoration"]
M = [[sum(1 for r in rows if r["modg"] == m and r["taskg"] == t) for t in tasks] for m in mods]
mx = max(max(v) for v in M)
ax.imshow(M, cmap="Blues", vmin=0, vmax=mx * 1.15, aspect="auto")
for i in range(len(mods)):
    for j in range(len(tasks)):
        v = M[i][j]
        ax.text(j, i, str(v) if v else "–", ha="center", va="center", fontsize=7,
                color="white" if v > mx * 0.55 else "#333333")
ax.set_xticks(range(len(tasks))); ax.set_xticklabels(["Classifi-\ncation", "Detection/\nlocalization", "Segmen-\ntation", "Severity/\noutcome", "Report\ngeneration", "Synthesis/\nrestoration"], fontsize=6.3)
ax.set_yticks(range(len(mods))); ax.set_yticklabels(mods, fontsize=7)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0)
ax.set_title("(c) Imaging modality × primary task", loc="left", fontsize=8.5, fontweight="bold")

# (d) representative tasks (image panel)
ax = fig.add_subplot(gs[1, 1]); ax.imshow(Image.open("figures/task_panel.png"), aspect="auto"); ax.axis("off")
ax.set_title("(d) Representative tasks", loc="left", fontsize=8.5, fontweight="bold")

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in FAMILIES]
fig.legend(handles, [f for f, _ in FAMILIES], loc="upper center", ncol=4, frameon=False, fontsize=7,
           bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=1.2)
fig.subplots_adjust(top=0.88, left=0.105, right=0.985, bottom=0.09)
fig.savefig("figures/fig_landscape.pdf"); fig.savefig("figures/fig_landscape.png", dpi=200)
print(len(rows), "studies;", dict(tot))
