import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--results", default="results")
parser.add_argument("--out", default="docs/figures")
args = parser.parse_args()

TRAINED, ZERO_SHOT, BASELINE = "#257de0", "#f47230", "#8a8a8a"
TEXT, GRID = "#191919", "#e5e5e5"
GROUP = {"LSTM": TRAINED, "GRU": TRAINED, "TiRex-2": ZERO_SHOT, "Toto": ZERO_SHOT,
         "Var": BASELINE, "Last-3": BASELINE, "IForest": BASELINE}
NAMES = {"Var": "Window variance", "IForest": "Isolation Forest", "Toto": "Toto 2.0"}

plt.rcParams.update({"font.size": 10, "text.color": TEXT, "axes.labelcolor": TEXT,
                     "xtick.color": TEXT, "ytick.color": TEXT, "axes.edgecolor": GRID,
                     "axes.spines.top": False, "axes.spines.right": False})

results = Path(args.results)
table = pd.concat([pd.read_csv(f, dtype={"server": str}) for f in sorted(results.glob("*.csv"))])
table["server"] = table["server"].str.zfill(3)
vus = table.groupby(["server", "method"])["VUS-PR"].mean().unstack()
methods = [m for m in ["LSTM", "GRU", "TiRex-2", "Toto", "Var", "Last-3", "IForest"] if m in vus]
vus = vus[methods]
labels = [NAMES.get(m, m) for m in methods]
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 4.5))
rng = np.random.default_rng(0)
for i, m in enumerate(methods):
    ax.boxplot(vus[m], positions=[i], widths=0.5, showfliers=False,
               medianprops={"color": GROUP[m], "linewidth": 2},
               boxprops={"color": GROUP[m]}, whiskerprops={"color": GROUP[m]},
               capprops={"color": GROUP[m]})
    ax.scatter(i + rng.uniform(-0.15, 0.15, len(vus)), vus[m], s=16, color=GROUP[m],
               edgecolor="white", linewidth=0.5, zorder=3)
ax.set_xticks(range(len(methods)), labels, rotation=20, ha="right")
ax.set_ylabel("VUS-PR (one dot = one server)")
ax.set_ylim(0, 1)
ax.yaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
for color, name in [(TRAINED, "trained per server"), (ZERO_SHOT, "zero-shot pretrained"),
                    (BASELINE, "baselines")]:
    ax.scatter([], [], color=color, label=name)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, borderaxespad=0)
ax.set_title("VUS-PR on 22 SMD servers", loc="left", pad=28)
fig.tight_layout()
fig.savefig(out / "vus_pr_by_method.png", dpi=200)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 9))
im = ax.imshow(vus.values, cmap="Blues", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(methods)), labels, rotation=30, ha="right")
ax.set_yticks(range(len(vus)), vus.index)
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
for r in range(vus.shape[0]):
    for c in range(vus.shape[1]):
        v = vus.values[r, c]
        ax.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=8,
                color="white" if v > 0.55 else TEXT)
fig.colorbar(im, ax=ax, fraction=0.04, label="VUS-PR")
ax.set_ylabel("Server")
ax.set_title("VUS-PR per server and method", loc="left")
fig.tight_layout()
fig.savefig(out / "vus_pr_heatmap.png", dpi=200)
plt.close(fig)

trained = vus[["LSTM", "GRU"]].max(axis=1)
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot([0, 1], [0, 1], color=BASELINE, linewidth=1, linestyle="--")
ax.text(0.02, 0.84, "above the line: zero-shot better", color=BASELINE, fontsize=9)
ax.text(0.98, 0.02, "below the line: trained better", ha="right", color=BASELINE, fontsize=9)
for m, color, marker in [("TiRex-2", "#257de0", "s"), ("Toto", "#f47230", "o")]:
    ax.scatter(trained, vus[m], s=48, color=color, marker=marker, edgecolor="white",
               linewidth=1, label=NAMES.get(m, m), zorder=3)
wins = vus.index[(vus["Toto"] > trained) | (vus["TiRex-2"] > trained)]
for s in wins:
    ax.annotate(s, (trained[s], vus.loc[s, ["Toto", "TiRex-2"]].max()), xytext=(4, 4),
                textcoords="offset points", fontsize=8)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel("VUS-PR, better of LSTM and GRU")
ax.set_ylabel("VUS-PR, zero-shot model")
ax.grid(True, color=GRID)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper left")
ax.set_title("Zero-shot vs. trained, one point per server", loc="left")
fig.tight_layout()
fig.savefig(out / "zero_shot_vs_trained.png", dpi=200)
plt.close(fig)

print(f"{len(vus)} servers, methods: {', '.join(methods)} -> {out}")
