import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from datasets import load_dataset
from torchvision import datasets, transforms

DEV = "cpu"
N_TRAIN = 10000  # per-domain training subsample, keeps every method to a few minutes on CPU


def set_seed(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)


def _norm(x):
    # uint8 NxHxWx3 -> float NxCx32x32 in [-1, 1], the same range for both domains
    return (torch.from_numpy(x).permute(0, 3, 1, 2).float() / 255 - 0.5) / 0.5


def load_data(n_train=N_TRAIN, seed=0):
    # MNIST: grayscale 28x28 -> 3-channel 32x32 so one model handles both domains
    rs = np.random.RandomState(seed)
    mn = {}
    for split in ("train", "test"):
        ds = datasets.MNIST("data", train=(split == "train"), download=True)
        x = F.interpolate(ds.data[:, None].float(), size=32, mode="bilinear", align_corners=False)
        x = x.expand(-1, 3, -1, -1).numpy().transpose(0, 2, 3, 1).clip(0, 255).astype(np.uint8)
        mn[split] = (x, ds.targets.numpy())
    # MNIST-M: parquet from the Hugging Face hub, already 32x32 RGB
    hf = load_dataset("Mike0307/MNIST-M")
    mm = {}
    for split in ("train", "test"):
        x = np.stack([np.array(im.convert("RGB")) for im in hf[split]["image"]])
        mm[split] = (x, np.array(hf[split]["label"]))
    out = {}
    for name, d in (("mnist", mn), ("mnistm", mm)):
        for split in ("train", "test"):
            x, y = d[split]
            if split == "train":
                idx = rs.permutation(len(x))[:n_train]
                x, y = x[idx], y[idx]
            out[f"{name}_{split}"] = (_norm(x), torch.from_numpy(y).long())
    return out


def sample_grid(data, path, n=10):
    fig, ax = plt.subplots(2, n, figsize=(n * 1.1, 2.6))
    for r, (name, title) in enumerate((("mnist_train", "MNIST (source)"), ("mnistm_train", "MNIST-M (target)"))):
        x, y = data[name]
        for c in range(n):
            ax[r, c].imshow((x[c].permute(1, 2, 0) * 0.5 + 0.5).clamp(0, 1))
            ax[r, c].set_title(int(y[c]), fontsize=8)
            ax[r, c].axis("off")
        ax[r, 0].text(-0.15, 0.5, title, transform=ax[r, 0].transAxes, rotation=90, va="center", ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
