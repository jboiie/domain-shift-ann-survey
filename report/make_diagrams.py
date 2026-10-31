import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def box(ax, x, y, w, h, text, fc="#e8eef7", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec="#333", lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x0, y0, x1, y1, text=None, color="#333"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color=color, lw=1.2))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.12, text, ha="center", fontsize=8, color=color)


def taxonomy(path):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    box(ax, 3.7, 4.5, 2.6, 0.6, "Handling domain shift", "#d9e2f3", 10)
    cols = [
        (0.1, "Supervised DA", ["Fine-tuning with a few\nlabeled target samples"]),
        (2.1, "Discrepancy-based", ["DAN (MK-MMD)", "Deep CORAL"]),
        (4.1, "Adversarial", ["DANN (gradient\nreversal)", "ADDA"]),
        (6.1, "Normalization / pixel", ["AdaBN", "CyCADA, data\naugmentation"]),
        (8.1, "Beyond adaptation", ["Domain\ngeneralization", "TENT (test-time\nadaptation)"]),
    ]
    for x, head, items in cols:
        box(ax, x, 3.1, 1.8, 0.7, head, "#fce5cd", 9)
        arrow(ax, 5, 4.5, x + 0.9, 3.8)
        for i, it in enumerate(items):
            box(ax, x + 0.05, 2.0 - i * 1.1, 1.7, 0.8, it, "#e2f0d9", 8.5)
            if i == 0:
                arrow(ax, x + 0.9, 3.1, x + 0.9, 2.8)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def architecture(path):
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    box(ax, 0.05, 1.8, 1.3, 0.8, "Input\n3x32x32", "#f2f2f2")
    box(ax, 1.75, 1.8, 2.7, 0.8, "Conv-BN-ReLU-Pool x3\n(32, 64, 128 channels)", "#d9e2f3")
    box(ax, 4.85, 1.8, 1.6, 0.8, "Linear 2048->128\n+ ReLU", "#d9e2f3")
    arrow(ax, 1.35, 2.2, 1.75, 2.2)
    arrow(ax, 4.45, 2.2, 4.85, 2.2)
    ax.text(5.65, 1.55, "128-d feature", ha="center", fontsize=8)
    box(ax, 7.4, 3.0, 2.3, 0.8, "Label classifier\nLinear 128->10", "#e2f0d9")
    box(ax, 7.4, 0.6, 2.3, 0.8, "Domain classifier\n128->64->1", "#fce5cd")
    box(ax, 6.7, 1.95, 0.5, 0.5, "GRL", "#f8cbad", 8)
    arrow(ax, 6.45, 2.4, 7.4, 3.4)
    arrow(ax, 6.45, 2.0, 6.7, 2.2)
    arrow(ax, 7.2, 2.2, 7.4, 1.0)
    ax.text(4.0, 3.9, "Source-only, target-only and AdaBN use the label classifier only.\nDANN adds the GRL and the domain classifier, used during training only.",
            fontsize=8.5, ha="center", va="center")
    ax.text(8.5, 2.15, "forward: identity\nbackward: -lambda x gradient", fontsize=7.5, ha="center", color="#a0360a")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    taxonomy("figures/taxonomy.png")
    architecture("figures/architecture.png")
