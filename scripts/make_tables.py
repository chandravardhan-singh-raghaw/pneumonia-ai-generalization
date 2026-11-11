"""Generate catalogue tables (main-text study tables and supplementary Table S1) from catalog/catalog.csv."""
import csv, sys
sys.path.insert(0, "catalog")
from key_ideas import KEY

SHORT = {  # concise dataset labels for tables (full strings stay in the CSV)
 "liu2020differentiating": "Single-centre CT (Ruian, China)",
 "ortiz2022automatic": "Kermany; Cohen; ChestX-ray8",
 "al2022effectiveness": "COVID-CT",
 "rajpurkar2017chexnet": "ChestX-ray14; Stanford test set",
 "varshni2019pneumonia": "ChestX-ray14 subset",
 "ikechukwu2021resnet": "CheXpert$^{\\dagger}$",
 "szepesi2022detection": "Kermany$^{\\dagger}$",
 "yi2023identification": "Kermany$^{\\dagger}$",
 "sharma2023deep": "Kermany; Kaggle COVID-19/pneumonia",
 "nahiduzzaman2021novel": "Kermany",
 "mujahid2022pneumonia": "Kermany (Kaggle)",
 "mabrouk2022pneumonia": "Kermany",
 "buriboev2024concatenated": "Kermany + enhanced copies",
 "malik2023cdc_net": "12 pooled public sources",
 "yang2022deep": "Kermany (background removed)",
 "ibrahim2024pneumonia": "Cohen; COVID-19 Radiography DB; Kermany",
 "singh2024efficient": "Kermany",
 "ukwuoma2022automated": "COVID-19 Radiography DB; ChestX-ray-15k",
 "ukwuoma2023hybrid": "ChestX-ray8; Kermany$^{\\dagger}$",
 "raghaw2024explainable": "Kermany; VinDr-PCXR; NIH-Pediatric",
 "saber2025efficient": "Kermany; Cohen; CXR lung masks",
 "angara2024novel": "Kermany",
 "yue2024medmamba": "PneumoniaMNIST; CPN X-ray (+14 non-CXR)",
 "khalili2025localization": "VinDr-CXR; ChestX-ray8; CXR-AL14",
 "polsinelli2020light": "COVID-CT; SIRM",
 "ismael2021deep": "380 CXR (Cohen, Kaggle)",
 "monshi2021covidxraynet": "COVIDx; COVIDcxr",
 "gupta2022covid": "COVIDx",
 "shome2021covid": "Three merged public sets (30k)",
 "krishnan2021vision": "COVID-19 Radiography DB",
 "mondal2021xvitcos": "COVIDx CXR-2; COVIDx CT-2A; CheXpert",
 "fan2022covid": "COVIDx-CT",
 "park2022multi": "CheXpert; BIMCV; Brixia; Korean hospitals",
 "qayyum2022collaborative": "Cohen (CXR); POCUS (US)",
 "wang2017chestx": "ChestX-ray8",
 "yan2018weakly": "ChestX-ray14",
 "tam2020weakly": "MIMIC-CXR; ChestX-ray14",
 "keshavamurthy2021weakly": "RSNA Pneumonia",
 "ouyang2023weakly": "Private LUS video, 8 US sites",
 "han2021pneumonia": "RSNA Pneumonia",
 "wei2022deep": "Yanxishe pneumonia CXR",
 "shakouri2023dino": "ChestX-ray14; Kermany; COVIDGR",
 "anwar2024ss": "COVIDx CXR-3 sources; in-house",
 "zang2024pneumonia": "MosMedData",
 "feng2023contrastive": "RSNA$\\to$Kermany; RSNA$\\to$TTSH",
 "yadav2021lung": "Six public CXR/CT sets",
 "akila2023investigating": "Kermany",
 "rana2024auto": "Unnamed CXR set",
 "motamed2021data": "Kermany; COVIDx",
 "khalifa2022detection": "Kermany (624-image subset)",
 "vashisht2023pneumonia": "Unnamed online CXR",
 "jin2023generating": "Unnamed CXR set",
 "alsulami2024mv": "CheXpert (frontal + lateral)",
 "shi2022super": "PCP HRCT",
 "sheu2022multi": "Private (Taichung VGH)",
 "tian2025medical": "P2Med-MD (private)",
 "goswami2025medivlm": "IU X-ray; MIMIC-CXR; CASIA-CXR",
 "yu2025boundary": "Pediatric-P; MosMedData$^{\\dagger}$",
 "wang2020noise": "UESTC-COVID-19 CT",
 "zhang2024cd": "COVID-CT-MD; COVID-19-CT-Seg$^{\\dagger}$",
 "dong2025glmr": "3DLSC-COVID$^{\\dagger}$",
 "amyar2020multi": "COVID-CT; MedSeg; private (Rouen)",
 "ranjbarzadeh2021lung": "COVID-CT (re-annotated)",
}
FAM_ORDER = ["Handcrafted/radiomics", "Custom CNN", "Transfer learning (CNN)", "Transformer", "Hybrid/ensemble",
             "State-space model", "Generative", "Multimodal fusion", "Vision-language/LLM", "Other (spiking)"]
