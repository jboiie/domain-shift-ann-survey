"""Builds Domain_Shift_Presentation.pptx from results/results.json and figures/."""
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
R = json.load(open(ROOT / "results" / "results.json"))
S, P, G = R["summary"], R["per_seed"], R["gap_closed_per_seed"]

NAVY = RGBColor(0x1B, 0x2F, 0x4E)
ACCENT = RGBColor(0xB5, 0x4A, 0x2A)
INK = RGBColor(0x22, 0x26, 0x2E)
MUTED = RGBColor(0x5F, 0x68, 0x75)
LIGHT = RGBColor(0xEE, 0xF1, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
state = {"n": 0}


def text(slide, x, y, w, h, runs, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space=6):
    """runs: str or list of paragraphs; a paragraph is a str or a list of (text, bold) tuples."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space)
        for t, b in ([(para, bold)] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            r.font.size, r.font.bold, r.font.name = Pt(size), b, FONT
            r.font.color.rgb = color
    return tb


def bullets(slide, x, y, w, h, items, size=18):
    tb = text(slide, x, y, w, h, [[("•  ", False)] + ([(i, False)] if isinstance(i, str) else i) for i in items], size=size, space=10)
    return tb


def rect(slide, x, y, w, h, fill, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s


def new_slide(title, subtitle=None):
    s = prs.slides.add_slide(BLANK)
    state["n"] += 1
    text(s, 0.6, 0.35, 12.1, 0.8, title, size=30, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, 0.65, 1.15, 1.0, 0.05, ACCENT)
    if subtitle:
        text(s, 0.6, 1.3, 12.1, 0.5, subtitle, size=16, color=MUTED)
    rect(s, 0, 7.05, 13.333, 0.02, LIGHT)
    text(s, 0.6, 7.07, 9, 0.35, "21CSE326T Artificial Neural Networks  |  SRM Institute of Science and Technology, Kattankulathur", size=11, color=MUTED)
    text(s, 11.9, 7.07, 0.85, 0.35, str(state["n"] + 0), size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


def picture(slide, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return slide.shapes.add_picture(str(ROOT / path), Inches(x), Inches(y), **kw)


def table(slide, x, y, w, rows, col_w, size=14, row_h=0.45, first_bold=True, hl_rows=()):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    t = gt.table
    tblPr = gt._element.graphic.graphicData.tbl.tblPr
    tblPr.set("bandRow", "0")
    tblPr.set("firstRow", "0")
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.1)
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else (LIGHT if i in hl_rows else WHITE)
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 or nc <= 2 or i == 0 and j == 0 else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = val
            r.font.size, r.font.name = Pt(size), FONT
            r.font.bold = i == 0 or (j == 0 and first_bold)
            r.font.color.rgb = WHITE if i == 0 else INK
    return t


def pm(a, b, nd=2):
    return f"{a:.{nd}f} ± {b:.{nd}f}"


# 1. Title
s = prs.slides.add_slide(BLANK)
state["n"] += 1
rect(s, 0, 0, 13.333, 7.5, NAVY)
rect(s, 0.8, 0.7, 3.6, 1.25, WHITE)
picture(s, "report/assets/srm_logo.jpeg", 0.95, 0.85, w=3.3)
text(s, 0.8, 2.35, 11.7, 1.9, "Domain Shift in Artificial Neural Networks: A Survey of Domain Adaptation Techniques", size=38, color=WHITE, bold=True)
rect(s, 0.85, 4.3, 1.2, 0.06, ACCENT)
text(s, 0.8, 4.5, 11.7, 0.5, "Case study for 21CSE326T Artificial Neural Networks", size=20, color=WHITE)
text(s, 0.8, 5.05, 6.2, 1.6, [[("Jai", False)], [("Aggam Singh Arora", False)], [("Areeb Akhtar", False)], [("Ujwal M", False)]], size=17, color=WHITE, space=2)
text(s, 7.2, 5.05, 5.4, 1.6, [[("Guide: ", True), ("Dr. Kothai G", False)], "Department of Computational Intelligence", "SRM Institute of Science and Technology, Kattankulathur", "November 2026"], size=16, color=WHITE, space=3)

# 2. Motivation
s = new_slide("Motivation: a model that works in one hospital fails in another")
bullets(s, 0.6, 1.6, 7.2, 4.5, [
    "Zech et al. (2018) trained CNNs to detect pneumonia in chest radiographs.",
    "Tested at outside hospitals, the models did worse than at their training hospital in 3 of 5 comparisons.",
    "The same models could identify the hospital system from the image alone.",
    "The model had learned cues unrelated to pneumonia, such as scanner and hospital artifacts.",
], size=20)
for k, (big, small) in enumerate([("3 of 5", "comparisons with lower accuracy at outside hospitals"),
                                  ("99.95%", "hospital-system detection, NIH"),
                                  ("99.98%", "hospital-system detection, Mount Sinai")]):
    y = 1.65 + k * 1.75
    rect(s, 8.5, y, 4.2, 1.5, LIGHT)
    rect(s, 8.5, y, 0.08, 1.5, ACCENT)
    text(s, 8.75, y + 0.1, 3.9, 0.75, big, size=36, color=NAVY, bold=True)
    text(s, 8.75, y + 0.82, 3.9, 0.65, small, size=14, color=MUTED)
text(s, 0.6, 6.45, 12, 0.4, "Zech et al., PLOS Medicine 15(11): e1002683, 2018.", size=12, color=MUTED)

# 3. Domain shift
s = new_slide("What is domain shift")
text(s, 0.6, 1.6, 12.1, 1.0, "A model is trained on data from a source distribution and used on data from a different target distribution, for the same task. Held-out accuracy on the source then says little about accuracy in deployment.", size=19)
table(s, 0.6, 3.05, 12.1, [
    ["Type", "What changes", "Example"],
    ["Covariate shift", "Input distribution P(x); P(y | x) is unchanged", "Different scanner, camera, lighting or background"],
    ["Label shift", "Class proportions P(y); P(x | y) is unchanged", "A disease is more common at one hospital"],
    ["Concept shift", "The relation P(y | x) itself", "Label meaning drifts over time or between annotators"],
], [2.6, 5.0, 4.5], size=16, row_h=0.7)
text(s, 0.6, 6.1, 12.1, 0.6, "This work focuses on covariate shift in image classification, where the target domain has no labels (unsupervised domain adaptation).", size=16, color=MUTED)

# 4. Why accuracy drops
s = new_slide("Why accuracy drops: the Ben-David bound")
rect(s, 0.6, 1.7, 12.1, 1.3, LIGHT)
text(s, 0.6, 1.7, 12.1, 1.3, "ε_T(h)  ≤  ε_S(h)  +  ½ d_HΔH(S, T)  +  λ", size=34, color=NAVY, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for k, (h, b) in enumerate([("ε_T(h)", "Target error: what we care about and cannot measure without target labels."),
                            ("ε_S(h)", "Source error: low, because we train on it."),
                            ("d_HΔH(S, T)", "Divergence between the two domains as seen by the hypothesis class. Domain adaptation tries to shrink this term."),
                            ("λ", "Error of the best single hypothesis on both domains. If it is large, no method can adapt.")]):
    y = 3.35 + k * 0.85
    text(s, 0.7, y, 2.6, 0.7, h, size=20, color=ACCENT, bold=True)
    text(s, 3.4, y, 9.3, 0.8, b, size=18)
text(s, 0.6, 6.6, 12, 0.4, "Ben-David et al., Machine Learning 79(1-2): 151-175, 2010.", size=12, color=MUTED)

# 5. Taxonomy
s = new_slide("Taxonomy of approaches")
picture(s, "figures/taxonomy.png", 1.7, 1.5, h=5.35)

# 6. Methods compared
s = new_slide("Methods surveyed")
table(s, 0.6, 1.55, 12.1, [
    ["Method", "Core idea", "Target data at training"],
    ["Fine-tuning", "Continue training on labeled target data", "Labeled"],
    ["DAN (2015)", "Penalize multi-kernel MMD between domains on task-specific layers", "Unlabeled"],
    ["Deep CORAL (2016)", "Align second-order statistics (covariances) of the features", "Unlabeled"],
    ["DANN (2015)", "Domain classifier with a gradient reversal layer; features become domain-invariant", "Unlabeled"],
    ["ADDA (2017)", "Untied target encoder trained against a domain discriminator", "Unlabeled"],
    ["AdaBN (2016)", "Replace batch-norm statistics with statistics of the target data", "Unlabeled, no training"],
    ["CyCADA (2018)", "Pixel-level and feature-level adaptation with cycle consistency", "Unlabeled"],
    ["TENT (2021)", "Minimize prediction entropy on test batches, updating BN parameters", "Unlabeled, at test time"],
], [2.6, 6.7, 2.8], size=14, row_h=0.56)

# 7. Experiment design
s = new_slide("Experiment: MNIST to MNIST-M")
text(s, 0.6, 1.6, 12.1, 0.6, "Question: how much of the accuracy lost to domain shift can a cheap method (AdaBN) and an adversarial method (DANN) recover, with no target labels?", size=19)
table(s, 0.6, 2.7, 12.1, [
    ["Method", "Role", "Uses target images", "Uses target labels"],
    ["Source-only", "Lower reference: ignore the shift", "No", "No"],
    ["AdaBN", "Re-estimate BN statistics on target images", "Yes", "No"],
    ["DANN", "Adversarial feature alignment", "Yes", "No"],
    ["Target-only", "Upper bound", "Yes", "Yes"],
], [2.6, 5.3, 2.2, 2.0], size=16, row_h=0.65)
text(s, 0.6, 6.15, 12.1, 0.6, [[("Metric: ", True), ("gap closed = (method - source-only) / (target-only - source-only), on MNIST-M test accuracy, computed per seed.", False)]], size=16)

# 8. Datasets
s = new_slide("Datasets")
picture(s, "figures/samples.png", 0.6, 1.55, w=12.1)
table(s, 0.6, 4.65, 12.1, [
    ["", "MNIST (source)", "MNIST-M (target)"],
    ["Content", "Handwritten digits, grayscale, resized to 32x32 and copied to 3 channels", "MNIST digits blended with random photo patches, 32x32 RGB"],
    ["Source", "torchvision download", "Hugging Face dataset Mike0307/MNIST-M"],
    ["Training / test", "10,000 random training images / 10,000 test", "10,000 random training images / 9,001 test"],
], [2.0, 5.2, 4.9], size=14, row_h=0.55)

# 9. Architecture
s = new_slide("Shared backbone and DANN components")
picture(s, "figures/architecture.png", 0.9, 1.55, h=4.55)
text(s, 0.6, 6.25, 12.1, 0.7, "Three Conv-BatchNorm-ReLU-MaxPool blocks (32, 64, 128 channels), a 128-d feature layer and a 10-way classifier. Every method uses this backbone; DANN adds the gradient reversal layer and a domain classifier.", size=15, color=MUTED)

# 10. AdaBN and DANN
s = new_slide("AdaBN and DANN")
for x, head, items in [
    (0.6, "AdaBN", [
        "Take the source-only model and keep all weights fixed.",
        "Recompute each BatchNorm layer's mean and variance on unlabeled target images.",
        "Two sets of statistics: source for MNIST, target for MNIST-M, so MNIST accuracy is unchanged.",
        "No training: about 1 second.",
    ]),
    (6.9, "DANN", [
        "A domain classifier on the 128-d features separates source from target.",
        "The gradient reversal layer is the identity going forward and multiplies the gradient by -λ going backward, so the feature extractor learns to confuse the domain classifier.",
        "Label loss on source only; λ = 2 / (1 + exp(-10p)) - 1 rises from 0 to 1.",
        "A concatenated source and target batch goes through the backbone, so BN statistics are mixed.",
    ])]:
    rect(s, x, 1.55, 5.8, 0.55, NAVY)
    text(s, x + 0.15, 1.55, 5.5, 0.55, head, size=20, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    bullets(s, x, 2.3, 5.8, 4.6, items, size=18)

# 11. Training setup
s = new_slide("Training setup")
cfg = R["config"]
table(s, 0.6, 1.6, 12.1, [
    ["Item", "Value"],
    ["Optimizer", "SGD, momentum 0.9"],
    ["Learning rate", "0.01 / (1 + 10p)^0.75, p = training progress from 0 to 1 (Ganin and Lempitsky)"],
    ["Batch size / epochs", f"{cfg['batch_size']} / {cfg['epochs']}, identical for every method"],
    ["Training data", f"{cfg['n_train_per_domain']:,} images per domain"],
    ["Seeds", "0, 1, 2 (all reported, none selected)"],
    ["Hardware", "CPU only; about 7 minutes per seed for all four methods"],
], [3.0, 9.1], size=16, row_h=0.62)
text(s, 0.6, 6.1, 12.1, 0.7, "Before the final run, the preprocessing of both domains was audited (same format, range and normalization) and no problem was found. AdaBN is evaluated with source statistics on MNIST and target statistics on MNIST-M.", size=14, color=MUTED)

# 12. Results table
s = new_slide("Results", "Mean ± std over 3 seeds, test accuracy (%)")
names = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
rows = [["Method", "MNIST", "MNIST-M", "Gap closed"]]
for k, v in S.items():
    g = "-" if k == "source_only" else ("100 (by definition)" if k == "target_only" else pm(v["gap_mean"], v["gap_std"], 1) + " %")
    rows.append([names[k], pm(v["mnist_mean"], v["mnist_std"]), pm(v["mnistm_mean"], v["mnistm_std"]), g])
table(s, 0.6, 1.95, 12.1, rows, [2.8, 2.9, 3.0, 3.4], size=18, row_h=0.72, hl_rows=(2,))
text(s, 0.6, 5.85, 12.1, 0.9, "A model at 98.75% on MNIST scores 19.62% on MNIST-M. AdaBN recovers 37.6% of the gap, DANN 26.7%.", size=18, color=NAVY, bold=True)

# 13. Bar chart + per-seed
s = new_slide("Accuracy by method and per-seed MNIST-M results")
picture(s, "figures/results_bar.png", 0.5, 1.55, w=6.9)
rows = [["MNIST-M (%)", "Seed 0", "Seed 1", "Seed 2"]]
for k in names:
    rows.append([names[k]] + [f"{x:.2f}" for x in P[k]["mnistm"]])
table(s, 7.6, 1.7, 5.2, rows, [1.7, 1.17, 1.17, 1.16], size=14, row_h=0.5)
rows = [["Gap closed (%)", "Seed 0", "Seed 1", "Seed 2"]]
for k in ("adabn", "dann"):
    rows.append([names[k]] + [f"{x:.1f}" for x in G[k]])
table(s, 7.6, 4.5, 5.2, rows, [1.7, 1.17, 1.17, 1.16], size=14, row_h=0.5)
text(s, 7.6, 6.15, 5.2, 0.7, "AdaBN is ahead of DANN in every seed.", size=15, color=NAVY, bold=True)

# 14. t-SNE
s = new_slide("Feature space: source-only vs DANN")
picture(s, "figures/tsne.png", 1.25, 1.5, h=4.75)
text(s, 0.6, 6.3, 12.1, 0.7, "t-SNE of 128-d features, seed 0. DANN's domain loss reached ln 2 (about 0.693), the value for a chance-level domain classifier, yet source and target features still sit in separate regions.", size=15, color=MUTED)

# 15. Findings and limitations
s = new_slide("Findings and limitations")
for x, head, items in [
    (0.6, "Findings", [
        "The shift is large: 98.75% on MNIST falls to 19.62% on MNIST-M.",
        "AdaBN closed more of the gap than DANN in every seed, with no training.",
        "DANN improved on source-only in every seed but varies more across seeds (gap closed 20.7 to 34.4).",
        "A domain loss at chance did not mean the domains were aligned.",
        "Not directly comparable to Ganin and Lempitsky (57.5% source-only, 81.5% DANN): different network, data size and MNIST-M copy.",
    ]),
    (6.9, "Limitations", [
        "Toy benchmark with a synthetic shift; may not transfer to real shifts such as hospitals.",
        "Small CNN, 10,000 images per domain, 30 epochs, 3 seeds.",
        "DANN was not tuned per method. Why it trails AdaBN here was not tested; mixed BN statistics and small data are candidates.",
        "Only AdaBN and DANN were run. The other surveyed methods are described, not implemented.",
    ])]:
    rect(s, x, 1.55, 5.8, 0.55, NAVY)
    text(s, x + 0.15, 1.55, 5.5, 0.55, head, size=20, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    bullets(s, x, 2.3, 5.8, 4.6, items, size=17)

# 16. Conclusion + references
s = new_slide("Conclusion and references")
bullets(s, 0.6, 1.55, 12.1, 2.1, [
    "Domain shift is a deployment risk that held-out accuracy on the training distribution does not reveal.",
    "In this setup, re-estimating batch-norm statistics (AdaBN) was the cheapest and most reliable adaptation method; DANN gave a smaller and less stable gain.",
    "Code, results and report: github.com/jboiie/domain-shift-ann-survey",
], size=17)
text(s, 0.6, 3.85, 12.1, 0.4, "References", size=16, color=ACCENT, bold=True)
text(s, 0.6, 4.25, 12.1, 2.7, [
    "Zech et al. (2018). Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs. PLOS Medicine 15(11): e1002683.",
    "Ben-David et al. (2010). A theory of learning from different domains. Machine Learning 79(1-2): 151-175.",
    "Ganin & Lempitsky (2015). Unsupervised domain adaptation by backpropagation. ICML, PMLR 37: 1180-1189.",
    "Ganin et al. (2016). Domain-adversarial training of neural networks. JMLR 17(59): 1-35.",
    "Li et al. (2016). Revisiting batch normalization for practical domain adaptation. arXiv:1603.04779.",
    "Wang & Deng (2018). Deep visual domain adaptation: A survey. Neurocomputing 312: 135-153.",
], size=13, color=MUTED, space=4)

out = ROOT / "presentation" / "Domain_Shift_Presentation.pptx"
prs.save(out)
print("saved", out, len(prs.slides._sldIdLst), "slides")
