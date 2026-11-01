"""Does an agent solve the pieces it trained on? Wasted cost per note on PIG train / test and on
held-out beginner tunes, plus test Mgen.

Waste per note = (agent cost - M0 cost) / notes under the agent's own reward; 0 = optimal. Equal
waste on train and test means the agent underfits (it never solved its training pieces) rather
than overfits.

    python experiments/check_fit.py --ckpt runs/r1_s0/best.pt "runs/r1x_*_s0/best.pt"
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "webapp"), str(ROOT)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pig-dir", default="data/PianoFingeringDataset_v1.2")
    ap.add_argument("--ckpt", nargs="+", required=True, help="checkpoints or globs (mode given)")
    ap.add_argument("--out", help="also write the table (markdown) here")
    args = ap.parse_args()

    import torch

    torch.set_num_threads(2)
    from beginner_data import heldout_tunes
    from evaluate import _env_cfg
    from fingerly.dqn import Agent
    from fingerly.metrics import rollout, summarize
    from fingerly.twohand.env import SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig, piece_events, segment_stream
    from fingerly.twohand.search import dp_segment

    ckpts = [p for g in args.ckpt for p in (sorted(glob.glob(g)) or [g])]
    agents = {Path(p).parent.name: Agent.load(p) for p in ckpts}
    meta = next(iter(agents.values())).extra
    prep = PrepConfig(**meta["prep"])
    cfg = _env_cfg(meta["env"], meta["v_max"])
    ctx = Context(args.pig_dir, prep)

    def pool_of(segs, cache=True):
        pool = SegmentPool(segs, cfg, bonus=False, cache=cache)
        m0 = {(i.seg.piece, i.seg.index): dp_segment(i).cost for i in pool.infos}
        return pool, m0, sum(i.seg.n_notes for i in pool.infos)

    pools = {"PIG train": pool_of(ctx.split.train), "PIG test": pool_of(ctx.split.test)}
    tunes = []
    for name, notes in heldout_tunes().items():
        tunes += segment_stream(name, piece_events([notes], prep), prep, min_len=1)
    pools["Beginner tunes"] = pool_of(tunes, cache=False)

    lines = ["| Checkpoint | Waste/note PIG train | Waste/note PIG test | Waste/note beginner tunes | Test Mgen |",
             "| --- | --- | --- | --- | --- |"]
    for k, ag in agents.items():
        row = []
        for name, (pool, m0, notes) in pools.items():
            eps = rollout(pool, ag.greedy())
            cost = sum(r.rules + r.extra for e in eps for r in e.records)
            row.append(f"{(cost - sum(m0.values())) / notes:.2f}")
            if name == "PIG test":
                mgen = summarize(eps)["Mgen"]
        lines.append(f"| {k} | " + " | ".join(row) + f" | {100 * mgen:.1f}% |")
        print(lines[-1], flush=True)
    text = "\n".join(lines)
    print("\n" + text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