FAM_COLOR = {"Handcrafted/radiomics": "famH", "Custom CNN": "famA", "Transfer learning (CNN)": "famB",
             "Transformer": "famC", "Hybrid/ensemble": "famD", "State-space model": "famE", "Generative": "famF",
             "Multimodal fusion": "famG", "Vision-language/LLM": "famG", "Other (spiking)": "famH"}

SHORTFAM = {"Handcrafted/radiomics": "Handcrafted", "Transfer learning (CNN)": "Transfer learning", "Other (spiking)": "Spiking NN", "State-space model": "SSM"}
def esc(s): return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")
def ds(r): return SHORT.get(r["key"], "NR" if r["datasets"].lower().startswith(("unclear", "not named")) else esc(r["datasets"][:45]))
def pub(r):
    p = r["data_public"]
    if r["key"] in ("ikechukwu2021resnet", "szepesi2022detection", "yi2023identification", "ukwuoma2023hybrid",
                    "yu2025boundary", "zhang2024cd", "dong2025glmr"): return "Public"
    return p if p in ("Public", "Private", "Mixed") else "NR"
def code(r):
    c = r["code"]
    if c.startswith("http"):
        u = c.split()[0].rstrip(".,;")
        return "\\ding{51}\\,{\\scriptsize\\url{%s}}" % u.replace("https://github.com/", "github.com/")
    if c.startswith("Not released"): return "\\ding{55}"
    return "NR"

rows = list(csv.DictReader(open("catalog/catalog.csv", encoding="utf-8")))
rows.sort(key=lambda r: (FAM_ORDER.index(r["family"]), int(r["year"]), r["first_author"]))

def name(r):
    a = r["first_author"].split(",")[0].strip()
    return f"{a} et al.~\\cite{{{r['key']}}}"

# ---------- Supplementary Table S1 (longtable) ----------
out = ["\\begin{footnotesize}\\setlength{\\tabcolsep}{3pt}",
"\\begin{longtable}{@{}P{2.9cm} c P{1.3cm} P{2.0cm} P{2.0cm} P{4.1cm} c P{3.3cm}@{}}",
"\\caption{Complete catalogue of the %d pneumonia imaging studies discussed in the main text, grouped by model family. Data: availability of the training and test data (Public, Private, Mixed). Code: official code release (\\ding{51} = official repository, with its GitHub path; \\ding{55} = paper and repository search found none; NR = could not be determined). $^{\\dagger}$Dataset taken from the original manuscript; not independently re-verified.}\\label{tab:s_catalogue}\\\\" % len(rows),
"\\toprule \\textbf{Study} & \\textbf{Year} & \\textbf{Modality} & \\textbf{Task} & \\textbf{Family} & \\textbf{Training/test data} & \\textbf{Data} & \\textbf{Code} \\\\ \\midrule \\endfirsthead",
"\\toprule \\textbf{Study} & \\textbf{Year} & \\textbf{Modality} & \\textbf{Task} & \\textbf{Family} & \\textbf{Training/test data} & \\textbf{Data} & \\textbf{Code} \\\\ \\midrule \\endhead",
"\\bottomrule \\endfoot"]
prev = None
for r in rows:
    if prev is not None and r["family"] != prev: out.append("\\cdashline{1-8}[0.5pt/2pt]\\noalign{\\vskip 0.5ex}")
    prev = r["family"]
    out.append(f"{name(r)} & {r['year']} & {esc(r['modality'])} & {esc(r['task'])} & {esc(SHORTFAM.get(r['family'], r['family']))} & {ds(r)} & {pub(r)} & {code(r)} \\\\")
