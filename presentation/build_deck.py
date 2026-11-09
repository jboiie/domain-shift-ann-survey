"""Builds the case study review deck on the course template.

Usage: python presentation/build_deck.py "<path to case study review template.pptx>"
Numbers are read from results/results.json; figures come from figures/.
"""
import io
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.opc.packuri import PackURI
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "Desktop/CLG/ANN/case study review template.pptx")
OUT = ROOT / "presentation" / "Domain_Shift_Case_Study_Review.pptx"
R = json.load(open(ROOT / "results" / "results.json"))
S = R["summary"]
FONT = "Times New Roman"

prs = Presentation(TEMPLATE)
LOGO = next(sh for sh in prs.slides[2].shapes if sh.shape_type == 13).image.blob
logo_xy = (8.17, 0.42, 2.44, 0.9)
thanks = prs.slides[len(prs.slides) - 1]
thanks.part.partname = PackURI("/ppt/slides/slide99.xml")  # free slide12 for the new slides

# keep the template title slide and the Thank You slide, drop the sample content slides
ids = prs.slides._sldIdLst
for sld in list(ids)[1:-1]:
    prs.part.drop_rel(sld.rId)
    ids.remove(sld)


def run(p, t, size, bold=False, italic=False):
    r = p.add_run()
    r.text = t
    r.font.size, r.font.bold, r.font.italic, r.font.name = Pt(size), bold, italic, FONT
    r.font.color.rgb = RGBColor(0, 0, 0)
    return r


