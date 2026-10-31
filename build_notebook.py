import nbformat as nbf

cells = [
"pip install torch torchvision numpy pandas matplotlib scikit-learn datasets pyarrow",
"""import json
import pandas as pd
import da""",
"""# Load MNIST (source) and MNIST-M (target), 3-channel 32x32, 10k-image training subsample per domain
da.set_seed(0)
data = da.load_data()
for k, (x, y) in data.items():
    print(k, tuple(x.shape))""",
"""# Sample images from both domains
da.sample_grid(data, "figures/samples.png")""",
"""# Source-only, AdaBN, DANN and target-only on 3 seeds, 20 epochs each
logs = []
def log(s):
    logs.append(s)
    print(s)
res, models = da.run_all(data, seeds=(0, 1, 2), epochs=20, log=log)
res["logs"] = logs""",
"""# Results table
names = {"source_only": "Source-only", "adabn": "AdaBN", "dann": "DANN", "target_only": "Target-only"}
rows = [{"Method": names[k], "MNIST acc (%)": f"{v['mnist_mean']:.2f} +/- {v['mnist_std']:.2f}",
         "MNIST-M acc (%)": f"{v['mnistm_mean']:.2f} +/- {v['mnistm_std']:.2f}",
         "% gap closed": f"{v['gap_mean']:.1f} +/- {v['gap_std']:.1f}"} for k, v in res["summary"].items()]
pd.DataFrame(rows)""",
"""# Save every number the report uses
with open("results.json", "w") as f:
    json.dump(res, f, indent=2)""",
"""# Bar chart of the results table
da.bar_chart(res["summary"], "figures/results_bar.png")""",
"""# t-SNE of penultimate features, source-only vs DANN (seed 0 models)
da.tsne_plot({"Source-only": models["source_only"], "DANN": models["dann"]}, data, "figures/tsne.png")""",
"""# Render the seed-0 training logs as images
s0 = [l for l in logs if "seed 0" in l]
da.log_image([l for l in s0 if l.startswith("[source_only]")] + [l for l in s0 if l.startswith("[target_only]")], "figures/log_supervised.png", "Source-only and target-only training (seed 0)")
da.log_image([l for l in s0 if l.startswith("[dann]")], "figures/log_dann.png", "DANN training (seed 0)")
da.log_image([l for l in logs if l.startswith("seed ")], "figures/log_eval.png", "Test accuracy per seed")""",
]
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell(c) for c in cells]
nb.metadata["kernelspec"] = {"display_name": "Python 3", "name": "python3", "language": "python"}
nbf.write(nb, "domain_shift.ipynb")