out += ["\\end{longtable}", "\\end{footnotesize}"]
open("tab_catalogue.tex", "w").write("\n".join(out))

# ---------- main-text tables ----------
def table(sel, caption, label, fname):
    L = ["\\begin{table*}[!t]", "\\centering", "\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
         f"\\caption{{{caption}}}", f"\\label{{{label}}}",
         "\\begin{NiceTabular*}{\\linewidth}{@{\\extracolsep{\\fill}}P{3.0cm} c P{1.7cm} P{2.1cm} P{3.6cm} P{5.6cm}@{}}",
         "\\toprule", "\\textbf{Study} & \\textbf{Year} & \\textbf{Modality} & \\textbf{Group} & \\textbf{Data} & \\textbf{Key idea} \\\\", "\\midrule"]
    prev = None
    for r in sel:
        g0 = r["paradigm"] if label.startswith("tab:paradigms") else r["family"]
        if prev is not None and g0 != prev: L.append("\\cdashline{1-6}[0.5pt/2pt]\\noalign{\\vskip 0.5ex}")
        prev = g0
        grp = r["paradigm"] if label == "tab:paradigms" else SHORTFAM.get(r["family"], r["family"])
        L.append(f"{name(r)} & {r['year']} & {esc(r['modality'])} & {esc(grp)} & {ds(r)} & {esc(KEY[r['key']])} \\\\")
    L += ["\\bottomrule", "\\end{NiceTabular*}", "\\end{table*}"]
    open(fname, "w").write("\n".join(L))

PAR_ORDER = ["Weakly supervised", "Self-supervised", "Semi-supervised", "Domain adaptation", "Unsupervised", "Federated"]
par = sorted([r for r in rows if r["paradigm"] in PAR_ORDER], key=lambda r: (PAR_ORDER.index(r["paradigm"]), int(r["year"])))
table(par, "Pneumonia imaging studies using weak, self-, semi- or unsupervised learning, domain adaptation or federated learning. NR: not reported. Full details for every study are given in Table~S1 (supplementary).", "tab:paradigms", "tab_paradigms.tex")
arch = [r for r in rows if r["paradigm"] == "Supervised" and r["family"] in
        ("Custom CNN", "Transfer learning (CNN)", "Transformer", "Hybrid/ensemble", "State-space model", "Other (spiking)", "Handcrafted/radiomics")
        and not r["task"].startswith("Segmentation")]
part1 = [r for r in arch if r["family"] in ("Handcrafted/radiomics", "Custom CNN", "Transfer learning (CNN)")]
part2 = [r for r in arch if r not in part1]
table(part1, "Supervised pneumonia classification and detection studies (part 1 of 2): handcrafted features, custom CNNs and transfer learning. Generative, multimodal and segmentation studies are listed in Sections~\\ref{sec:generative}, \\ref{sec:vlm} and \\ref{sec:applications}; all studies are listed in Table~S1 (supplementary). NR: not reported. $^{\\dagger}$Dataset taken from the authors' earlier manuscript.", "tab:architectures", "tab_architectures.tex")
table(part2, "Supervised pneumonia classification and detection studies (part 2 of 2): Vision Transformers, hybrids and ensembles, state-space models and other paradigms. NR: not reported. $^{\\dagger}$Dataset taken from the authors' earlier manuscript.", "tab:architectures2", "tab_architectures2.tex")
print(len(rows), len(par), len(part1), len(part2))
