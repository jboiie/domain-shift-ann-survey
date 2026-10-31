import json
from pathlib import Path
from docx.enum.text import WD_BREAK
from docx.shared import Inches, Pt
from docx_helpers import *

ROOT = Path(__file__).resolve().parents[1]  # repository root
R = json.load(open(ROOT / "results" / "results.json"))
S = R["summary"]
CFG = R["config"]

TITLE = "DOMAIN SHIFT IN ARTIFICIAL NEURAL NETWORKS: A SURVEY OF DOMAIN ADAPTATION TECHNIQUES"
TITLE_CASE = "Domain Shift in Artificial Neural Networks: A Survey of Domain Adaptation Techniques"
AUTHORS = [("Jai", "RA2411026010131"), ("Aggam Singh Arora", "RA2411026010139"),
           ("Areeb Akhtar", "RA2411026010154"), ("Ujwal M", "RA2411026010157")]

FIGS, TABS = [], []


def acc(k, d):
    return f"{S[k][d + '_mean']:.1f}"


def pm(k, d):
    return f"{S[k][d + '_mean']:.2f} ± {S[k][d + '_std']:.2f}"


def gap(k):
    return f"{S[k]['gap_mean']:.1f}"


def fig(doc, path, title, desc, width=6.0, expect=None):
    n = len(FIGS) + 1
    assert expect is None or n == expect, (title, n, expect)
    FIGS.append((n, title, desc))
    figure(doc, str(path), f"Figure {n}: {title}", width)


def tab(doc, title, desc, header, rows, widths, size=10, expect=None, **kw):
    n = len(TABS) + 1
    assert expect is None or n == expect, (title, n, expect)
    TABS.append((n, title, desc))
    table(doc, f"Table {n}: {title}", header, rows, widths, size, **kw)


