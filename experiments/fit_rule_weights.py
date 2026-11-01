"""Fit per-rule reward weights so that the reward's optimum (M0, exact DP) agrees better with the
pianists. M0 is only the yardstick for the reward here; the fingerings that are reported still come
from RL agents trained on the chosen reward. Fit on training pieces, confirm on validation; the test
pieces are not used.

Weights are set per group (rule_audit.py's findings): span rules (stretch, small-span, large-span),
position changes (count, size), thumb-on-black, and the time-leap weight w_time.

    python experiments/fit_rule_weights.py --out results/twohand_v2/rule_weights.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
GROUPS = {"span": (0, 1, 2), "pos": (3, 4), "thumb_black": (9,)}


def weights(span, pos, tb):
    w = [1.0] * 12
    for g, v in (("span", span), ("pos", pos), ("thumb_black", tb)):
        for i in GROUPS[g]:
            w[i] = v
    return w


def score(job):
    """(config, split) -> M0's Mgen and reward cost for that split."""
    import dataclasses

    import torch

    torch.set_num_threads(1)
    from evaluate import _env_cfg
    from fingerly.metrics import replay, summarize
    from fingerly.twohand.env import SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig
    from fingerly.twohand.search import dp_segment

    (span, pos, tb, wt), split, pig, ckpt = job
    meta = torch.load(ckpt, map_location="cpu", weights_only=False)["extra"]
    ctx = Context(pig, PrepConfig(**meta["prep"]))
    cfg = dataclasses.replace(_env_cfg(meta["env"], meta["v_max"]), w_time=wt,
                              rule_w=tuple(weights(span, pos, tb)))
    pool = SegmentPool(ctx.segments(split), cfg, bonus=False, cache=False)
    fing = {(i.seg.piece, i.seg.index): dp_segment(i).fingering for i in pool.infos}
    s = summarize(replay(pool, fing))
    return dict(span=span, pos=pos, thumb_black=tb, w_time=wt, split=split, Mgen=s["Mgen"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pig-dir", default="data/PianoFingeringDataset_v1.2")
    ap.add_argument("--ckpt", default="runs/v2_r3_s0/best.pt", help="only for its settings")
    ap.add_argument("--span", type=float, nargs="+", default=[0.25, 0.5, 0.75, 1.0])
    ap.add_argument("--pos", type=float, nargs="+", default=[0.5, 1.0])
    ap.add_argument("--thumb-black", type=float, nargs="+", default=[1.0, 2.0, 4.0])
    ap.add_argument("--w-time", type=float, nargs="+", default=[1.0, 2.0])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    grid = list(itertools.product(args.span, args.pos, args.thumb_black, args.w_time))
    with ProcessPoolExecutor(args.workers) as ex:
        train = list(ex.map(score, [(g, "train", args.pig_dir, args.ckpt) for g in grid]))
        train.sort(key=lambda r: -r["Mgen"])
        for r in train:
            print(f"train  span {r['span']:<5} pos {r['pos']:<4} thumb-black {r['thumb_black']:<4} "
                  f"w_time {r['w_time']:<4} M0 Mgen {100 * r['Mgen']:.2f}", flush=True)
        # confirm the 5 best training configs and the original reward on validation
        top = [(r["span"], r["pos"], r["thumb_black"], r["w_time"]) for r in train[:5]]
        top += [(1.0, 1.0, 1.0, 1.0)] if (1.0, 1.0, 1.0, 1.0) not in top else []
        val = list(ex.map(score, [(g, "val", args.pig_dir, args.ckpt) for g in top]))
    for r in val:
        print(f"val    span {r['span']:<5} pos {r['pos']:<4} thumb-black {r['thumb_black']:<4} "
              f"w_time {r['w_time']:<4} M0 Mgen {100 * r['Mgen']:.2f}")
    base = next(r for r in val if (r["span"], r["pos"], r["thumb_black"], r["w_time"]) == (1.0, 1.0, 1.0, 1.0))
    best = max(val, key=lambda r: r["Mgen"])
    out = dict(train=train, val=val, chosen=dict(best, rule_w=weights(best["span"], best["pos"], best["thumb_black"])),
               baseline_val_Mgen=base["Mgen"])
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f"chosen on validation: {best} (original reward: {100 * base['Mgen']:.2f})")


if __name__ == "__main__":
    main()
