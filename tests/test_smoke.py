"""Smoke test: data audit plus one epoch of each method on a few hundred synthetic images.

Uses synthetic tensors in the same format as da.load_data, so it needs no download.
Only checks that everything runs and returns valid accuracies, not that it learns.
"""
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import da  # noqa: E402


def fake_split(n, color, seed):
    g = torch.Generator().manual_seed(seed)
    y = torch.randint(0, 10, (n,), generator=g)
    gray = torch.rand(n, 1, 32, 32, generator=g) * 2 - 1
    x = gray.expand(-1, 3, -1, -1).clone()
    if color:
        x = (x + 0.5 * (torch.rand(n, 3, 1, 1, generator=g) * 2 - 1)).clamp(-1, 1)
    return x, y


def fake_data(n_train=300, n_test=200):
    return {"mnist_train": fake_split(n_train, False, 0), "mnist_test": fake_split(n_test, False, 1),
            "mnistm_train": fake_split(n_train, True, 2), "mnistm_test": fake_split(n_test, True, 3)}


def test_methods_run_and_give_valid_accuracies():
    data = fake_data()
    da.audit(data)
    xs, ys = data["mnist_train"]
    xm, ym = data["mnistm_train"]
    quiet = lambda s: None
    src = da.train_supervised(xs, ys, 1, 0, quiet, "source_only")
    ada = da.adabn(src, xm)
    dann = da.train_dann(xs, ys, xm, 1, 0, quiet)
    for name, model in (("source_only", src), ("adabn", ada), ("dann", dann)):
        for domain in ("mnist", "mnistm"):
            x, y = data[f"{domain}_test"]
            acc = da.accuracy(model, x, y)
            assert 0 <= acc <= 100, (name, domain, acc)