def center(doc, text, size=12, bold=False, italic=False, after=4, spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = C
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = spacing
    _r = p.add_run(text)
    _r.bold, _r.italic = bold, italic
    _r.font.size = Pt(size)
    _r.font.name = FONT
    return p


def plain_heading(doc, text, size=14, page_break=True):
    p = center(doc, text, size, True, after=14)
    p.paragraph_format.page_break_before = page_break
    return p


def front_matter(doc):
    center(doc, TITLE, 15, True, after=14)
    center(doc, "A PROJECT REPORT", 12, after=10)
    center(doc, "Submitted by", 12, italic=True, after=6)
    for n, r in AUTHORS:
        center(doc, f"{n} ({r})", 13, after=3)
    center(doc, "Under the Guidance of", 12, italic=True, after=6).paragraph_format.space_before = Pt(8)
    center(doc, "Dr. KOTHAI G", 13, after=2)
    center(doc, "(Assistant Professor, Department of Computational Intelligence)", 11, after=8)
    center(doc, "in partial fulfillment of the requirements for the degree of", 11, italic=True, after=6)
    center(doc, "BACHELOR OF TECHNOLOGY", 13, after=2)
    center(doc, "in", 12, after=2)
    center(doc, "COMPUTER SCIENCE AND ENGINEERING", 13, after=2)
    center(doc, "with specialization in (ARTIFICIAL INTELLIGENCE & MACHINE LEARNING)", 12, after=14)
    p = doc.add_paragraph()
    p.alignment = C
    p.add_run().add_picture(str(ROOT / "report" / "assets" / "srm_logo.jpeg"), width=Inches(3.0))
    p.paragraph_format.space_after = Pt(18)
    for t in ("DEPARTMENT OF COMPUTATIONAL INTELLIGENCE", "COLLEGE OF ENGINEERING AND TECHNOLOGY",
              "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", "KATTANKULATHUR - 603 203", "NOVEMBER 2026"):
        center(doc, t, 13, after=4)

    # Bonafide certificate
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.add_run().add_picture(str(ROOT / "report" / "assets" / "srm_logo.jpeg"), width=Inches(1.8))
    center(doc, "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", 14, after=2).paragraph_format.space_before = Pt(12)
    center(doc, "KATTANKULATHUR - 603 203", 14, after=14)
    center(doc, "BONAFIDE CERTIFICATE", 13, True, after=14)
    names = ", ".join(f"{n} ({r})" for n, r in AUTHORS)
    para(doc, f"Certified that **21CSE326T - Artificial Neural Networks** - Project report titled "
              f"“{TITLE_CASE}” is the bonafide work of “{names}” who carried out the project work "
              "under my supervision. Certified further, that to the best of my knowledge the work reported herein does not form "
              "any other project report or dissertation on the basis of which a degree or award was conferred on an earlier "
              "occasion on this or any other candidate.")
    for _ in range(4):
        doc.add_paragraph()
    t = doc.add_table(rows=1, cols=2)
    t.autofit = False
    blocks = [("SIGNATURE", ["Dr. KOTHAI G", "Faculty In-Charge", "Assistant Professor,", "Department of Computational Intelligence"]),
              ("SIGNATURE", ["Dr. ANNIE UTHRA R", "Professor & Head,", "Department of Computational Intelligence"])]
    for cell, (sig, lines) in zip(t.rows[0].cells, blocks):
        cell.width = Inches(3.1)
        cell.paragraphs[0].paragraph_format.line_spacing = 1.0
        cell.paragraphs[0].alignment = L
        r = cell.paragraphs[0].add_run(sig)
        r.bold = True
        r.font.size = Pt(10)
        r.font.name = FONT
        for i, ln in enumerate(lines):
            q = cell.add_paragraph()
            q.alignment = L
            q.paragraph_format.line_spacing = 1.0
            q.paragraph_format.space_after = Pt(0)
            q.paragraph_format.space_before = Pt(6 if i == 0 else 0)
            rr = q.add_run(ln)
            rr.bold = i == 0
            rr.font.size = Pt(10)
            rr.font.name = FONT

    # Acknowledgements
    plain_heading(doc, "ACKNOWLEDGEMENTS")
    for t_ in [
        "We express our humble gratitude to Dr. C. Muthamizhchelvan, Vice-Chancellor, SRM Institute of Science and Technology, "
        "for the facilities extended for the project work and for his continued support.",
        "We extend our sincere thanks to Dr. Leenus Jesu Martin M, Dean-CET, SRM Institute of Science and Technology, "
        "for his invaluable support.",
        "We wish to thank Dr. Revathi Venkataraman, Professor and Chairperson, School of Computing, SRM Institute of Science "
        "and Technology, for her support throughout the project work.",
        "We extend our sincere thanks to Dr. M. Pushpalatha, Professor and Associate Chairperson - CS, School of Computing, and "
        "Dr. Lakshmi, Professor and Associate Chairperson - AI, School of Computing, SRM Institute of Science and Technology, "
        "for their invaluable support.",
        "We are grateful to our Head of the Department, Dr. Annie Uthra R, Professor and Head, Department of Computational "
        "Intelligence, SRM Institute of Science and Technology, for her suggestions and encouragement at all stages of the "
        "project work.",
        "We thank our Project Coordinators, Panel Head and Panel Members, Department of Computational Intelligence, SRM "
        "Institute of Science and Technology, for their inputs during the project reviews and for their support.",
        "We thank our Faculty Advisor, Dr. Abhijah Roseline S, Department of Computational Intelligence, SRM Institute of "
        "Science and Technology, for guiding us through the course.",
        "We are deeply grateful to our guide, Dr. Kothai G, Department of Computational Intelligence, SRM Institute of Science "
        "and Technology, for giving us the opportunity to pursue this project under their mentorship. They gave us the "
        "freedom and support to explore research topics of our interest, and their enthusiasm for solving problems has been "
        "a constant source of inspiration.",
        "We thank all the staff members of the Department of Computational Intelligence, School of Computing, SRM Institute of "
        "Science and Technology, for their help during the project. Finally, we thank our parents, family members and "
        "friends for their constant love, support and encouragement.",
    ]:
        para(doc, t_)

    # Table of contents
    plain_heading(doc, "TABLE OF CONTENTS")
    toc(doc)


def abstract(doc):
    chapter(doc, "ABSTRACT", None)
    para(doc, "Neural networks are trained on samples from one data distribution and then used on another. When the two "
              "differ, accuracy can fall sharply even though the task is unchanged. This is called domain shift. A study of "
              "pneumonia-detection networks on chest X-rays found lower accuracy at outside hospitals in 3 of 5 comparisons, "
              "and the same networks could identify the source hospital of an X-ray with more than 99.9% accuracy on two of "
              "the sites. This report surveys methods that reduce the effect of domain shift: fine-tuning, discrepancy-based "
              "methods (DAN, Deep CORAL), adversarial methods (DANN, ADDA), adaptive batch normalization (AdaBN), pixel-level "
              "translation and augmentation, domain generalization, and test-time adaptation (TENT). The methods are compared "
              "on whether they need target labels, whether they need target data during training, compute cost, implementation "
              "effort and typical failure modes.")
    para(doc, f"A small worked example supports the survey. A convolutional network is trained on MNIST (source) and tested on "
              f"MNIST-M (target), a version of MNIST with coloured natural-image backgrounds. Training uses "
              f"{CFG['n_train_per_domain']:,} images per domain, {CFG['epochs']} epochs, the SGD recipe of Ganin et al. and "
              f"{len(CFG['seeds'])} random seeds, and results are reported as mean accuracy over the seeds. The source-only model "
              f"reaches {acc('source_only', 'mnist')}% on MNIST but only {acc('source_only', 'mnistm')}% on MNIST-M. A model trained "
              f"on labeled MNIST-M reaches {acc('target_only', 'mnistm')}%, which is the ceiling. AdaBN, which needs no training, "
              f"raises MNIST-M accuracy to {acc('adabn', 'mnistm')}% ({gap('adabn')}% of the gap closed) and leaves MNIST accuracy "
              f"unchanged. DANN, trained with labeled MNIST and unlabeled MNIST-M, reaches {acc('dann', 'mnistm')}% "
              f"({gap('dann')}% of the gap closed), less than AdaBN in every seed. A t-SNE view of the learned features shows that "
              f"the two domains remain separate after DANN. The digits are a toy benchmark, and the report discusses why real "
              f"shifts such as those in medical imaging are harder.")


# ---------------------------------------------------------------- Chapter 1
def ch1(doc):
    chapter(doc, "CHAPTER 1", "INTRODUCTION")
    h2(doc, "1.1 Background of the Problem")
    para(doc, "An artificial neural network learns a mapping from inputs to outputs using a finite set of training examples. "
              "Standard machine learning theory assumes that the training examples and the examples seen after deployment are "
              "drawn independently from the same distribution (the i.i.d. assumption). Under this assumption, accuracy on a "
              "held-out test set estimates accuracy in use.")
    para(doc, "In practice the assumption often fails. A model is trained on data from one hospital, one camera, one season or "
              "one city, and is then applied somewhere else. The training distribution is called the source domain and the "
              "deployment distribution is called the target domain. The difference between them is called domain shift or "
              "dataset shift [Quiñonero-Candela et al., 2009]. Domain shift is not a rare corner case: it appears whenever the "
              "conditions of data collection change, and a network that scores highly on its own test set can perform poorly "
              "on the target domain.")
    para(doc, "Domain adaptation is the area of machine learning that studies how to reduce this loss of accuracy. It is a "
              "special case of transfer learning [Pan and Yang, 2010] in which the task stays the same and only the input "
              "distribution (or its relation to the labels) changes.")

    h2(doc, "1.2 Motivation")
    para(doc, "The clearest evidence of the problem comes from medicine. Zech et al. (2018) trained convolutional neural "
              "networks (CNNs) to detect pneumonia on chest X-rays from three sources: the NIH Clinical Center, Mount Sinai "
              "Hospital and Indiana University Network for Patient Care. In 3 of 5 natural comparisons, performance on X-rays "
              "from outside hospitals was significantly lower than on held-out X-rays from the hospitals used for training. "
              "The authors also found that the CNNs could identify the hospital system that produced an X-ray with very high "
              "accuracy: 99.95% for the NIH images and 99.98% for the Mount Sinai images. Scanner settings, image processing and "
              "markers differ between hospitals, so a network can use these cues. The network learned patterns specific to where "
              "its training data came from, and not only the signs of disease. A model that looks accurate in internal "
              "validation can therefore be less reliable in a new hospital.")
    para(doc, "The same effect appears in driving. A perception model trained on images taken in clear daytime weather is "
              "usually less accurate in rain, fog or at night, because the pixel statistics of the scene change while the "
              "objects to be recognised stay the same. Work on foggy scene understanding is one example of research motivated "
              "by this gap [Sakaridis et al., 2018].")
    para(doc, "These real cases are difficult to reproduce and measure. This project therefore uses a controlled version of the "
              "same problem. A network trained on clean handwritten digits (MNIST) is tested on digits drawn over natural-image "
              "backgrounds in random colours (MNIST-M). The label set is identical, the digit shapes are the same, and only the "
              "appearance changes. The drop in accuracy can be measured exactly, and the methods in the survey can be compared "
              "under identical conditions.")

    h2(doc, "1.3 Problem Statement")
    para(doc, "A neural network trained on a labeled source domain performs well on source data but loses accuracy on a target "
              "domain whose input distribution differs. Collecting and labeling new data for every new deployment condition is "
              "expensive and, in medicine, often impractical. There is a need to understand:")
    bullets(doc, ["why neural networks are sensitive to domain shift;",
                  "which families of domain adaptation methods exist and what each requires in terms of labels, data and compute;",
                  "how much of the lost accuracy simple and adversarial methods recover under a fair, controlled comparison."])

    h2(doc, "1.4 Research Objectives")
    para(doc, "The main objectives of this project are:")
    numbered(doc, ["To define domain shift (covariate, label and concept shift) and explain why the i.i.d. assumption breaks.",
                   "To explain why neural networks are vulnerable to domain shift, using generalization, overfitting and inductive bias.",
                   "To survey the main domain adaptation methods and compare them on target-label need, target-data need, compute "
                   "cost, implementation complexity and failure modes.",
                   "To demonstrate domain shift with a small CNN trained on MNIST and tested on MNIST-M.",
                   "To implement and compare AdaBN and DANN against source-only and target-only baselines using the same backbone, "
                   "and to report the share of the accuracy gap each one closes."])
    para(doc, "The project is aligned with two United Nations Sustainable Development Goals. **SDG 3: Good Health and Well-being**: "
              "diagnostic models are increasingly trained at one hospital and used at others, and the Zech et al. study shows that "
              "unnoticed domain shift can make them unreliable. Methods that detect and reduce domain shift support safer "
              "deployment of AI in health care. **SDG 9: Industry, Innovation and Infrastructure**: industrial and transport "
              "systems, such as visual inspection and driver assistance, operate under changing conditions, and robust "
              "adaptation methods help build dependable intelligent infrastructure.")

    h2(doc, "1.5 Scope of the Study")
    para(doc, "This study is a literature survey with a small supporting experiment. The scope includes:")
    bullets(doc, ["A survey of domain adaptation methods for image classification: fine-tuning, discrepancy-based, adversarial, "
                  "normalization-based, pixel-level, domain generalization and test-time adaptation.",
                  "An experiment on one digit pair: MNIST as the source and MNIST-M as the target.",
                  "Four experimental settings with one shared CNN backbone: source-only, AdaBN, DANN and target-only.",
                  f"A subsample of {CFG['n_train_per_domain']:,} training images per domain, {CFG['epochs']} training epochs and "
                  f"{len(CFG['seeds'])} random seeds, so that every run finishes in minutes on a CPU."])
    para(doc, "The study does not implement the other surveyed methods (DAN, Deep CORAL, ADDA, CyCADA, TENT), does not use "
              "medical images, and does not tune hyperparameters for the best possible accuracy.")

    h2(doc, "1.6 Significance and Expected Contributions")
    para(doc, "The report gives a single, readable account of how domain shift arises in neural networks and how it is handled. "
              "The expected contributions are:")
    bullets(doc, ["A structured taxonomy and a comparison table of domain adaptation methods that can be used to choose a method "
                  "for a given situation.",
                  "A reproducible demonstration of domain shift on MNIST and MNIST-M, with all numbers produced by the project "
                  "notebook.",
                  "A like-for-like comparison of a training-free method (AdaBN) and an adversarial method (DANN) on the same "
                  "backbone, with the share of the accuracy gap closed.",
                  "A discussion of the limits of the experiment and of open challenges for real-world domain shift."])


# ---------------------------------------------------------------- Chapter 2
def ch2(doc):
    chapter(doc, "CHAPTER 2", "LITERATURE SURVEY")
    h2(doc, "2.1 Overview of the Research Area")
    h3(doc, "2.1.1 Source and target domains")
    para(doc, "A domain consists of an input space and a probability distribution over it. In domain adaptation there is a "
              "source domain with labeled data, where the model is trained, and a target domain, where the model will be used. "
              "Both share the same task and label set. In *unsupervised* domain adaptation (UDA) the target data are available "
              "without labels. In *supervised* domain adaptation a few labeled target samples are available. Wang and Deng "
              "(2018) give a survey of deep methods for these settings in visual recognition.")
    h3(doc, "2.1.2 Types of shift")
    para(doc, "Let X be the input and Y the label. Three kinds of shift are usually distinguished.")
    bullets(doc, ["**Covariate shift:** the input distribution P(X) changes but the rule linking inputs to labels, P(Y|X), stays "
                  "the same [Shimodaira, 2000]. MNIST to MNIST-M is of this kind: the digit still determines the label, but the "
                  "images look different. Chest X-rays from two scanners are another example.",
                  "**Label shift (prior shift):** the label distribution P(Y) changes while P(X|Y) stays the same. A pneumonia "
                  "classifier trained at a hospital where 10% of patients have pneumonia and used at a hospital where 40% do is "
                  "an example.",
                  "**Concept shift:** the relation P(Y|X) itself changes. The same input should now receive a different label, "
                  "for example when a diagnostic criterion is revised or when the meaning of a word changes over time."])
    para(doc, "Real shifts usually combine these. Most methods in this survey target covariate shift, because it is the case "
              "that can be addressed without target labels.")
    h3(doc, "2.1.3 Why the i.i.d. assumption breaks")
    para(doc, "Generalization guarantees assume that test examples come from the same distribution as training examples. When "
              "deployment data come from a different distribution, the held-out validation accuracy measured on source data no "
              "longer estimates target accuracy. The network is not malfunctioning: it is being asked a question outside the "
              "distribution it was trained on.")
    h3(doc, "2.1.4 Why neural networks are vulnerable")
    para(doc, "The vulnerability can be tied to three topics from the course syllabus.")
    bullets(doc, ["**Generalization and overfitting (Unit 3, Session 23).** A network that fits its training data well can still "
                  "fail on new data. Domain shift is a specific form of this: the network generalizes to unseen samples from the "
                  "*same* distribution, but not to samples from a different one. Any feature that helps on the training set, "
                  "including a spurious one such as the background, scanner type or hospital marker, will be used.",
                  "**Hypothesis space and inductive bias (Unit 3, Session 22).** A CNN is flexible enough to represent many "
                  "functions that agree on the source data and disagree on the target data. Training on source data alone gives "
                  "no reason to prefer the function that ignores the background. Its inductive bias (locality, weight sharing) "
                  "does not encode which image properties are irrelevant to the label.",
                  "**Data selection and preprocessing (Unit 5, Session 37).** The training set determines what the model can "
                  "learn. Data collected under narrow conditions, and normalization computed on those data, bake the source "
                  "conditions into the model. Batch normalization statistics are an example: they are estimated on source data "
                  "and fixed at test time, which is what AdaBN later changes."])
    para(doc, "Ben-David et al. (2010) give a bound that expresses this formally. For a hypothesis h, the target error is "
              "bounded by the source error plus a term that measures how different the two domains look to the hypothesis "
              "class, plus a term for the error of the best single hypothesis on both domains:")
    para(doc, "ε_T(h) ≤ ε_S(h) + ½ d_HΔH(D_S, D_T) + λ", align=C, italic=True)
    para(doc, "In words, target error is small only if (a) the model is accurate on the source, (b) the two domains are hard to "
              "tell apart with the available hypotheses, and (c) some hypothesis does well on both domains. Training on the source "
              "only controls the first term. The methods in this survey try to shrink the second term, either by making features "
              "of the two domains look alike (discrepancy-based, adversarial, normalization-based methods) or by making the "
              "inputs look alike (pixel-level methods).")

    h2(doc, "2.2 Existing Models and Frameworks")
    para(doc, "Domain adaptation methods can be grouped by how they reduce the difference between domains. Figure 1 shows the "
              "taxonomy used in this report.")
    fig(doc, str(ROOT / "figures/taxonomy.png"), "Taxonomy of domain shift handling methods",
        "Groups the surveyed methods into supervised adaptation, discrepancy-based, adversarial, normalization and pixel-level, "
        "and methods that go beyond adaptation.", 6.3, expect=1)

    h3(doc, "2.2.1 Fine-tuning with a few labeled target samples (supervised DA)")
    para(doc, "The simplest approach continues training a source-trained network on a small labeled target set, usually with a "
              "lower learning rate. It needs no new algorithm and works well when a few labels are available. Its limits are "
              "overfitting to the small target set and forgetting of source knowledge. Labeling target data is the cost that "
              "the other methods try to avoid.")
    h3(doc, "2.2.2 Discrepancy-based methods")
    para(doc, "These methods add a loss that measures the distance between source and target feature distributions and minimize "
              "it together with the classification loss.")
    bullets(doc, ["**DAN (Deep Adaptation Network)** [Long et al., 2015] adds a multi-kernel maximum mean discrepancy (MK-MMD) "
                  "penalty on the activations of the task-specific layers of a CNN. MMD is the distance between the mean "
                  "embeddings of two distributions in a kernel feature space.",
                  "**Deep CORAL** [Sun and Saenko, 2016] aligns the second-order statistics, the feature covariance matrices, "
                  "of source and target. The loss is the squared Frobenius distance between the two covariance matrices, and it "
                  "is differentiable and cheap to add to a network."])
    h3(doc, "2.2.3 Adversarial methods")
    para(doc, "These methods train a domain classifier to tell source features from target features, while the feature extractor "
              "is trained to make this impossible.")
    bullets(doc, ["**DANN (Domain-Adversarial Neural Network)** [Ganin and Lempitsky, 2015; Ganin et al., 2016] attaches a domain "
                  "classifier to the feature extractor through a gradient reversal layer (GRL). The GRL is the identity in the "
                  "forward pass and multiplies the gradient by a negative constant in the backward pass. The domain classifier "
                  "therefore learns to separate the domains, while the feature extractor receives the reversed gradient and "
                  "learns features that confuse it. The label classifier is trained on labeled source data only. The method is "
                  "motivated by the domain-divergence term in the Ben-David bound.",
                  "**ADDA (Adversarial Discriminative Domain Adaptation)** [Tzeng et al., 2017] first trains a source encoder and "
                  "classifier with labels. It then learns a separate target encoder, with untied weights, against a domain "
                  "discriminator using a GAN-style loss, and applies the source classifier to the target encoder output."])
    h3(doc, "2.2.4 Normalization-based methods")
    para(doc, "**AdaBN (Adaptive Batch Normalization)** [Li et al., 2016] is based on the observation that label-related knowledge "
              "lives mainly in the network weights, while domain-related knowledge lives largely in the statistics of the "
              "batch normalization layers. AdaBN replaces the source mean and variance in every BN layer with the mean and "
              "variance computed on target data. No weights are changed, no labels are used and no gradient step is taken, so "
              "the cost is a single forward pass over target data. It only helps networks that contain BN layers.")
    h3(doc, "2.2.5 Pixel-level and data-level methods")
    para(doc, "Instead of aligning features, these methods change the images. **CyCADA** [Hoffman et al., 2018] translates source "
              "images into the style of the target domain with cycle-consistent image-to-image translation, adds a semantic "
              "consistency loss so that content is preserved, and combines this with feature-level adaptation. The translated, "
              "labeled images are used to train the task model. **Data augmentation** (random colour changes, blur, noise, "
              "crops) enlarges the range of appearances seen in training and makes the model less dependent on any single one. "
              "It needs no target data but only helps against variations that the augmentation anticipates.")
    h3(doc, "2.2.6 Beyond adaptation: domain generalization and test-time adaptation")
    bullets(doc, ["**Domain generalization (DG)** assumes that no target data are available at training time. The model is "
                  "trained on several source domains and is expected to work on unseen domains [Zhou et al., 2023]. A large "
                  "benchmark study found that plain empirical risk minimization, when tuned carefully, is competitive with "
                  "specialised DG methods [Gulrajani and Lopez-Paz, 2021].",
                  "**TENT (test-time entropy minimization)** [Wang et al., 2021] adapts the model while it is being tested. For "
                  "each batch of unlabeled test data it uses test-batch BN statistics and updates only the BN scale and shift "
                  "parameters to reduce the entropy of the predictions. It needs neither source data nor labels at test time."])

    h3(doc, "2.2.7 Comparison of methods")
    para(doc, "Table 1 compares the methods on the properties that matter for choosing one in practice. Entries describe "
              "general tendencies reported in the literature and are qualitative.")
    rows = [
        ["Fine-tuning (supervised DA)", "Yes, a few", "Yes (labeled)", "Low", "Low", "Overfits the small target set; forgets source knowledge"],
        ["DAN / MK-MMD", "No", "Yes (unlabeled)", "Medium (kernel terms grow with batch size)", "Medium", "Sensitive to kernel choice; aligns overall distributions, not classes"],
        ["Deep CORAL", "No", "Yes (unlabeled)", "Low to medium", "Low", "Matches only second-order statistics; weak under large non-linear shift"],
        ["DANN", "No", "Yes (unlabeled)", "Medium (extra domain head, joint training)", "Medium", "Unstable adversarial training; sensitive to the lambda schedule and learning rate; can mix classes"],
        ["ADDA", "No", "Yes (unlabeled)", "Medium to high (two stages, second encoder)", "High", "Unstable GAN-style training; depends on a good source encoder"],
        ["AdaBN", "No", "Yes (unlabeled, statistics only)", "Very low (one forward pass)", "Very low", "Fixes only shift that BN statistics can capture; needs BN layers and enough target samples"],
        ["Pixel-level (CyCADA)", "No", "Yes (unlabeled images)", "High (GAN training)", "High", "Translation artifacts or content changes; GAN training is hard to stabilise"],
        ["Data augmentation", "No", "No", "Low", "Low", "Covers only the shifts that were anticipated"],
        ["Domain generalization", "No", "No (needs several source domains)", "Low to high", "Medium", "No guarantee on truly new domains; needs diverse sources"],
        ["TENT (test-time)", "No", "At test time only (unlabeled)", "Low (one update per test batch)", "Low", "Error accumulation and collapse with small batches or long streams; label shift"],
    ]
    tab(doc, "Comparison of domain shift methods",
        "Compares the surveyed methods on target-label need, target-data need during training, compute cost, implementation "
        "complexity and typical failure modes.",
        ["Method", "Needs target labels?", "Needs target data at training?", "Compute cost", "Implementation complexity", "Typical failure modes"],
        rows, [0.9, 0.6, 0.8, 0.9, 1.1, 1.6], size=8.5, expect=1, bold_first_col=True)

    h2(doc, "2.3 Research Gaps Identified")
    numbered(doc, ["**Toy benchmarks.** Many methods are evaluated on digits and office-object benchmarks. Gains on these do not "
                   "always carry over to medical images or driving scenes, where the shift is subtler and the cost of error "
                   "is higher.",
                   "**No target labels for model selection.** In unsupervised adaptation there are no target labels to choose "
                   "hyperparameters or to decide when to stop, yet many papers select settings using target accuracy.",
                   "**Unstable adversarial training.** Adversarial methods can oscillate or fail to converge, and results can "
                   "vary across random seeds.",
                   "**Label and concept shift.** Most feature-alignment methods assume covariate shift only. Under label shift, "
                   "forcing the feature distributions to match can hurt accuracy [Zhao et al., 2019].",
                   "**Few like-for-like comparisons.** Papers often use different backbones and training budgets, which makes "
                   "it hard to say how much of an improvement comes from the adaptation method itself.",
                   "**Reporting of simple baselines.** Cheap methods such as AdaBN are not always included as baselines even "
                   "though they can recover a large part of the loss."])

    h2(doc, "2.4 Research Objectives")
    numbered(doc, ["Quantify the effect of domain shift on a small CNN using MNIST as the source and MNIST-M as the target.",
                   "Use one shared backbone and the same training budget for all methods so that comparisons are fair.",
                   "Evaluate a training-free adaptation method (AdaBN) and an adversarial method (DANN) without target labels.",
                   "Measure each method by the share of the source-only to target-only accuracy gap that it closes.",
                   "Inspect the learned features with t-SNE to see how the two domains are arranged before and after "
                   "adversarial adaptation.",
                   "State the limitations of the experiment and the open challenges for real-world domain shift."])
