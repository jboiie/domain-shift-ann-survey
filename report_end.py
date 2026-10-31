import ast
import textwrap
from build_report import *


def _last_domain_loss():
    line = [l for l in R["logs"] if l.startswith("[dann] seed 0")][-1]
    return float(line.split("domain_loss ")[1].split()[0])


def ch7(doc):
    chapter(doc, "CHAPTER 7", "RESULTS AND DISCUSSIONS")
    names = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
    ps = R["per_seed"]
    h2(doc, "7.1 Project Outcomes (Performance Evaluation, Comparisons, Testing Results)")
    para(doc, f"All four settings use the same CNN backbone, the same training recipe and {CFG['epochs']} epochs, and were run with "
              f"{len(CFG['seeds'])} random seeds. Accuracy is measured on the full MNIST test set ({CFG['n_test_mnist']:,} images) and the "
              f"full MNIST-M test set ({CFG['n_test_mnistm']:,} images). The share of the gap closed is "
              "(method - source-only) / (target-only - source-only), computed on MNIST-M accuracy for each seed and then averaged.")
    para(doc, "Methodology notes. First, the inputs were audited before training: both domains reach the model as 3 x 32 x 32 "
              "float tensors in [-1, 1] with the same normalization (mean 0.5, standard deviation 0.5 per channel), the three "
              "channels of MNIST are identical copies of the grayscale image, and labels are integer class indices. The audit "
              "found nothing to change. Second, AdaBN is evaluated with two sets of batch normalization statistics: MNIST test "
              "images are scored with the original source statistics and MNIST-M test images with the statistics re-estimated on "
              "unlabeled MNIST-M training images. The weights are identical in both cases, so the MNIST accuracy of AdaBN equals "
              "that of the source-only model by construction. Third, every method is trained with the recipe of Ganin et al.: "
              "SGD with momentum 0.9 and a learning rate annealed as 0.01 / (1 + 10p)^0.75, where p runs from 0 to 1 over "
              "training. DANN uses the reversal coefficient λ = 2 / (1 + exp(-10p)) - 1. The recipe and the number of epochs "
              "were fixed before the reported run and applied identically to all methods. A first run with the Adam optimizer is "
              "not reported.")
    tab(doc, "Results summary (mean ± standard deviation over 3 seeds)",
        "Gives MNIST accuracy, MNIST-M accuracy and the share of the gap closed for source-only, AdaBN, DANN and target-only.",
        ["Method", "MNIST accuracy (%)", "MNIST-M accuracy (%)", "Gap closed (%)"],
        rows_results_all(), [1.5, 1.6, 1.7, 1.4], size=10, expect=5)
    fig(doc, "figures/results_bar.png", "Accuracy of each method on MNIST and MNIST-M (error bars: standard deviation over 3 seeds)",
        "Bar chart of the results summary table, with MNIST and MNIST-M accuracy for each method.", 5.6, expect=5)
    tab(doc, "MNIST-M accuracy (%) for each seed",
        "Lists the MNIST-M test accuracy of every method for each random seed, to show the run-to-run variation.",
        ["Method"] + [f"Seed {s}" for s in CFG["seeds"]],
        [[names[k]] + [f"{v:.2f}" for v in ps[k]["mnistm"]] for k in names], [1.8, 1.4, 1.4, 1.4], size=10, expect=6)
    tab(doc, "MNIST accuracy (%) for each seed",
        "Lists the MNIST test accuracy of every method for each random seed.",
        ["Method"] + [f"Seed {s}" for s in CFG["seeds"]],
        [[names[k]] + [f"{v:.2f}" for v in ps[k]["mnist"]] for k in names], [1.8, 1.4, 1.4, 1.4], size=10, expect=7)
    tab(doc, "Gap closed (%) for each seed",
        "Lists the share of the source-only to target-only gap on MNIST-M that AdaBN and DANN closed for each random seed.",
        ["Method"] + [f"Seed {s}" for s in CFG["seeds"]],
        [[names[k]] + [f"{v:.1f}" for v in R["gap_closed_per_seed"][k]] for k in ("adabn", "dann")], [1.8, 1.4, 1.4, 1.4], size=10, expect=8)
    tab(doc, "Average training time per run on CPU",
        "Gives the average time in seconds needed to train or adapt each method for one seed.",
        ["Method", "Time per run (s)"],
        [[names[k], f"{S[k]['train_seconds_per_run']:.1f}"] for k in names], [2.2, 2.2], size=10, expect=9)

    h2(doc, "7.2 Domain Shift")
    para(doc, f"The source-only model is almost perfect on MNIST ({acc('source_only', 'mnist')}%) and far lower on MNIST-M "
              f"({acc('source_only', 'mnistm')}%), where chance is 10%. High accuracy on the source test set therefore says "
              "nothing about accuracy on the target domain, which is the same point made by the hospital X-ray study: internal "
              "validation did not predict performance at other sites. The network likely relies on cues that are present in "
              "clean MNIST and changed in MNIST-M, such as the contrast between a bright stroke and a black background. This "
              "explanation is consistent with the results but was not tested separately.")
    para(doc, "For reference, Ganin and Lempitsky (2015) report 57.5% source-only accuracy and 98.9% target-only accuracy on "
              "MNIST to MNIST-M, with their own MNIST-M generation, network and training set sizes. The source-only accuracy "
              "here is lower, while the target-only accuracy is close. The source-only difference may come from the smaller "
              "network, the 10,000-image subsample or the copy of MNIST-M used, but this was not isolated by an experiment, "
              "and the absolute numbers in this report should not be compared directly with published ones.")

    h2(doc, "7.3 AdaBN")
    para(doc, f"AdaBN closed {S['adabn']['gap_mean']:.1f} ± {S['adabn']['gap_std']:.1f}% of the gap ({pm('adabn', 'mnistm')}% on "
              f"MNIST-M) with about {S['adabn']['train_seconds_per_run']:.1f} seconds of computation, and it improved on the "
              f"source-only model for every seed ({', '.join(f'{v:.1f}' for v in ps['adabn']['mnistm'])}% against "
              f"{', '.join(f'{v:.1f}' for v in ps['source_only']['mnistm'])}%). A likely reason is that the first layers of a "
              "CNN see the pixel statistics directly. MNIST-M images have different channel means and variances from MNIST "
              "images, so the source-estimated BN statistics push the activations of target images to the wrong range. "
              "Replacing them with target statistics puts the activations back into a range the weights were trained for. No "
              "label or weight update is needed, which suggests that part of the shift here is a change of overall intensity "
              "and contrast statistics that BN can absorb. This explanation was not tested separately. The remaining gap shows "
              "that statistics alone are not enough: the textured backgrounds of MNIST-M are not just a change of mean and "
              "variance.")
    para(doc, "AdaBN needs unlabeled target data at adaptation time and a way to know which domain an input comes from, because "
              "the model holds one set of statistics per domain. Its MNIST accuracy is unchanged only because MNIST images are "
              "still scored with the source statistics.")

    h2(doc, "7.4 DANN")
    para(doc, f"DANN reached {pm('dann', 'mnistm')}% on MNIST-M and closed {S['dann']['gap_mean']:.1f} ± {S['dann']['gap_std']:.1f}% "
              f"of the gap, while keeping MNIST accuracy at {pm('dann', 'mnist')}%. It improved on source-only in every seed "
              f"({', '.join(f'{v:.1f}' for v in ps['dann']['mnistm'])}%), but it closed less of the gap than AdaBN on average and "
              f"in every seed (AdaBN: {', '.join(f'{v:.1f}' for v in ps['adabn']['mnistm'])}%). DANN took "
              f"{S['dann']['train_seconds_per_run']:.0f} seconds per run against {S['adabn']['train_seconds_per_run']:.1f} seconds "
              "for AdaBN. Its improvement is therefore modest, and it varies between seeds more than that of AdaBN.")
    para(doc, "DANN needs no target labels because the only signal it takes from the target data is the domain label, which "
              "is known by construction (every image in the target batch is a target image). The classification loss uses "
              "source labels only. The target data influence the feature extractor through the reversed gradient of the domain "
              "loss.")
    para(doc, f"The training log (Screenshot 2) shows that the domain loss reached {_last_domain_loss():.3f} in the last epoch of "
              "seed 0, which is the value ln 2 = 0.693 expected when the domain classifier performs at chance on training batches. "
              "The adversarial game therefore ended in a state where the domain classifier could not separate the domains, yet "
              f"target accuracy was only {acc('dann', 'mnistm')}% and the t-SNE view (Figure 4) still shows the two domains apart. "
              "Fooling a domain classifier does not guarantee that the feature distributions are aligned class by class, and "
              "marginal feature alignment is known to have this limit [Zhao et al., 2019]. Other factors may also contribute: the "
              "network is small, the training set is a 10,000-image subsample, the domain classifier was not tuned, and the source "
              "and target images of a step share one batch normalization batch. None of these was isolated by an experiment. Ganin "
              "and Lempitsky (2015) report 81.5% for DANN on MNIST to MNIST-M with a different setup, and the accuracy here is "
              "lower.")

    h2(doc, "7.5 What the t-SNE Plot Shows")
    para(doc, "In Figure 4, the source-only model produces ten tight MNIST clusters, and the MNIST-M features form one large, "
              "diffuse region that touches only a few of those clusters. This matches the low target accuracy: target images "
              "are mostly not mapped near the class clusters. After DANN, the ten MNIST clusters remain, and the MNIST-M points "
              "form elongated bands that stay apart from all of them. The plot therefore does not show the domains merging, "
              f"which is consistent with the modest accuracy gain for seed 0 (MNIST-M accuracy {ps['dann']['mnistm'][0]:.1f}% for "
              f"DANN against {ps['source_only']['mnistm'][0]:.1f}% for source-only).")
    para(doc, "t-SNE is a qualitative tool. The plot is from one seed and 2,000 points, t-SNE distances are not meaningful "
              "beyond local neighbourhoods, and the absence of overlap in two dimensions does not by itself prove that the "
              "domains are separable in the full 128-dimensional space. The plot supports the accuracy numbers but does not "
              "replace them.")

    h2(doc, "7.6 What Worked and Why")
    bullets(doc, [f"**AdaBN** gave the best improvement per unit of effort ({gap('adabn')}% of the gap closed in about "
                  f"{S['adabn']['train_seconds_per_run']:.1f} seconds, without training), likely because part of the shift is "
                  "visible in layer statistics. It was better than DANN in every seed.",
                  f"**DANN** improved on source-only ({acc('dann', 'mnistm')}% against {acc('source_only', 'mnistm')}%) and kept source "
                  f"accuracy, using no target labels, but it closed only {gap('dann')}% of the gap and was less effective than AdaBN "
                  "in this setup.",
                  f"**Target labels** remain the most reliable fix: the target-only model reached {acc('target_only', 'mnistm')}%. "
                  "Domain adaptation methods are useful when such labels cannot be obtained."])

    h2(doc, "7.7 Limitations")
    bullets(doc, ["Digits are a toy benchmark. The shift from MNIST to MNIST-M is large but synthetic. Real shifts, for example "
                  "between hospitals, are subtler, mix covariate and label shift, and cannot be checked as easily.",
                  f"Only {len(CFG['seeds'])} seeds, a {CFG['n_train_per_domain']:,}-image subsample per domain and a small CNN were used. "
                  "Rankings of methods may change with a different backbone, budget or tuning.",
                  "DANN used the recipe of Ganin et al. but on a smaller network and dataset, and its domain classifier and "
                  "batch handling were not tuned. The comparison shows how the methods behave under identical conditions, "
                  "not their best achievable accuracy, and it is not a reproduction of the published DANN numbers.",
                  "The recipe and the number of epochs were fixed in advance and applied to all methods. A real unsupervised "
                  "setting has no target labels for model selection.",
                  "Only AdaBN and DANN were implemented. The other surveyed methods are discussed from the literature only."])


