"""Report figures for the v2 ablation study and sensitivity study (report/figures/), in the style of the
other report figures.

    python experiments/plot_ablsens.py

Reads results/twohand_final/ablations_final.json, ablations_wilcoxon.json and sensitivity_final.json.
Writes report/figures/fig_ablation.png, fig_sensitivity.png and (with benchmarks_final.json) fig_benchmarks.png.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results" / "twohand_final"
OUT = ROOT / "report" / "figures"
BLUE, RED, GREY, INK = "#2a78d6", "#e8613c", "#9aa3ad", "#333333"

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#555555", "axes.grid": True, "grid.color": "#e6e6e6",
                     "axes.axisbelow": True})

ABL = {  # variant -> label (what is removed or replaced)
    "v2_abl_nolook": "− look-ahead (K = 0)",
    "v2_abl_balliauw": "Trained on balliauw15 rules",
    "v2_abl_nobonus": "− imitation bonus (λ = 0)",
    "v2_abl_notime": "− time-leap term",
    "v2_abl_nstep1": "− n-step (n = 1)",
    "v2_abl_nohandpos": "− hand-position features",
    "v2_abl_nodouble": "− Double DQN and dueling",
    "v2_abl_nooverlap": "− overlap tolerance",
    "v2_abl_nomask": "− action masking",
    "v2_abl_noelite": "− elite replay",
    "v2_abl_nocross": "− crossing term (2c, vs 2c)",
}


def ablation_figure():
    M = json.loads((RES / "ablations_final.json").read_text())["methods"]
    W = json.loads((RES / "ablations_wilcoxon.json").read_text())
    rows = []
    for k, label in ABL.items():
        ref = W[k]["ref"]
        dm = 100 * (M[k]["Mgen"]["mean"] - M[ref]["Mgen"]["mean"])
        dd = M[k]["d_rel_balliauw15"]["mean"] - M[ref]["d_rel_balliauw15"]["mean"]
        rows.append((label, dm, W[k]["Mgen"][1], dd, W[k]["d_rel_balliauw15"][1]))
    rows.sort(key=lambda r: r[1])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    y = range(len(rows))
    for ax, (vi, pi, title, good_low) in zip(axes, ((1, 2, "Δ Mgen vs full method (points) ↑", False),
                                                   (3, 4, "Δ d_rel vs full method ↓", True))):
        vals = [r[vi] for r in rows]
        cols = [(BLUE if ((v < 0) == good_low) else RED) if r[pi] is not None and r[pi] < 0.05 else GREY
                for v, r in zip(vals, rows)]
        ax.barh(list(y), vals, color=cols, height=0.65)
        ax.axvline(0, color=INK, lw=1)
        for yi, (v, r) in enumerate(zip(vals, rows)):
            ax.text(v + (0.03 if vi == 3 else 0.3) * (1 if v >= 0 else -1), yi,
                    f"{v:+.1f}" if vi == 1 else f"{v:+.3f}", va="center", ha="left" if v >= 0 else "right", fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", visible=False)
        lo, hi = min(vals), max(vals)
        pad = 0.35 * (hi - lo)
        ax.set_xlim(min(0, lo) - pad, max(0, hi) + pad)
    axes[0].set_yticks(list(y), [r[0] for r in rows])
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (RED, BLUE, GREY)]
    fig.legend(handles, ["significantly worse (Wilcoxon p < 0.05)", "significantly better", "not significant"],
               loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.suptitle("Ablations of v2 R3 (γ 0.5, λ 4): 30 test pieces, 2 seeds per variant vs 3 for the full method",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(OUT / "fig_ablation.png", dpi=150)
    print("wrote", OUT / "fig_ablation.png")


SENS = [  # (title, prefix, values in order, label of the centre value, x labels)
    ("Discount γ", "v2_sens_gamma_", ["0.3", None, "0.7", "0.9", "0.99"], "0.5"),
    ("Imitation weight λ", "v2_sens_lam_", ["0", "1", "2", None, "8"], "4"),
    ("Elite share of the batch", "v2_sens_elite_", ["0.1", "0.25", "0.5"], None),
    ("Learning rate", "v2_sens_lr_", ["0.0001", "0.0003", "0.001"], None),
    ("chord_tol / overlap_tol (s)", "v2_sens_tol_", ["0.02-0.03", "0.03-0.05", "0.05-0.08"], None),
    ("v_max percentile", "v2_sens_vmax_", ["90", "95", "99"], None),
]


def sensitivity_figure():
    M = json.loads((RES / "sensitivity_final.json").read_text())["methods"]
    base = M["v2_sens_base"]
    fig, axes = plt.subplots(2, 3, figsize=(11, 6))
    for n, (ax, (title, pre, vals, centre)) in enumerate(zip(axes.flat, SENS)):
        labels, mg, gap, is_base = [], [], [], []
        for v in vals:
            m = base if v is None else M[pre + v]
            labels.append(centre if v is None else v.replace("-", " / "))
            mg.append(100 * m["Mgen"]["mean"])
            gap.append(m["gap"]["mean"])
            is_base.append(v is None or m is base or m["Mgen"]["mean"] == base["Mgen"]["mean"])
        x = range(len(labels))
        ax.plot(list(x), mg, "-o", color=BLUE, lw=2, label="Mgen (%)")
        for xi, (g, b) in enumerate(zip(mg, is_base)):
            if b:
                ax.plot(xi, g, "o", ms=10, mfc="none", mec=INK, mew=1.2)
        ax.set_xticks(list(x), labels)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(52, 66)
        if n % 3 == 0:
            ax.set_ylabel("validation Mgen (%) ↑", color=BLUE, fontsize=9)
        ax2 = ax.twinx()
        ax2.plot(list(x), gap, "--s", color=RED, lw=1.5, ms=4, label="gap to optimum")
        ax2.set_ylim(0.15, 0.6)
        ax2.grid(False)
        ax2.spines["right"].set_visible(True)
        if n % 3 == 2:
            ax2.set_ylabel("gap to optimum (lower is better)", color=RED, fontsize=9)
        else:
            ax2.set_yticklabels([])
    h1 = plt.Line2D([], [], color=BLUE, marker="o", lw=2, label="validation Mgen (%) ↑")
    h2 = plt.Line2D([], [], color=RED, marker="s", ls="--", label="validation gap to optimum ↓")
    h3 = plt.Line2D([], [], color=INK, marker="o", ms=9, mfc="none", ls="none", label="final setting (γ 0.5, λ 4)")
    fig.legend(handles=[h1, h2, h3], loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.suptitle("Sensitivity of v2 R3: one setting changed at a time, 1 seed, 500k steps, validation pieces",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(OUT / "fig_sensitivity.png", dpi=150)
    print("wrote", OUT / "fig_sensitivity.png")


def benchmark_figure():
    M = json.loads((RES / "benchmarks_final.json").read_text())["methods"]
    rows = [("Tabular Q-learning\n(per piece)", "v2_qlearn"), ("MaskablePPO", "v2_ppo"),
            ("DQN (plain)", "v2_dqn"), ("Ours: masked Double DQN\n+ dueling + n-step + elite (R3)", "v2_r3")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    y = range(len(rows))
    specs = (("Mgen", 100, "Test Mgen (%) ↑", "{:.1f}"), ("d_rel_balliauw15", 1, "d_rel ↓", "{:.2f}"),
             ("gap", 1, "Gap to the reward optimum ↓", "{:.2f}"))
    for ax, (key, scale, title, fmt) in zip(axes, specs):
        vals = [scale * M[k][key]["mean"] for _, k in rows]
        errs = [scale * M[k][key].get("std", 0.0) for _, k in rows]
        cols = [BLUE if k == "v2_r3" else GREY for _, k in rows]
        ax.barh(list(y), vals, xerr=errs, color=cols, height=0.6, error_kw=dict(ecolor=INK, lw=1, capsize=3))
        for yi, v in enumerate(vals):
            ax.text(v, yi + 0.36, fmt.format(v), ha="center", fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", visible=False)
    axes[0].set_xlim(40, 66)
    axes[0].set_yticks(list(y), [r[0] for r in rows])
    fig.suptitle("RL benchmarks on the v2 setup (γ 0.5, λ 4): 30 test pieces, mean ± std over 3 seeds", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "fig_benchmarks.png", dpi=150)
    print("wrote", OUT / "fig_benchmarks.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ablation_figure()
    sensitivity_figure()
    if (RES / "benchmarks_final.json").exists():
        benchmark_figure()
