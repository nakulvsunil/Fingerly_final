"""Seed ensemble of Part C RL agents: at each event, the action with the highest Q averaged over the
checkpoints (legal actions only). Writes per-piece fingerings in finetune.py's format, so evaluate.py
scores them with --fingerings like R4.

    python experiments/ensemble.py --ckpt "runs/v2_r3_s*/best.pt" --split val --out runs/v2_ens_r3_val
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def ensemble_policy(agents):
    from fingerly.dqn import NEG

    def pol(obs, masks):
        q = np.mean([ag.q_values(obs) for ag in agents], axis=0)
        q[~masks] = NEG
        return q.argmax(1)

    return pol


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", nargs="+", required=True, help="checkpoints or globs (same mode and settings)")
    ap.add_argument("--pig-dir", default="data/PianoFingeringDataset_v1.2")
    ap.add_argument("--split", choices=["test", "val"], default="val")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import torch

    torch.set_num_threads(4)
    from evaluate import _env_cfg
    from fingerly.dqn import Agent
    from fingerly.metrics import rollout
    from fingerly.twohand.env import SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig

    ckpts = sorted({p for g in args.ckpt for p in (glob.glob(g) or [g])})
    agents = [Agent.load(p) for p in ckpts]
    meta = agents[0].extra
    for p, ag in zip(ckpts, agents):
        if ag.extra["env"] != meta["env"] or ag.extra["prep"] != meta["prep"]:
            raise SystemExit(f"{p} has different settings from {ckpts[0]}")
    ctx = Context(args.pig_dir, PrepConfig(**meta["prep"]))
    cfg = _env_cfg(meta["env"], meta["v_max"])
    pool = SegmentPool(ctx.segments(args.split), cfg, bonus=False)
    eps = rollout(pool, ensemble_policy(agents))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    env = dict(meta["env"], lam=0.0, v_max=meta["v_max"])
    (out / "config.json").write_text(json.dumps(dict(ckpt=ckpts, split=args.split, env=env, prep=meta["prep"],
                                                     v_max=meta["v_max"], mode=meta.get("mode")), indent=1))
    by = defaultdict(list)
    for e in eps:
        by[e.info.seg.piece].append(dict(piece=e.info.seg.piece, index=e.info.seg.index,
                                         fingering=[[r.hand, r.set] for r in e.records]))
    for piece, segs in by.items():
        (out / f"{piece}.json").write_text(json.dumps(dict(piece=piece, segments=segs, ckpt=ckpts)))
    (out / "done.json").write_text("{}")
    print(f"{len(ckpts)} checkpoints, {len(eps)} segments -> {out}")


if __name__ == "__main__":
    main()
