"""Compare checkpoints on held-out beginner tunes and on the 30 PIG test pieces.

    python webapp/check_beginner.py --pig-dir data/PianoFingeringDataset_v1.2 \
        --ckpt runs/a2_s2/best.pt "runs/beginner_s*/best.pt" --out results_beginner.md

Beginner tunes (beginner_data.heldout_tunes: never trained on, never used for selection): wasted
cost per note = (agent cost - M0 cost) / notes, under the agent's own reward (0 = optimal).
PIG test: Mgen (match with the pianists), waste per note and gap to M0, the same quantities as the
project's evaluation, computed with the same code for every checkpoint.
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pig-dir", required=True)
    ap.add_argument("--ckpt", nargs="+", required=True, help="checkpoints or globs")
    ap.add_argument("--no-pig", action="store_true", help="skip the PIG test pieces")
    ap.add_argument("--out", help="also write the tables (markdown) here")
    args = ap.parse_args()

    import torch

    torch.set_num_threads(1)
    from beginner_data import heldout_tunes
    from evaluate import _env_cfg
    from fingerly.dqn import Agent
    from fingerly.metrics import rollout, summarize
    from fingerly.twohand.actions import fingers_of
    from fingerly.twohand.env import SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig, piece_events, segment_stream
    from fingerly.twohand.search import dp_segment, m0_costs

    ckpts = [p for g in args.ckpt for p in (sorted(glob.glob(g)) or [g])]
    agents = {Path(p).parent.name: Agent.load(p) for p in ckpts}
    meta = next(iter(agents.values())).extra
    prep = PrepConfig(**meta["prep"])
    cfg = _env_cfg(meta["env"], meta["v_max"])
    tunes = heldout_tunes()
    pools = {}
    for name, notes in tunes.items():
        segs = segment_stream(name, piece_events([notes], prep), prep, min_len=1)
        pool = SegmentPool(segs, cfg, bonus=False, cache=False)
        pools[name] = (pool, sum(dp_segment(i).cost for i in pool.infos), len(notes))

    lines = ["## Held-out beginner tunes: wasted cost per note (0 = the optimum)", "",
             "| Tune | " + " | ".join(agents) + " |", "| --- |" + " --- |" * len(agents)]
    tot = {k: [0.0, 0] for k in agents}
    rh = {}
    for name, (pool, m0, n) in pools.items():
        row = []
        for k, ag in agents.items():
            eps = rollout(pool, ag.greedy())
            c = sum(r.rules + r.extra for e in eps for r in e.records)
            row.append(f"{(c - m0) / n:.2f}")
            tot[k][0] += c - m0
            tot[k][1] += n
            rh[(name, k)] = " ".join(str(fingers_of(r.set, r.hand)[0]) for e in eps for r in e.records if r.hand == "R")
        lines.append(f"| {name} | " + " | ".join(row) + " |")
    lines.append("| **All tunes** | " + " | ".join(f"**{t[0] / t[1]:.2f}**" for t in tot.values()) + " |")

    lines += ["", "## Right-hand fingerings", ""]
    for name in ("Ode to Joy", "Mary Had a Little Lamb", "Twinkle, Twinkle, Little Star"):
        lines.append(f"**{name}**")
        lines += [f"- {k}: `{rh[(name, k)][:80]}`" for k in agents]
        lines.append("")

    if not args.no_pig:
        ctx = Context(args.pig_dir, prep, meta["args"]["vmax_percentile"])
        test = SegmentPool(ctx.split.test, cfg, bonus=False)
        m0 = m0_costs(test, 1000)
        lines += ["## PIG test pieces (30, never trained on)", "",
                  "| Checkpoint | Mgen | Waste / note | Gap to M0 |", "| --- | --- | --- | --- |"]
        for k, ag in agents.items():
            s = summarize(rollout(test, ag.greedy()), m0)
            waste = (s["cost"] - sum(m0.values())) / s["notes"]
            lines.append(f"| {k} | {100 * s['Mgen']:.1f}% | {waste:.2f} | {s['gap']:.3f} |")

    text = "\n".join(lines)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