def rows_results_all():
    names = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
    return [[names[k], pm(k, "mnist"), pm(k, "mnistm"), f"{S[k]['gap_mean']:.1f} ± {S[k]['gap_std']:.1f}"] for k in names]


def ch8(doc):
    chapter(doc, "CHAPTER 8", "CONCLUSION AND FUTURE ENHANCEMENT")
    para(doc, "This report surveyed domain shift in neural networks and the main methods used to reduce it, and supported the "
              "survey with a controlled experiment. The hospital X-ray study of Zech et al. shows that the problem is real: "
              "networks that were accurate at the hospitals they were trained on were less accurate elsewhere, and could "
              "identify the hospital from the image. The MNIST to MNIST-M experiment reproduces the same effect in a form "
              "that can be measured.")
    para(doc, "The main findings are:")
    bullets(doc, [f"A CNN trained on MNIST scored {acc('source_only', 'mnist')}% on MNIST and {acc('source_only', 'mnistm')}% on MNIST-M, while a "
                  f"CNN trained on labeled MNIST-M scored {acc('target_only', 'mnistm')}% on MNIST-M. High source accuracy did not "
                  "predict target accuracy.",
                  f"AdaBN, which only replaces batch normalization statistics, closed {gap('adabn')}% of the gap in about one second "
                  f"without training, and left source accuracy unchanged when MNIST was scored with source statistics.",
                  f"DANN closed {gap('dann')}% of the gap on average, kept source accuracy, and was less effective than AdaBN in "
                  "every seed. Its domain classifier ended at chance level, but the t-SNE view still shows the two domains apart.",
                  "Methods differ in what they require. AdaBN and TENT need little compute, DANN and ADDA need adversarial "
                  "training, CyCADA needs image translation, and fine-tuning needs target labels."])
    para(doc, "The study met its objectives: it defined the types of shift, linked the vulnerability of networks to "
              "generalization, inductive bias and data selection, compared the method families, and measured two of them "
              "under identical conditions. It also has limits. The benchmark is a toy one, the training budget is small, DANN "
              "was only moderately effective in this setup, and the other surveyed methods were not run.")
    h2(doc, "Future Enhancement")
    bullets(doc, ["Train DANN longer on the full datasets and tune the domain classifier and batch handling, then report how "
                  "much of the gap to published results is due to the setup.",
                  "Add the other surveyed methods on the same backbone (Deep CORAL, DAN, TENT) for a wider like-for-like comparison.",
                  "Add USPS as a second target domain, and a harder benchmark with natural images.",
                  "Test on a real medical-imaging shift, for example chest X-rays from two hospitals, where label shift and "
                  "concept shift also occur.",
                  "Study model selection without target labels, which is the unresolved practical problem of unsupervised "
                  "domain adaptation.",
                  "Detect shift before accuracy is lost, for example by monitoring feature statistics at deployment."])


