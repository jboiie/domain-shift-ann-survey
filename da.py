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


class Net(nn.Module):
    # Shared backbone for every method: 3 conv blocks (BN is what AdaBN adapts) -> 128-d feature -> linear classifier
    def __init__(self):
        super().__init__()
        def block(i, o):
            return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(), nn.MaxPool2d(2))
        self.feat = nn.Sequential(block(3, 32), block(32, 64), block(64, 128), nn.Flatten(), nn.Linear(128 * 16, 128), nn.ReLU())
        self.clf = nn.Linear(128, 10)

    def forward(self, x):
        return self.clf(self.feat(x))


def batches(x, y, bs=128, shuffle=True):
    idx = torch.randperm(len(x)) if shuffle else torch.arange(len(x))
    for i in range(0, len(x), bs):
        j = idx[i:i + bs]
        yield x[j], y[j]


@torch.no_grad()
def accuracy(model, x, y):
    model.eval()
    return 100 * sum((model(xb).argmax(1) == yb).sum().item() for xb, yb in batches(x, y, 512, False)) / len(x)


def train_supervised(x, y, epochs, seed, log, tag):
    set_seed(seed)
    m = Net()
    opt = torch.optim.Adam(m.parameters(), 1e-3)
    for ep in range(epochs):
        m.train()
        tot = 0
        for xb, yb in batches(x, y):
            loss = F.cross_entropy(m(xb), yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item() * len(xb)
        log(f"[{tag}] seed {seed} epoch {ep + 1}/{epochs} loss {tot / len(x):.4f}")
    return m


@torch.no_grad()
def adabn(model, x_target):
    # Replace BN running statistics with target-domain statistics; no weights change, no labels used
    import copy
    m = copy.deepcopy(model)
    for mod in m.modules():
        if isinstance(mod, nn.BatchNorm2d):
            mod.reset_running_stats()
            mod.momentum = None  # cumulative average over all target batches
    m.train()
    for xb, _ in batches(x_target, torch.zeros(len(x_target)), 128, False):
        m(xb)
    return m.eval()


class GRL(torch.autograd.Function):
    # Identity in the forward pass; multiplies the gradient by -lambda in the backward pass
    @staticmethod
    def forward(ctx, x, lam):
        ctx.lam = lam
        return x.view_as(x)

    @staticmethod
    def backward(ctx, g):
        return -ctx.lam * g, None


def train_dann(xs, ys, xt, epochs, seed, log, tag="dann"):
    set_seed(seed)
    m = Net()
    dom = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 1))
    opt = torch.optim.Adam(list(m.parameters()) + list(dom.parameters()), 1e-3)
    steps = epochs * ((len(xs) + 127) // 128)
    k = 0
    for ep in range(epochs):
        m.train()
        tl = td = 0
        # source batches carry labels; target batches are unlabeled and only feed the domain loss
        for (xb, yb), (tb, _) in zip(batches(xs, ys), batches(xt, torch.zeros(len(xt)))):
            p = k / steps
            lam = 2 / (1 + np.exp(-10 * p)) - 1  # schedule from Ganin et al.
            k += 1
            n = min(len(xb), len(tb))
            xb, yb, tb = xb[:n], yb[:n], tb[:n]
            f = m.feat(torch.cat([xb, tb]))
            lc = F.cross_entropy(m.clf(f[:n]), yb)
            d = dom(GRL.apply(f, lam)).squeeze(1)
            dl = torch.cat([torch.zeros(n), torch.ones(n)])
            ld = F.binary_cross_entropy_with_logits(d, dl)
            opt.zero_grad()
            (lc + ld).backward()
            opt.step()
            tl += lc.item()
            td += ld.item()
        nb = steps // epochs
        log(f"[{tag}] seed {seed} epoch {ep + 1}/{epochs} label_loss {tl / nb:.4f} domain_loss {td / nb:.4f} lambda {lam:.3f}")
    return m


@torch.no_grad()
def features(model, x):
    model.eval()
    return torch.cat([model.feat(xb) for xb, _ in batches(x, torch.zeros(len(x)), 512, False)]).numpy()


def run_all(data, seeds=(0, 1, 2), epochs=20, log=print):
    # Every method shares the Net backbone and the same epoch budget
    import time
    xs, ys = data["mnist_train"]
    xm, ym = data["mnistm_train"]
    tests = {"mnist": data["mnist_test"], "mnistm": data["mnistm_test"]}
    names = ["source_only", "adabn", "dann", "target_only"]
    per = {n: {"mnist": [], "mnistm": []} for n in names}
    secs = {n: 0.0 for n in names}
    keep = {}
    for s in seeds:
        t = time.time(); src = train_supervised(xs, ys, epochs, s, log, "source_only"); secs["source_only"] += time.time() - t
        t = time.time(); ada = adabn(src, xm); secs["adabn"] += time.time() - t
        t = time.time(); dn = train_dann(xs, ys, xm, epochs, s, log); secs["dann"] += time.time() - t
        t = time.time(); tgt = train_supervised(xm, ym, epochs, s, log, "target_only"); secs["target_only"] += time.time() - t
        for n, m in zip(names, (src, ada, dn, tgt)):
            for d, (x, y) in tests.items():
                # AdaBN keeps two sets of BN statistics: source statistics for MNIST, target statistics for MNIST-M
                me = src if (n == "adabn" and d == "mnist") else m
                per[n][d].append(accuracy(me, x, y))
            log(f"seed {s} {n}: MNIST {per[n]['mnist'][-1]:.2f}  MNIST-M {per[n]['mnistm'][-1]:.2f}")
        if s == seeds[0]:
            keep = {"source_only": src, "dann": dn}
    gap = {n: [100 * (per[n]["mnistm"][i] - per["source_only"]["mnistm"][i]) /
               (per["target_only"]["mnistm"][i] - per["source_only"]["mnistm"][i]) for i in range(len(seeds))] for n in names}
    summ = {}
    for n in names:
        summ[n] = {"mnist_mean": float(np.mean(per[n]["mnist"])), "mnist_std": float(np.std(per[n]["mnist"])),
                   "mnistm_mean": float(np.mean(per[n]["mnistm"])), "mnistm_std": float(np.std(per[n]["mnistm"])),
                   "gap_mean": float(np.mean(gap[n])), "gap_std": float(np.std(gap[n])),
                   "train_seconds_per_run": secs[n] / len(seeds)}
    res = {"config": {"epochs": epochs, "seeds": list(seeds), "n_train_per_domain": len(xs), "batch_size": 128, "optimizer": "Adam lr 1e-3",
                      "n_test_mnist": len(tests["mnist"][0]), "n_test_mnistm": len(tests["mnistm"][0])},
           "per_seed": per, "gap_closed_per_seed": gap, "summary": summ}
    return res, keep


def bar_chart(summ, path):
    labels = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7, 4))
    for off, d, name in ((-0.2, "mnist", "MNIST (source test)"), (0.2, "mnistm", "MNIST-M (target test)")):
        v = [summ[k][d + "_mean"] for k in labels]
        e = [summ[k][d + "_std"] for k in labels]
        b = ax.bar(x + off, v, 0.4, yerr=e, capsize=3, label=name)
        for xi, vi in zip(x + off, v):
            ax.text(xi, vi + 2, f"{vi:.1f}", ha="center", fontsize=8)
    ax.set_xticks(x, labels.values())
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 125)
    ax.legend(loc="upper center", ncol=2)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.show()


