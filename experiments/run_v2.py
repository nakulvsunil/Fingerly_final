"""Retrain the Part C RL methods with the training fixes found by the r1x experiments ("v2").

The r1x runs showed every agent underfits (equal waste on training and test pieces) and that the
fixes are in training, not data. v2 = the original configurations with RECIPE added, λ re-chosen
on validation under the new recipe (--lam), the full step budget and no early stopping:

    R1  --lam 0          R2  --lam L          R3  --lam L --elite 1
    A2  --lam L --elite 1 --demos 0.25       2c  --mode assign, trunk from v2_r3 (same seed), curriculum

    python experiments/run_v2.py --recipe "--gamma 0.9" --lam 2 --jobs 4

Runs go to runs/v2_<method>_s<seed>; a run with done.json is skipped. Logs: runs/logs/v2_*.log.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
PIG = ["--pig-dir", "data/PianoFingeringDataset_v1.2"]
GIVEN = ["--mode", "given", "--cost", "parncutt12"]


def methods(lam: str):
    return {
        "r1": GIVEN + ["--lam", "0"],
        "r2": GIVEN + ["--lam", lam],
        "r3": GIVEN + ["--lam", lam, "--elite", "1"],
        "a2": GIVEN + ["--lam", lam, "--elite", "1", "--demos", "0.25"],
    }


def job(name: str, seed: int, args, recipe, steps: int):
    out = ROOT / "runs" / f"v2_{name}_s{seed}"
    scale = []
    if "--reward-scale" in recipe:
        i = recipe.index("--reward-scale")
        scale, recipe = recipe[i:i + 2], recipe[:i] + recipe[i + 2:]
    cmd = [PY, str(ROOT / "experiments" / "train_variant.py"), *scale, *PIG, *args, *recipe, "--steps", str(steps),
           "--patience", "100000000", "--device", "cuda", "--seed", str(seed), "--out", str(out)]
    return f"v2_{name}_s{seed}", cmd, out / "done.json"


def run(jobs, n_parallel: int):
    pending = [j for j in jobs if not j[2].exists()]
    running = []
    while pending or running:
        while pending and len(running) < n_parallel:
            name, cmd, done = pending.pop(0)
            log = open(ROOT / "runs" / "logs" / f"{name}.log", "a")
            print(f"{time.strftime('%H:%M:%S')} start {name}", flush=True)
            running.append((name, subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT), done))
        time.sleep(15)
        for r in list(running):
            if r[1].poll() is not None:
                running.remove(r)
                ok = r[1].returncode == 0 and r[2].exists()
                print(f"{time.strftime('%H:%M:%S')} {'done' if ok else 'FAILED'} {r[0]}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipe", required=True, help='training fixes, e.g. "--reward-scale 10 --gamma 0.9"')
    ap.add_argument("--lam", default="2", help="imitation weight for R2, R3, A2 and 2c")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    recipe = shlex.split(args.recipe)
    (ROOT / "runs" / "logs").mkdir(parents=True, exist_ok=True)

    run([job(m, s, a, recipe, 1_000_000) for m, a in methods(args.lam).items() for s in args.seeds], args.jobs)
    two_c = []
    for s in args.seeds:  # 2c needs v2_r3 of the same seed
        init = ROOT / "runs" / f"v2_r3_s{s}" / "best.pt"
        if init.exists():
            two_c.append(job("2c", s, ["--mode", "assign", "--cost", "parncutt12", "--lam", args.lam, "--elite", "1",
                                       "--init", str(init), "--curriculum"], recipe, 1_500_000))
    run(two_c, args.jobs)
    print("all v2 runs finished", flush=True)


if __name__ == "__main__":
    main()