REFS = [
    ("Foundation Papers", "Theory, surveys and background", [
        ("Ben-David, S., Blitzer, J., Crammer, K., Kulesza, A., Pereira, F., & Vaughan, J. W. (2010). A theory of learning from "
         "different domains. Machine Learning, 79(1-2), 151-175. doi:10.1007/s10994-009-5152-4.",
         "Gives the bound on target error in terms of source error and domain divergence."),
        ("Quiñonero-Candela, J., Sugiyama, M., Schwaighofer, A., & Lawrence, N. D. (Eds.). (2009). Dataset Shift in Machine "
         "Learning. MIT Press.", "Standard reference on dataset shift and its types."),
        ("Shimodaira, H. (2000). Improving predictive inference under covariate shift by weighting the log-likelihood function. "
         "Journal of Statistical Planning and Inference, 90(2), 227-244.", "Early formal treatment of covariate shift."),
        ("Pan, S. J., & Yang, Q. (2010). A survey on transfer learning. IEEE Transactions on Knowledge and Data Engineering, "
         "22(10), 1345-1359.", "Places domain adaptation within transfer learning."),
        ("Wang, M., & Deng, W. (2018). Deep visual domain adaptation: A survey. Neurocomputing, 312, 135-153. "
         "doi:10.1016/j.neucom.2018.05.083.", "Survey of deep domain adaptation methods for visual recognition."),
        ("Zhou, K., Liu, Z., Qiao, Y., Xiang, T., & Loy, C. C. (2023). Domain generalization: A survey. IEEE Transactions on "
         "Pattern Analysis and Machine Intelligence, 45(4), 4396-4415. doi:10.1109/TPAMI.2022.3195549.",
         "Survey of domain generalization methods."),
        ("LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). Gradient-based learning applied to document recognition. "
         "Proceedings of the IEEE, 86(11), 2278-2324.", "Source of the MNIST dataset."),
        ("Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training by reducing internal "
         "covariate shift. Proceedings of the 32nd International Conference on Machine Learning (ICML), PMLR 37, 448-456.",
         "Defines the batch normalization layer that AdaBN modifies."),
    ]),
    ("Domain Adaptation Methods", "Methods covered in the taxonomy", [
        ("Long, M., Cao, Y., Wang, J., & Jordan, M. I. (2015). Learning transferable features with deep adaptation networks. "
         "Proceedings of the 32nd International Conference on Machine Learning (ICML), PMLR 37, 97-105.",
         "DAN: multi-kernel MMD on task-specific layers."),
        ("Sun, B., & Saenko, K. (2016). Deep CORAL: Correlation alignment for deep domain adaptation. In Computer Vision - ECCV "
         "2016 Workshops, LNCS 9915, 443-450.", "Aligns feature covariances of source and target."),
        ("Ganin, Y., & Lempitsky, V. (2015). Unsupervised domain adaptation by backpropagation. Proceedings of the 32nd "
         "International Conference on Machine Learning (ICML), PMLR 37, 1180-1189.",
         "Introduces the gradient reversal layer and the MNIST-M dataset; reports 57.5% source-only and 81.5% DANN accuracy on MNIST to MNIST-M."),
        ("Ganin, Y., Ustinova, E., Ajakan, H., Germain, P., Larochelle, H., Laviolette, F., Marchand, M., & Lempitsky, V. "
         "(2016). Domain-adversarial training of neural networks. Journal of Machine Learning Research, 17(59), 1-35.",
         "Full DANN paper with the lambda schedule and theory."),
        ("Tzeng, E., Hoffman, J., Saenko, K., & Darrell, T. (2017). Adversarial discriminative domain adaptation. Proceedings of "
         "the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 7167-7176.",
         "ADDA: untied target encoder trained against a discriminator."),
        ("Li, Y., Wang, N., Shi, J., Liu, J., & Hou, X. (2016). Revisiting batch normalization for practical domain adaptation. "
         "arXiv:1603.04779.", "AdaBN: replaces BN statistics with target statistics."),
        ("Hoffman, J., Tzeng, E., Park, T., Zhu, J.-Y., Isola, P., Saenko, K., Efros, A., & Darrell, T. (2018). CyCADA: "
         "Cycle-consistent adversarial domain adaptation. Proceedings of the 35th International Conference on Machine "
         "Learning (ICML), PMLR 80, 1989-1998.", "Pixel-level and feature-level adaptation."),
        ("Wang, D., Shelhamer, E., Liu, S., Olshausen, B., & Darrell, T. (2021). Tent: Fully test-time adaptation by entropy "
         "minimization. International Conference on Learning Representations (ICLR).", "TENT: test-time adaptation."),
        ("Gulrajani, I., & Lopez-Paz, D. (2021). In search of lost domain generalization. International Conference on Learning "
         "Representations (ICLR).", "Benchmark study of domain generalization methods."),
        ("Zhao, H., Tachet des Combes, R., Zhang, K., & Gordon, G. (2019). On learning invariant representations for domain "
         "adaptation. Proceedings of the 36th International Conference on Machine Learning (ICML), PMLR 97, 7523-7532.",
         "Shows the limits of feature-distribution alignment under label shift."),
    ]),
    ("Real-World Domain Shift Studies", "Evidence of domain shift outside benchmarks", [
        ("Zech, J. R., Badgeley, M. A., Liu, M., Costa, A. B., Titano, J. J., & Oermann, E. K. (2018). Variable generalization "
         "performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study. PLOS "
         "Medicine, 15(11), e1002683. doi:10.1371/journal.pmed.1002683.",
         "Pneumonia CNNs were less accurate at outside hospitals in 3 of 5 comparisons and could identify the hospital system."),
        ("Sakaridis, C., Dai, D., & Van Gool, L. (2018). Semantic foggy scene understanding with synthetic data. International "
         "Journal of Computer Vision, 126(9), 973-992. doi:10.1007/s11263-018-1072-8.",
         "Scene understanding in fog, with synthetic fog added to clear-weather images."),
    ]),
    ("Tools and Frameworks", "Software and datasets used in the experiment", [
        ("Paszke, A., et al. (2019). PyTorch: An imperative style, high-performance deep learning library. Advances in Neural "
         "Information Processing Systems 32 (NeurIPS).", "Framework used for the models and training."),
        ("Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, "
         "2825-2830.", "Provides the t-SNE implementation."),
        ("van der Maaten, L., & Hinton, G. (2008). Visualizing data using t-SNE. Journal of Machine Learning Research, 9, "
         "2579-2605.", "The t-SNE method."),
        ("Lhoest, Q., et al. (2021). Datasets: A community library for natural language processing. Proceedings of the 2021 "
         "Conference on Empirical Methods in Natural Language Processing: System Demonstrations, 175-184.",
         "Hugging Face datasets library used to load MNIST-M."),
        ("Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90-95.",
         "Plotting library."),
        ("Harris, C. R., et al. (2020). Array programming with NumPy. Nature, 585, 357-362.", "Numerical library."),
        ("Mike0307. MNIST-M [Dataset]. Hugging Face Hub, https://huggingface.co/datasets/Mike0307/MNIST-M.",
         "Copy of MNIST-M used as the target domain."),
    ]),
]


