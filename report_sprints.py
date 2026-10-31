from build_report import *


def rows_results(keys):
    names = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
    return [[names[k], pm(k, "mnist"), pm(k, "mnistm"), f"{S[k]['gap_mean']:.1f} ± {S[k]['gap_std']:.1f}"] for k in keys]


def ch3(doc):
    chapter(doc, "CHAPTER 3", "SPRINT PLANNING AND EXECUTION METHODOLOGY")
    para(doc, "The practical work was organised in two sprints. Sprint I sets up the problem and the baselines. Sprint II "
              "adds the adaptation methods and compares them. All code is in one notebook (domain_shift.ipynb) with a small "
              "helper module (da.py), and every number in this report is read from the file results.json that the notebook writes.")
    sp = S["source_only"]
    drop = sp["mnist_mean"] - sp["mnistm_mean"]

    h2(doc, "3.1 Sprint I: Problem Setup and Baseline")
    h3(doc, "3.1.1 Objectives with User Stories of Sprint I")
    numbered(doc, ["Load MNIST (source) and MNIST-M (target) and bring both to the same input format.",
                   "Define one CNN backbone that is used unchanged by every method.",
                   "Train a source-only model and measure its accuracy on both domains to demonstrate domain shift.",
                   "Train a target-only model on labeled MNIST-M to obtain an upper bound."])
    para(doc, "User stories:")
    bullets(doc, ["As a reader, I want to see sample images from both domains so that I understand what changes between them.",
                  "As a researcher, I want one shared model definition so that differences in results come from the method and "
                  "not from the architecture.",
                  "As a researcher, I want a source-only baseline and a target-only ceiling so that I can express every "
                  "method as a share of the gap between them."])

    h3(doc, "3.1.2 Functional Document")
    numbered(doc, ["**Data loading.** MNIST is loaded with torchvision. MNIST-M is loaded from the Hugging Face dataset "
                   "“Mike0307/MNIST-M” (parquet files, PNG images).",
                   "**Preprocessing.** MNIST images are resized from 28x28 to 32x32 and copied to three channels. MNIST-M images "
                   "are already 32x32 RGB. Pixel values of both domains are scaled to the range [-1, 1].",
                   f"**Subsampling.** {CFG['n_train_per_domain']:,} training images are drawn at random from each domain with a fixed "
                   f"seed. Full test sets are used: {CFG['n_test_mnist']:,} MNIST and {CFG['n_test_mnistm']:,} MNIST-M images.",
                   "**Training.** Supervised training with cross-entropy loss, using SGD with momentum 0.9 and a learning rate annealed "
                   "from 0.01 as in Ganin et al. Source-only uses labeled MNIST. Target-only uses labeled MNIST-M.",
                   "**Evaluation.** Accuracy on the MNIST test set and on the MNIST-M test set for every model."])
    tab(doc, "Experimental setup",
        "Lists datasets, image format, training subsample, backbone, optimizer, epochs, batch size and seeds used in all experiments.",
        ["Item", "Setting"],
        [["Source domain", "MNIST (torchvision), 60,000 train / 10,000 test images"],
         ["Target domain", "MNIST-M (Hugging Face: Mike0307/MNIST-M), 59,001 train / 9,001 test images"],
         ["Input format", "3 x 32 x 32, values in [-1, 1]"],
         ["Training images used", f"{CFG['n_train_per_domain']:,} per domain (random subsample)"],
         ["Test images used", f"{CFG['n_test_mnist']:,} MNIST, {CFG['n_test_mnistm']:,} MNIST-M (full test sets)"],
         ["Backbone", "3 x (Conv 3x3, BatchNorm, ReLU, MaxPool) with 32, 64, 128 channels; Linear 2048 to 128; ReLU"],
         ["Label classifier", "Linear 128 to 10"],
         ["Optimizer", f"{CFG['optimizer']}, batch size {CFG['batch_size']}"],
         ["Epochs", f"{CFG['epochs']} for every method"],
         ["Random seeds", ", ".join(str(s) for s in CFG["seeds"]) + " (results are mean and standard deviation over seeds)"],
         ["Hardware", "CPU only"]],
        [1.7, 4.5], size=10, expect=2, bold_first_col=True)

    h3(doc, "3.1.3 Architecture Document")
    para(doc, "Every method uses the same network, shown in Figure 2. Three convolution blocks (convolution, batch "
              "normalization, ReLU, 2x2 max pooling) reduce the 32x32 input to a 4x4 map with 128 channels. A linear layer "
              "maps the flattened 2048 values to a 128-dimensional feature vector, and a linear classifier maps the feature to "
              "ten digit classes. Batch normalization layers are included on purpose, because AdaBN works by changing their "
              "statistics. The network is small so that every run finishes in minutes on a CPU.")
    fig(doc, "figures/architecture.png", "Shared CNN backbone and the additional DANN components",
        "Shows the shared feature extractor and label classifier, and the gradient reversal layer and domain classifier "
        "that are added for DANN only.", 6.3, expect=2)
    para(doc, "The two domains are shown in Figure 3. MNIST digits are white strokes on a black background. In MNIST-M the same "
              "digit shapes are blended with random patches from natural photographs, so the strokes take on the colours and "
              "textures of the background.")
    fig(doc, "figures/samples.png", "Sample images from MNIST (source) and MNIST-M (target)",
        "Shows ten training images from each domain with their labels. The digit shapes are the same; MNIST-M adds coloured "
        "natural-image backgrounds.", 6.3, expect=3)

    h3(doc, "3.1.4 Outcome of Objectives / Result Analysis of Sprint I")
    tab(doc, "Sprint I results: source-only and target-only models (mean ± standard deviation over 3 seeds)",
        "Reports test accuracy on MNIST and MNIST-M for the source-only baseline and the target-only upper bound.",
        ["Method", "MNIST accuracy (%)", "MNIST-M accuracy (%)"],
        [["Source-only (trained on MNIST)", pm("source_only", "mnist"), pm("source_only", "mnistm")],
         ["Target-only (trained on MNIST-M)", pm("target_only", "mnist"), pm("target_only", "mnistm")]],
        [2.6, 1.8, 1.8], size=10, expect=3)
    para(doc, f"The source-only model reaches {acc('source_only', 'mnist')}% on MNIST but only {acc('source_only', 'mnistm')}% on "
              f"MNIST-M, a drop of {drop:.1f} percentage points on a task with the same ten labels. Random guessing would give "
              f"about 10%, so the model is only slightly better than chance on the target domain. This is the domain shift "
              f"demonstration. The target-only model reaches {acc('target_only', 'mnistm')}% on MNIST-M, which shows that the "
              f"backbone is able to solve the target task when it has labeled target data. This value is the ceiling used "
              f"to compute the share of the gap closed by each method. The target-only model reaches "
              f"{acc('target_only', 'mnist')}% on clean MNIST, lower than the source-only model on its own domain, which shows "
              f"that the shift also hurts in the opposite direction, though less.")
    h3(doc, "3.1.5 Sprint Retrospective")
    bullets(doc, ["The source-only baseline and target-only ceiling gave a clear scale: a method that gets close to "
                  f"{acc('target_only', 'mnistm')}% on MNIST-M has closed the gap, and one that stays near "
                  f"{acc('source_only', 'mnistm')}% has not.",
                  "Using one backbone and one training budget for all methods keeps the comparison fair. The cost is that "
                  "the backbone is not tuned for any single method.",
                  f"Training on a {CFG['n_train_per_domain']:,}-image subsample keeps each run to about "
                  f"{S['source_only']['train_seconds_per_run']:.0f} seconds on a CPU, but the absolute accuracies would differ with "
                  "the full training sets.",
                  "The MNIST-M test split in the Hugging Face copy has 9,001 images, not the 9,000 often quoted. The report "
                  "uses the data as distributed."])

    h2(doc, "3.2 Sprint II: Adaptation Methods")
    h3(doc, "3.2.1 Objectives with User Stories of Sprint II")
    numbered(doc, ["Implement AdaBN on the source-only model using unlabeled MNIST-M data.",
                   "Implement DANN with a gradient reversal layer, a domain classifier and the lambda schedule of Ganin et al.",
                   "Compare AdaBN and DANN with the baselines using the share of the gap closed.",
                   "Inspect the learned features with t-SNE for the source-only model and for DANN."])
    para(doc, "User stories:")
    bullets(doc, ["As a practitioner, I want to know how much a free, training-free fix such as AdaBN recovers.",
                  "As a researcher, I want to see whether adversarial training with unlabeled target data improves on that.",
                  "As a reader, I want a picture that shows how the two domains are arranged in feature space."])

    h3(doc, "3.2.2 Functional Document")
    para(doc, "**AdaBN.**", keep_next=True)
    numbered(doc, ["Take the trained source-only model.",
                   "Reset the running mean and variance of every batch normalization layer.",
                   "Pass the unlabeled MNIST-M training images through the network in training mode, without gradient steps, "
                   "so that each layer accumulates the average mean and variance of the target data.",
                   "Switch to evaluation mode and test. No weight changes and no target labels are used."])
    para(doc, "**DANN.**", keep_next=True)
    numbered(doc, ["Each step takes a batch of labeled MNIST images and a batch of unlabeled MNIST-M images.",
                   "Both batches pass through the feature extractor.",
                   "The label classifier is trained with cross-entropy loss on the source features only.",
                   "The domain classifier receives source and target features through the gradient reversal layer and is trained "
                   "with binary cross-entropy to predict the domain (source 0, target 1).",
                   "The reversal layer sends the negated, scaled gradient to the feature extractor, so the feature extractor is "
                   "pushed to make the two domains indistinguishable while still supporting the label classifier."])
    para(doc, "The reversal strength follows the schedule of Ganin et al.: λ = 2 / (1 + exp(-10p)) - 1, where p goes from "
              "0 to 1 over training. It starts near 0, so the classifier first learns digits, and rises towards 1, so domain "
              "confusion is enforced progressively.")
    para(doc, "**t-SNE.** Features (the 128-dimensional output of the feature extractor) of 1,000 MNIST test images and 1,000 "
              "MNIST-M test images are embedded in two dimensions with t-SNE (perplexity 30, fixed random state) for the "
              "seed-0 source-only and DANN models.")

    h3(doc, "3.2.3 Architecture Document")
    para(doc, "AdaBN does not change the architecture. DANN adds two parts to the shared backbone (Figure 2): a gradient "
              "reversal layer (GRL) and a domain classifier made of two linear layers (128 to 64 to 1) with a ReLU. The GRL "
              "is an identity function in the forward pass and multiplies the gradient by -\u03bb in the backward pass. The total "
              "training loss is the sum of the label loss on source data and the domain loss on source and target data. "
              "All methods, DANN included, are trained with the recipe of Ganin et al.: SGD with momentum 0.9 and a learning rate "
              "0.01 / (1 + 10p)^0.75, where p is the fraction of training steps completed. Source and target images of a step "
              "are passed through the network as one concatenated batch, so batch normalization statistics during DANN training "
              "are computed over both domains.")

    h3(doc, "3.2.4 Outcome of Objectives / Result Analysis of Sprint II")
    tab(doc, "Sprint II results: adaptation methods (mean ± standard deviation over 3 seeds)",
        "Reports MNIST and MNIST-M accuracy and the share of the source-only to target-only gap closed for AdaBN and DANN.",
        ["Method", "MNIST accuracy (%)", "MNIST-M accuracy (%)", "Gap closed (%)"],
        rows_results(["adabn", "dann"]), [1.5, 1.6, 1.7, 1.4], size=10, expect=4)
    dn = S["dann"]
    para(doc, f"AdaBN raises MNIST-M accuracy from {acc('source_only', 'mnistm')}% to {acc('adabn', 'mnistm')}% and closes "
              f"{gap('adabn')}% of the gap, without any training. MNIST accuracy is the same as for the source-only model "
              f"({acc('adabn', 'mnist')}%), because MNIST images are scored with the source statistics. DANN reaches "
              f"{acc('dann', 'mnistm')}% on MNIST-M and closes {gap('dann')}% of the gap, while keeping {acc('dann', 'mnist')}% on "
              f"MNIST. DANN results vary more between seeds than AdaBN results (standard deviation of {dn['mnistm_std']:.1f} "
              f"against {S['adabn']['mnistm_std']:.1f} points on MNIST-M). In this experiment AdaBN closed more of the gap than "
              "DANN, in every seed.")
    para(doc, "Figure 4 shows the t-SNE embedding of the features. For the source-only model, MNIST features form ten compact "
              "clusters, one per digit, while MNIST-M features form one large, diffuse region that touches only a few of those "
              "clusters. For DANN, the ten MNIST clusters remain and the MNIST-M points form elongated bands that stay apart "
              "from them. The two domains are not merged in this run.")
    fig(doc, "figures/tsne.png", "t-SNE of 128-dimensional features: source-only model (left) and DANN (right)",
        "Shows 1,000 MNIST (blue) and 1,000 MNIST-M (red) test images embedded in 2-D for the seed-0 source-only and DANN models.",
        6.3, expect=4)
    h3(doc, "3.2.5 Sprint Retrospective")
    last = [l for l in R["logs"] if l.startswith("[dann] seed 0")][-1].split("domain_loss ")[1].split()[0]
    bullets(doc, [f"AdaBN was the cheapest method by a large margin: {S['adabn']['train_seconds_per_run']:.1f} seconds per run, "
                  f"against {S['dann']['train_seconds_per_run']:.0f} seconds for DANN training.",
                  f"The domain loss of DANN reached {last} in the last epoch of seed 0 (see the training log in the screenshots), "
                  "close to ln 2 = 0.693, the value of a domain classifier that cannot separate the domains in training batches. "
                  "Yet target accuracy improved only moderately and the t-SNE view still shows separate domains, so fooling the "
                  "domain classifier was not sufficient for aligning the classes.",
                  "The gap closed by DANN was " + ", ".join(f"{g:.1f}%" for g in R["gap_closed_per_seed"]["dann"])
                  + " for seeds 0, 1 and 2, and AdaBN closed more in every seed.",
                  "Next steps would be to train longer on the full datasets, tune the domain classifier, and treat source and "
                  "target batches separately in batch normalization. These were not done, because the aim was a fair comparison "
                  "with one recipe and one backbone on a CPU."])


