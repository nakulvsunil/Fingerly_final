"""R4 variant: fine-tune on each piece (finetune.py's loop: lr 1e-4, eps 0.1, rule reward only, no
labels) but keep the greedy fingering with the lowest cost under the agent's own reward seen after
any episode, instead of the last one. The pianists' fingerings are never used.

    python experiments/finetune_best.py --ckpt runs/v2_r3_s0/best.pt --split val --episodes 100 \
        --out runs/v2_r4best_val_s0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def finetune_best(ckpt, pool, episodes, lr, eps, seed, device, batch=256, train_every=4, buffer=50_000,
                  deadline=None):
    """deadline: time.time() value after which no new episode starts (None = run all episodes)."""
    from fingerly.dqn import Agent, NStep, Replay, set_seeds
    from fingerly.metrics import rollout
    from fingerly.twohand.env import Episode

    set_seeds(seed)
    rng = np.random.default_rng(seed)
    agent = Agent.load(ckpt, device)
    for g in agent.opt.param_groups:
        g["lr"] = lr
    cfg = agent.cfg
    buf = Replay(buffer, pool.cfg.obs_dim, pool.cfg.n_actions)

    def greedy_eps():
        e = rollout(pool, agent.greedy())
        return sum(r.rules + r.extra for x in e for r in x.records), e

    best_cost, best = greedy_eps()
    curve, best_ep, acc = [best_cost], 0, 0.0
    for k in range(1, episodes + 1):
        if deadline is not None and time.time() >= deadline:
            break
        for info in pool.infos:
            ep = Episode(pool.cfg, pool.model)
            o, m = ep.reset(info)
            ns = NStep(cfg.n_step, cfg.gamma)
            while not ep.done:
                a = int(agent.act(o[None], m[None], eps, rng)[0])
                r, done = ep.step(a)
                o2, m2 = (ep.obs(), ep.mask()) if not done else (np.zeros_like(o), np.ones_like(m))
                for tr in ns.push(o, a, r, o2, m2, done):
                    buf.add(*tr[:6])
                o, m = o2, m2
                if len(buf) >= batch:
                    acc += 1.0 / train_every
                    while acc >= 1:
                        agent.update(*buf.take(buf.idx(rng, batch)))
                        acc -= 1
        c, e = greedy_eps()
        curve.append(c)
        if c < best_cost:
            best_cost, best, best_ep = c, e, k
    fing = [dict(piece=e.info.seg.piece, index=e.info.seg.index, fingering=[[r.hand, r.set] for r in e.records])
            for e in best]
    return curve, best_ep, fing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--pig-dir", default="data/PianoFingeringDataset_v1.2")
    ap.add_argument("--split", choices=["test", "val"], default="val")
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--eps", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--pieces", nargs="*", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import torch

    torch.set_num_threads(1)
    from fingerly.twohand.env import EnvConfig, SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig

    meta = torch.load(args.ckpt, map_location="cpu", weights_only=False)["extra"]
    ctx = Context(args.pig_dir, PrepConfig(**meta["prep"]))
    env = dict(meta["env"], lam=0.0, v_max=ctx.v_max)
    ecfg = EnvConfig(**env)
    by = defaultdict(list)
    for s in ctx.segments(args.split):
        by[s.piece].append(s)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(dict(vars(args), env=env), indent=1, default=str))
    for piece in sorted(by):
        f = out / f"{piece}.json"
        if (args.pieces and piece not in args.pieces) or f.exists():
            continue
        t = time.time()
        curve, best_ep, fing = finetune_best(args.ckpt, SegmentPool(by[piece], ecfg, bonus=False), args.episodes,
                                             args.lr, args.eps, args.seed, args.device)
        f.write_text(json.dumps(dict(piece=piece, curve=curve, best_episode=best_ep, segments=fing,
                                     seconds=time.time() - t, ckpt=args.ckpt, seed=args.seed), default=float))
        print(f"{piece}: cost {curve[0]:.0f} -> best {min(curve):.0f} (episode {best_ep}), {time.time() - t:.0f}s",
              flush=True)
    if not args.pieces:
        (out / "done.json").write_text("{}")


if __name__ == "__main__":
    main()