def ch9(doc):
    chapter(doc, "CHAPTER 9", "REFERENCES")
    for i, (head, sub, items) in enumerate(REFS, 1):
        h2(doc, f"{i}. {head}")
        para(doc, sub, italic=True, keep_next=True)
        for ref, key in items:
            p = para(doc, "•\t" + ref, after=0)
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.keep_with_next = True
            q = para(doc, f"*Key:* {key}", after=8)
            q.paragraph_format.left_indent = Inches(0.4)
    para(doc, "In-text citations of the form [Author, Year] refer to this list.", italic=True)


def _src(name, tree, lines):
    for node in tree.body:
        if getattr(node, "name", None) == name:
            start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
            return "\n".join(lines[start - 1:node.end_lineno])
    raise KeyError(name)


def wrap_code(txt, width=82):
    out = []
    for ln in txt.split("\n"):
        ind = len(ln) - len(ln.lstrip())
        if len(ln) > width and not ln.lstrip().startswith("#") and "  # " in ln:
            code_part, comment = ln.split("  # ", 1)
            out.append(" " * ind + "# " + comment)  # trailing comment moves to its own line above the code
            ln = code_part
        if len(ln) <= width:
            out.append(ln)
        elif ln.lstrip().startswith("#"):
            out += textwrap.wrap(ln, width, subsequent_indent=" " * ind + "# ", break_long_words=False)
        else:
            out += textwrap.wrap(ln, width, subsequent_indent=" " * (ind + 4), break_long_words=False, replace_whitespace=False)
    return "\n".join(out)