def ch4(doc, figs):
    chapter(doc, "CHAPTER 4", "LIST OF FIGURES")
    for n, t, d in figs:
        h3(doc, f"{n}. {t}")
        para(doc, d)


def ch5(doc, tabs):
    chapter(doc, "CHAPTER 5", "LIST OF TABLES")
    for n, t, d in tabs:
        h3(doc, f"{n}. {t}")
        para(doc, d)


ABBR = [
    ("AdaBN", "Adaptive Batch Normalization, a method that replaces source batch normalization statistics with target statistics."),
    ("ADDA", "Adversarial Discriminative Domain Adaptation, an adversarial method with a separate target encoder."),
    ("ANN", "Artificial Neural Network, a model made of layers of connected units that learns from examples."),
    ("BCE", "Binary Cross-Entropy, the loss used by the domain classifier."),
    ("BN", "Batch Normalization, a layer that normalizes activations using batch mean and variance."),
    ("CNN", "Convolutional Neural Network, a network built from convolution layers, used for image data."),
    ("CORAL", "Correlation Alignment, a method that aligns feature covariances of two domains."),
    ("CPU", "Central Processing Unit, the hardware on which all experiments were run."),
    ("CyCADA", "Cycle-Consistent Adversarial Domain Adaptation, a pixel-level and feature-level adaptation method."),
    ("DA", "Domain Adaptation, the task of adapting a model trained on a source domain to a different target domain."),
    ("DAN", "Deep Adaptation Network, a discrepancy-based method using multi-kernel MMD."),
    ("DANN", "Domain-Adversarial Neural Network, an adversarial method that uses a gradient reversal layer."),
    ("DG", "Domain Generalization, training a model to work on unseen domains without target data."),
    ("GAN", "Generative Adversarial Network, a model trained with a generator and a discriminator."),
    ("GRL", "Gradient Reversal Layer, an identity layer in the forward pass that negates the gradient in the backward pass."),
    ("i.i.d.", "Independent and identically distributed, the standard assumption about training and test samples."),
    ("MK-MMD", "Multi-Kernel Maximum Mean Discrepancy, a distance between distributions using several kernels."),
    ("MMD", "Maximum Mean Discrepancy, a distance between the mean embeddings of two distributions."),
    ("MNIST", "Modified National Institute of Standards and Technology handwritten digit dataset, the source domain."),
    ("MNIST-M", "MNIST digits blended with natural-image backgrounds, the target domain."),
    ("ReLU", "Rectified Linear Unit, the activation function max(0, x)."),
    ("SDG", "Sustainable Development Goal, as defined by the United Nations."),
    ("SGD", "Stochastic Gradient Descent, used with momentum for all training runs."),
    ("TENT", "Test-time entropy minimization, a test-time adaptation method."),
    ("t-SNE", "t-distributed Stochastic Neighbor Embedding, a method for 2-D visualization of high-dimensional features."),
    ("UDA", "Unsupervised Domain Adaptation, adaptation using unlabeled target data."),
    ("USPS", "United States Postal Service handwritten digit dataset, a common second digit domain; not used in this project."),
]


def ch6(doc):
    chapter(doc, "CHAPTER 6", "ABBREVIATIONS")
    para(doc, "This chapter lists the abbreviations used in the report so that readers from different backgrounds can follow "
              "the terms in the survey, the method descriptions and the experiments.")
    h2(doc, "List of Abbreviations")
    numbered(doc, [f"**{a}**: {d}" for a, d in ABBR])