def tsne_plot(models, data, path, n=1000):
    from sklearn.manifold import TSNE
    xs = data["mnist_test"][0][:n]
    xt = data["mnistm_test"][0][:n]
    fig, ax = plt.subplots(1, len(models), figsize=(5.5 * len(models), 5))
    for a, (title, m) in zip(ax, models.items()):
        f = np.concatenate([features(m, xs), features(m, xt)])
        z = TSNE(2, perplexity=30, random_state=0).fit_transform(f)
        a.scatter(*z[:n].T, s=6, c="tab:blue", label="MNIST (source)", alpha=0.6)
        a.scatter(*z[n:].T, s=6, c="tab:red", label="MNIST-M (target)", alpha=0.6)
        a.set_title(title)
        a.set_xticks([])
        a.set_yticks([])
        a.legend(loc="upper right", markerscale=2)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.show()


def log_image(lines, path, title):
    fig = plt.figure(figsize=(9, 0.22 * len(lines) + 0.8), facecolor="#1e1e1e")
    fig.text(0.02, 1 - 0.3 / fig.get_figheight(), title, color="#9cdcfe", family="monospace", fontsize=9, va="top")
    for i, l in enumerate(lines):
        fig.text(0.02, 1 - (0.75 + 0.22 * i) / fig.get_figheight(), l, color="#d4d4d4", family="monospace", fontsize=8, va="top")
    plt.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
