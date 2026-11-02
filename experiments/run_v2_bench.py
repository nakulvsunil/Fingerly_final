"""Retrain the RL benchmark algorithms (README §C.9.5, E8) on the final v2 setup and evaluate them.

The first benchmarks (runs/dqn_*, ppo_*, qlearn) used γ 0.99, λ 0.5 and early stopping. Here they get
the v2 recipe of the main method: γ 0.5, λ 4 (rule reward only for tabular Q-learning, as before),
no early stopping, 3 seeds, 1M steps:

    python experiments/run_v2_bench.py --jobs 4 [--wait-for runs/logs/v2_ablsens_runner.out]

--wait-for: start only once that runner log says "evaluation finished" (queue behind another batch).
Runs: runs/v2_dqn_s*, runs/v2_ppo_s*, runs/v2_qlearn. Results: results/twohand_final/benchmarks_final.json.
"""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from run_v2 import GIVEN, PIG, PY, ROOT, job, run

LAM = "4"
RES = ROOT / "results" / "twohand_final"


def jobs(seeds):
    J = [job("dqn", s, GIVEN + ["--lam", LAM, "--algo", "dqn"], ["--gamma", "0.5"], 1_000_000) for s in seeds]
    for s in seeds:
        out = ROOT / "runs" / f"v2_ppo_s{s}"
        J.append((f"v2_ppo_s{s}", [PY, "train_ppo.py", *PIG, "--mode", "given", "--lam", LAM, "--gamma", "0.5",
                                   "--seed", str(s), "--out", str(out)], out / "done.json"))
    out = ROOT / "runs" / "v2_qlearn"
    J.append(("v2_qlearn", [PY, "train.py", *PIG, "--mode", "given", "--algo", "qlearn", "--split", "test",
                            "--episodes", "500", "--gamma", "0.5", "--out", str(out)], out / "148.json"))
    return J


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--wait-for", help="runner log; start after it prints 'evaluation finished'")
    a = ap.parse_args()
    if a.wait_for:
        print(f"{time.strftime('%H:%M:%S')} waiting for {a.wait_for}", flush=True)
        while "evaluation finished" not in (Path(a.wait_for).read_text(errors="replace") if Path(a.wait_for).exists() else ""):
            time.sleep(60)
    (ROOT / "runs" / "logs").mkdir(parents=True, exist_ok=True)
    run(jobs(a.seeds), a.jobs)
    print("all benchmark runs finished", flush=True)

    out = RES / "benchmarks_final.json"
    if not out.exists():
        R = ROOT / "runs"
        cmd = [PY, "evaluate.py", *PIG, "--split", "test", "--mode", "given", "--cost", "parncutt12", "balliauw15",
               "--no-baselines", "--reference", "results/twohand/m0_given_test.json", "--success-gap", "0.10",
               "--wilcoxon", "--compute", "--ckpt", str(R / "v2_dqn_s*" / "best.pt"), str(R / "v2_ppo_s*" / "best.zip"),
               str(R / "v2_r3_s*" / "best.pt"), "--fingerings", str(R / "v2_qlearn"), "--workers", "4", "--out", str(out)]
        subprocess.run(cmd, cwd=ROOT, check=False)
    print("evaluation finished", flush=True)


if __name__ == "__main__":
    main()
