"""Redo the ablations (E10) and the sensitivity study (E12) on the final v2 setup.

The originals (runs/abl_*, runs/sens_*) were trained with the first Part C recipe (γ = 0.99, early
stopping). Here every variant is the v2 R3 configuration (γ 0.5, λ 4, elite, no early stopping)
with one thing changed, exactly as round3() in run_twohand.py did for the old setup:

    python experiments/run_v2_ablsens.py --jobs 4

Ablations: 2 seeds, 1M steps (abl_nocross: assign mode from v2_r3, 1.5M, compare with v2_2c).
Sensitivity: 1 seed, 500k steps, around γ 0.5 and λ 4.
Runs go to runs/v2_abl_*_s<seed> and runs/v2_sens_*_s0; a run with done.json is skipped.
Afterwards both are evaluated into results/twohand_final/{ablations,sensitivity}_final.json.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from run_v2 import GIVEN, PIG, PY, ROOT, job, run

GAMMA, LAM = "0.5", "4"
RECIPE = ["--gamma", GAMMA]
FULL = GIVEN + ["--lam", LAM, "--elite", "1"]
RES = ROOT / "results" / "twohand_final"


def ablations(seeds):
    variants = {
        "abl_nobonus": GIVEN + ["--lam", "0", "--elite", "1"],
        "abl_noelite": GIVEN + ["--lam", LAM],
        "abl_nomask": FULL + ["--no-mask"],
        "abl_notime": FULL + ["--w-time", "0"],
        "abl_nolook": FULL + ["--lookahead", "0"],
        "abl_nohandpos": FULL + ["--no-hand-pos"],
        "abl_nstep1": FULL + ["--n-step", "1"],
        "abl_nodouble": FULL + ["--no-double", "--no-dueling"],
        "abl_reduce": FULL + ["--chords", "reduce"],
        "abl_nooverlap": FULL + ["--overlap-tol", "0"],
        "abl_balliauw": ["--mode", "given", "--cost", "balliauw15", "--lam", LAM, "--elite", "1"],
    }
    J = [job(n, s, a, RECIPE, 1_000_000) for s in seeds for n, a in variants.items()]
    for s in seeds:  # crossing term exists only with hand assignment: 2c without it, against v2_2c
        init = ROOT / "runs" / f"v2_r3_s{s}" / "best.pt"
        J.append(job("abl_nocross", s, ["--mode", "assign", "--cost", "parncutt12", "--lam", LAM, "--elite", "1",
                                        "--w-cross", "0", "--init", str(init), "--curriculum"], RECIPE, 1_500_000))
    return J


def sensitivity():
    sens = {f"sens_lam_{l}": (GIVEN + ["--lam", l, "--elite", "1"], RECIPE) for l in ("0", "1", "2", "8")}
    sens["sens_base"] = (FULL, RECIPE)  # the centre point (γ 0.5, λ 4) at the same 500k budget
    sens.update({f"sens_gamma_{g}": (FULL, ["--gamma", g]) for g in ("0.3", "0.7", "0.9", "0.99")})
    sens.update({f"sens_elite_{e}": (GIVEN + ["--lam", LAM, "--elite", e], RECIPE) for e in ("0.1", "0.25", "0.5")})
    sens.update({f"sens_lr_{lr}": (FULL + ["--lr", lr], RECIPE) for lr in ("0.0001", "0.0003", "0.001")})
    sens.update({f"sens_tol_{c}-{o}": (FULL + ["--chord-tol", c, "--overlap-tol", o], RECIPE)
                 for c, o in (("0.02", "0.03"), ("0.03", "0.05"), ("0.05", "0.08"))})
    sens.update({f"sens_vmax_{q}": (FULL + ["--vmax-percentile", q], RECIPE) for q in ("90", "95", "99")})
    return [job(n, 0, a, r, 500_000) for n, (a, r) in sens.items()]


def evaluate(args, out):
    if out.exists():
        return
    cmd = [PY, "evaluate.py", *PIG, *args, "--workers", "4", "--out", str(out)]
    print("evaluate ->", out.name, flush=True)
    subprocess.run(cmd, cwd=ROOT, check=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--no-eval", action="store_true")
    a = ap.parse_args()
    (ROOT / "runs" / "logs").mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)

    run(ablations(a.seeds) + sensitivity(), a.jobs)
    print("all ablation and sensitivity runs finished", flush=True)
    if a.no_eval:
        return
    R = ROOT / "runs"
    evaluate(["--split", "test", "--mode", "given", "--cost", "parncutt12", "balliauw15", "--no-baselines",
              "--reference", "results/twohand/m0_given_test.json", "results/twohand/m0_assign_test.json",
              "--success-gap", "0.10", "--ckpt", str(R / "v2_abl_*_s*" / "best.pt"), str(R / "v2_r3_s*" / "best.pt"),
              str(R / "v2_2c_s*" / "best.pt")], RES / "ablations_final.json")
    evaluate(["--split", "val", "--mode", "given", "--no-baselines", "--reference", "results/twohand/m0_given_val.json",
              "--ckpt", str(R / "v2_sens_*_s0" / "best.pt")], RES / "sensitivity_final.json")
    print("evaluation finished", flush=True)


if __name__ == "__main__":
    sys.exit(main())