def ch10(doc):
    chapter(doc, "CHAPTER 10", "APPENDIX")
    src = open("da.py", encoding="utf8").read()
    tree, lines = ast.parse(src), src.split("\n")
    para(doc, "The listings below are copied from da.py, the helper module used by the notebook domain_shift.ipynb. "
              "Long lines are wrapped for printing.")
    for title, names in [("1. Data loading and preprocessing (MNIST and MNIST-M)", ["load_data"]),
                         ("2. Shared CNN backbone and supervised training (source-only and target-only)", ["Net", "make_opt", "set_lr", "train_supervised"]),
                         ("3. AdaBN", ["adabn"]),
                         ("4. DANN: gradient reversal layer and training loop", ["GRL", "train_dann"])]:
        h2(doc, title)
        para(doc, "Code snippet:", keep_next=True)
        code(doc, "\n\n".join(wrap_code(_src(n, tree, lines)) for n in names))


SHOTS = [
    ("figures/log_supervised.png", "Training log of the source-only and target-only models (seed 0)", 6.0),
    ("figures/log_dann.png", "Training log of DANN (seed 0): label loss, domain loss and lambda per epoch", 6.0),
    ("figures/log_eval.png", "Test accuracy of every method for each seed, as printed by the notebook", 6.0),
    ("figures/samples.png", "Sample images from MNIST and MNIST-M (Figure 3)", 6.0),
    ("figures/results_bar.png", "Results bar chart (Figure 5)", 5.4),
    ("figures/tsne.png", "t-SNE of source-only and DANN features (Figure 4)", 6.2),
]


def screenshots(doc):
    chapter(doc, "SCREENSHOTS AND VISUALIZATIONS", None)
    para(doc, "Training logs are rendered from the text printed by the notebook. Plots are the images saved by the notebook.")
    for i, (p, c, w) in enumerate(SHOTS, 1):
        figure(doc, p, f"Screenshot {i}: {c}", w)