def textbox(slide, x, y, w, h, paras, size=15, spacing=1.3, justify=True, after=4):
    """paras: list of str or list of (text, bold) segments."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.JUSTIFY if justify else PP_ALIGN.LEFT
        p.line_spacing = spacing
        p.space_after = Pt(after)
        for t, b in ([(para, False)] if isinstance(para, str) else para):
            run(p, t, size, b)
    return tb


def new_slide(title):
    s = prs.slides.add_slide(prs.slide_layouts[1])
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx != 0:
            ph._element.getparent().remove(ph._element)
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.9), Inches(1.25), Inches(9.2), Inches(0.7)
    t.text_frame.text = title
    p = t.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for r in p.runs:
        r.font.size, r.font.name = Pt(26), FONT
    s.shapes.add_picture(io.BytesIO(LOGO), *[Inches(v) for v in logo_xy])
    return s


def bullets(slide, y, items, size=15, h=None, x=0.7, w=9.6, spacing=1.3):
    return textbox(slide, x, y, w, h or 4, ["• " + i if isinstance(i, str) else [("• ", False)] + i for i in items], size, spacing)


def numbered(slide, y, items, size=15):
    return textbox(slide, 0.7, y, 9.6, 5.5, [[(f"{i}. ", False), (h + " ", True), (b, False)] for i, (h, b) in enumerate(items, 1)], size, 1.25, after=8)


def picture(slide, name, x, y, w):
    return slide.shapes.add_picture(str(ROOT / "figures" / name), Inches(x), Inches(y), width=Inches(w))


def table(slide, x, y, widths, rows, size=11, row_h=0.4, bold_first_col=False):
    gt = slide.shapes.add_table(len(rows), len(widths), Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * len(rows)))
    t = gt.table
    for j, w in enumerate(widths):
        t.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor(0xD9, 0xD9, 0xD9) if i == 0 else RGBColor(0xF2, 0xF2, 0xF2)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = c.text_frame.paragraphs[0]
            c.text_frame.word_wrap = True
            run(p, val, size, bold=(i == 0 or (bold_first_col and j == 0)))
    return t


def pm(a, b):
    return f"{a:.2f} ± {b:.2f}"


# 1. Title (template slide, edited in place)
s1 = prs.slides[0]
for sh in s1.shapes:
    if sh.name == "object 3":
        sh.text_frame.text = "Domain Shift in Artificial Neural Networks: A Survey of Domain Adaptation Techniques"
        p = sh.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        for r in p.runs:
            r.font.size, r.font.bold = Pt(26), True
    elif sh.name == "object 5":
        sh.left, sh.top, sh.width = Inches(0.5), Inches(5.6), Inches(3.8)
        tf = sh.text_frame
        tf.clear()
        tf.paragraphs[0].line_spacing = 1.2
        run(tf.paragraphs[0], "Guide Name:", 14, bold=True)
        for t in ("Dr. Kothai G", "Department of Computational Intelligence"):
            p = tf.add_paragraph()
            p.line_spacing = 1.2
            run(p, t, 14)
    elif sh.name == "object 6":
        sh.left, sh.top, sh.width = Inches(4.9), Inches(5.6), Inches(5.6)
        tf = sh.text_frame
        tf.clear()
        tf.paragraphs[0].line_spacing = 1.2
        run(tf.paragraphs[0], "Student Name & Registration Number", 14, bold=True)
        for n, r in (("Jai", "RA2411026010131"), ("Aggam Singh Arora", "RA2411026010139"),
                     ("Areeb Akhtar", "RA2411026010154"), ("Ujwal M", "RA2411026010157")):
            p = tf.add_paragraph()
            p.line_spacing = 1.2
            run(p, f"{n} - {r}", 14)
textbox(s1, 0.9, 4.15, 9.2, 0.9, ["Case Study Review: 21CSE326T Artificial Neural Networks",
                                  "SRM Institute of Science and Technology, Kattankulathur"], size=14, justify=False).text_frame.paragraphs
for p in s1.shapes[-1].text_frame.paragraphs:
    p.alignment = PP_ALIGN.CENTER

# 2. Introduction
s = new_slide("Introduction")
bullets(s, 2.15, [
    "Neural networks assume that training and deployment data come from the same distribution. Under domain shift this fails, and held-out accuracy gives no warning.",
    "Zech et al. (2018): pneumonia CNNs did worse at outside hospitals in 3 of 5 comparisons and identified the hospital system with 99.95% (NIH) and 99.98% (Mount Sinai) accuracy.",
    "Domain adaptation uses unlabeled target data to reduce the gap. The figure shows the families of methods surveyed.",
], size=15)
picture(s, "taxonomy.png", 1.5, 4.7, 8.0)

# 3. Abstract
s = new_slide("Abstract")
bullets(s, 2.15, [
    "This work surveys domain shift in neural networks and the main families of domain adaptation methods: fine-tuning, discrepancy-based (DAN, Deep CORAL), adversarial (DANN, ADDA), normalization-based (AdaBN, TENT), pixel-level (CyCADA) and domain generalization.",
    "A controlled experiment trains one small CNN on MNIST and tests it on MNIST-M, comparing source-only, target-only, AdaBN and DANN with the same network, data and training recipe.",
    f"Over three seeds, MNIST-M accuracy is {S['source_only']['mnistm_mean']:.2f}% for source-only, {S['adabn']['mnistm_mean']:.2f}% for AdaBN, {S['dann']['mnistm_mean']:.2f}% for DANN and {S['target_only']['mnistm_mean']:.2f}% for target-only.",
    "AdaBN closed more of the gap than DANN in every seed. DANN's domain loss reached ln 2, yet t-SNE still shows the two domains apart.",
    "The benchmark is a toy one, so the conclusions are limited accordingly.",
], size=17, spacing=1.4)

# 4. Problem statement
s = new_slide("Problem Statement")
bullets(s, 2.15, [
    "A model trained on a source domain loses accuracy on a target domain, and target labels are usually not available.",
    f"Source accuracy hides the loss: the same network scores {S['source_only']['mnist_mean']:.2f}% on MNIST and {S['source_only']['mnistm_mean']:.2f}% on MNIST-M.",
    "Question: using only unlabeled target images, how much of the lost accuracy can AdaBN and DANN recover under an identical network, data and training recipe?",
    "Published comparisons use different networks, data sizes and recipes, which makes the answer hard to read from the literature.",
], size=18, spacing=1.5)

# 5-7. Literature survey
HEAD = ["S.No.", "Title / Author / Publication", "Methodology", "Research Gap / Limitation", "Result / Contribution"]
LIT = [
    ["Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs. Zech et al., PLOS Medicine, 2018",
     "CNNs trained on chest X-rays from hospital systems, tested internally and at outside hospitals",
     "Studies the failure only; proposes no adaptation method",
     "Lower accuracy at outside hospitals in 3 of 5 comparisons; hospital system identified at 99.95% (NIH) and 99.98% (Mount Sinai)"],
    ["A theory of learning from different domains. Ben-David et al., Machine Learning, 2010",
     "Theoretical analysis of target error under domain shift",
     "A guarantee, not a training method; the divergence term is hard to compute exactly",
     "Target error is bounded by source error plus domain divergence plus the error of the best joint hypothesis"],
    ["Deep visual domain adaptation: A survey. Wang and Deng, Neurocomputing, 2018",
     "Survey of deep domain adaptation for visual recognition",
     "No controlled comparison of the methods",
     "Organizes deep adaptation methods by training loss and data setting"],
    ["Domain generalization: A survey. Zhou et al., IEEE TPAMI, 2023",
     "Survey of methods that use no target data at training time",
     "Survey only; no new experiments",
     "Taxonomy of domain generalization methods and open problems"],
    ["Learning transferable features with deep adaptation networks (DAN). Long et al., ICML, 2015",
     "Multi-kernel MMD penalty on task-specific layers",
     "Needs a kernel choice and unlabeled target data at training time",
     "Higher target accuracy than baselines on standard image benchmarks"],
    ["Deep CORAL: Correlation alignment for deep domain adaptation. Sun and Saenko, ECCV Workshops, 2016",
     "Differentiable loss that aligns feature covariances of source and target",
     "Aligns second-order statistics only",
     "Simple loss that adds no parameters; competitive on Office-31"],
    ["Unsupervised domain adaptation by backpropagation (DANN). Ganin and Lempitsky, ICML, 2015",
     "Domain classifier trained jointly with the features through a gradient reversal layer",
     "Adversarial training can be unstable; needs unlabeled target data",
     "MNIST to MNIST-M: 57.5% source-only to 81.5% with DANN (their setup)"],
    ["Domain-adversarial training of neural networks. Ganin et al., JMLR, 2016",
     "Full DANN formulation with theory and the lambda schedule",
     "Aligns marginal feature distributions only",
     "Evaluated on image classification and person re-identification"],
    ["Adversarial discriminative domain adaptation (ADDA). Tzeng et al., CVPR, 2017",
     "Untied target encoder trained against a domain discriminator",
     "Multi-stage adversarial training",
     "Competitive results on digit and Office adaptation tasks"],
    ["Revisiting batch normalization for practical domain adaptation (AdaBN). Li et al., arXiv, 2016",
     "Replace batch-norm statistics with target statistics; no training",
     "Only for networks with batch norm; adapts means and variances only",
     "Gains with no extra training; can be combined with other methods"],
    ["CyCADA: Cycle-consistent adversarial domain adaptation. Hoffman et al., ICML, 2018",
     "Pixel-level translation and feature-level adaptation with cycle consistency",
     "Heavy: needs generative adversarial training",
     "Adaptation on digit benchmarks and synthetic-to-real segmentation (GTA5 to Cityscapes)"],
    ["Tent: Fully test-time adaptation by entropy minimization. Wang et al., ICLR, 2021",
     "Minimize prediction entropy on test batches, updating batch-norm scale and shift",
     "Needs test batches and relies on confident predictions",
     "Lower error under corruption and shift without source data or labels"],
]
for k in range(3):
    s = new_slide("Literature Survey" + (" (Contd.)" if k else ""))
    rows = [HEAD] + [[str(k * 4 + i + 1)] + r for i, r in enumerate(LIT[k * 4:(k + 1) * 4])]
    table(s, 0.6, 2.2, [0.5, 2.5, 2.2, 2.1, 2.1], rows, size=10.5, row_h=1.2)

# 8. Research gaps
s = new_slide("Research Gaps")
numbered(s, 2.15, [
    ("Inconsistent comparison:", "methods are reported with different networks, data sizes and training recipes, so their results cannot be compared directly."),
    ("Cheap baselines:", "a normalization-only method such as AdaBN needs no training and is a useful reference next to adversarial methods."),
    ("Domain loss as a signal:", "a domain classifier at chance is often read as aligned features, but invariant representations have limits (Zhao et al., 2019)."),
    ("Real shifts:", "benchmark shifts are mostly synthetic or curated, while deployment shifts such as hospitals are harder to benchmark."),
    ("Variance:", "single-run results hide seed variance, which is large for adversarial training."),
], size=17)

# 9. Objectives
s = new_slide("Objectives")
numbered(s, 2.15, [
    ("", "To survey the types of domain shift and the main families of domain adaptation methods."),
    ("", "To compare source-only, AdaBN, DANN and a target-only upper bound on MNIST to MNIST-M with one network and one training recipe."),
    ("", "To report mean and standard deviation over seeds 0, 1 and 2, with every individual seed shown."),
    ("", "To measure the share of the source-to-target accuracy gap that each method closes."),
    ("", "To inspect the learned features with t-SNE and compare them with the DANN domain loss."),
    ("", "To publish the code, results and report so the experiment can be reproduced."),
], size=17)

# 10. Methodology
s = new_slide("Methodology")
picture(s, "architecture.png", 1.2, 2.1, 8.6)
bullets(s, 6.05, [
    [("Source-only / target-only: ", True), ("train on MNIST or MNIST-M labels. Target-only is the upper bound.", False)],
    [("AdaBN: ", True), ("replace batch-norm statistics with target statistics, no training. MNIST is scored with source statistics.", False)],
    [("DANN: ", True), ("domain classifier behind a gradient reversal layer (identity forward, -lambda times gradient backward), lambda = 2 / (1 + exp(-10p)) - 1.", False)],
], size=13, spacing=1.2)

# 11. Experimental setup
s = new_slide("Experimental Setup")
picture(s, "samples.png", 0.7, 2.1, 9.6)
cfg = R["config"]
table(s, 0.7, 4.7, [2.2, 7.4], [
    ["Item", "Value"],
    ["Domains", "MNIST (source), MNIST-M from Hugging Face Mike0307/MNIST-M (target); 32x32, 3 channels"],
    ["Data", f"{cfg['n_train_per_domain']:,} training images per domain; full test sets ({cfg['n_test_mnist']:,} and {cfg['n_test_mnistm']:,})"],
    ["Backbone", "3 x Conv-BN-ReLU-MaxPool (32, 64, 128), Linear 2048 to 128, Linear 128 to 10"],
    ["Optimizer", "SGD, momentum 0.9, lr = 0.01 / (1 + 10p)^0.75"],
    ["Training", f"batch size {cfg['batch_size']}, {cfg['epochs']} epochs, seeds 0, 1, 2, CPU only"],
], size=11, row_h=0.5, bold_first_col=True)

# 12. Comparative analysis
s = new_slide("Comparative Analysis of Models")
names = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
rows = [["Method", "MNIST acc. (%)", "MNIST-M acc. (%)", "Gap closed (%)"]]
for k, v in S.items():
    g = "-" if k == "source_only" else ("100 (by definition)" if k == "target_only" else f"{v['gap_mean']:.1f} ± {v['gap_std']:.1f}")
    rows.append([names[k], pm(v["mnist_mean"], v["mnist_std"]), pm(v["mnistm_mean"], v["mnistm_std"]), g])
table(s, 0.7, 2.15, [2.0, 2.4, 2.6, 2.6], rows, size=12, row_h=0.42, bold_first_col=True)
textbox(s, 0.7, 4.35, 9.6, 0.3, ["Mean ± std over seeds 0, 1, 2. AdaBN is ahead of DANN in every seed."], size=12, justify=False)
picture(s, "results_bar.png", 1.9, 4.8, 6.4)

# 13. Feature space
s = new_slide("Feature-Space Analysis")
picture(s, "tsne.png", 0.7, 2.1, 9.6)
bullets(s, 6.65, [
    "DANN's domain loss reached ln 2 (about 0.693), the value for a chance-level domain classifier.",
    "Source and target features still sit in separate regions, so a chance-level domain loss did not mean aligned features.",
    "The plot shows seed 0 only; it is a visual check, not a measurement.",
], size=13, spacing=1.2)

# 14. Conclusion and limitations
s = new_slide("Conclusion and Limitations")
bullets(s, 2.15, [
    "Domain shift is a deployment risk that held-out source accuracy does not reveal.",
    f"AdaBN closed {S['adabn']['gap_mean']:.1f}% of the gap with no training. DANN closed {S['dann']['gap_mean']:.1f}% with larger variation across seeds. AdaBN was ahead in every seed.",
    "Reporting a normalization-only baseline next to adversarial methods is cheap and informative.",
], size=16, spacing=1.4)
textbox(s, 0.7, 4.75, 9.6, 0.4, [[("Limitations", True)]], size=15, justify=False)
bullets(s, 5.2, [
    "Toy benchmark with a synthetic shift, a small CNN, 10,000 images per domain and 3 seeds.",
    "Why DANN trails AdaBN here was not tested; mixed batch-norm statistics and small data are candidates.",
    "Not directly comparable to Ganin and Lempitsky (57.5% source-only, 81.5% DANN): different network, data size and MNIST-M copy.",
    "Only AdaBN and DANN were run; the other surveyed methods are described, not implemented.",
], size=14, spacing=1.25)

# 15. References
s = new_slide("References")
REFS = [
    "J. R. Zech et al., “Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs,” PLOS Medicine, vol. 15, no. 11, e1002683, 2018.",
    "S. Ben-David et al., “A theory of learning from different domains,” Machine Learning, vol. 79, pp. 151-175, 2010.",
    "Y. Ganin and V. Lempitsky, “Unsupervised domain adaptation by backpropagation,” ICML, PMLR 37, pp. 1180-1189, 2015.",
    "Y. Ganin et al., “Domain-adversarial training of neural networks,” JMLR, vol. 17, no. 59, pp. 1-35, 2016.",
    "Y. Li et al., “Revisiting batch normalization for practical domain adaptation,” arXiv:1603.04779, 2016.",
    "M. Long et al., “Learning transferable features with deep adaptation networks,” ICML, PMLR 37, pp. 97-105, 2015.",
    "B. Sun and K. Saenko, “Deep CORAL: Correlation alignment for deep domain adaptation,” ECCV Workshops, LNCS 9915, pp. 443-450, 2016.",
    "E. Tzeng et al., “Adversarial discriminative domain adaptation,” CVPR, pp. 7167-7176, 2017.",
    "J. Hoffman et al., “CyCADA: Cycle-consistent adversarial domain adaptation,” ICML, PMLR 80, pp. 1989-1998, 2018.",
    "D. Wang et al., “Tent: Fully test-time adaptation by entropy minimization,” ICLR, 2021.",
    "M. Wang and W. Deng, “Deep visual domain adaptation: A survey,” Neurocomputing, vol. 312, pp. 135-153, 2018.",
    "K. Zhou et al., “Domain generalization: A survey,” IEEE TPAMI, vol. 45, no. 4, pp. 4396-4415, 2023.",
    "H. Zhao et al., “On learning invariant representations for domain adaptation,” ICML, PMLR 97, pp. 7523-7532, 2019.",
]
textbox(s, 0.7, 2.1, 9.6, 6, [[(f"{i}. ", False), (r, False)] for i, r in enumerate(REFS, 1)], size=11, spacing=1.1, after=4)

# Thank You slide goes last
ids = prs.slides._sldIdLst
ty = next(e for e in ids if prs.part.related_part(e.rId).slide is thanks)
ids.remove(ty)
ids.append(ty)

prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
