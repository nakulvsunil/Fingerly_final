"""Continue training the A2 agent with beginner-style pieces added (web app add-on).

The A2 agent fingers PIG pieces at about 2x the M0 optimum but simple beginner tunes at about 30x:
PIG has almost no music like them. This continues A2 (all weights from runs/a2_s2/best.pt, same
settings: lambda 2, demonstrations 0.25, elite replay 0.25) on PIG's training pieces plus random
beginner pieces from beginner_data.py (rule reward only on those: they have no labels).

Checkpoint selection uses PIG validation Mgen and the wasted cost per note on a separate set of
generated beginner pieces, (agent cost - M0 cost) / notes:  select = Mgen - 0.05 * waste. (A ratio
agent / M0 is misleading on easy pieces, where M0 is close to 0.) The real beginner tunes in
beginner_data.heldout_tunes() are never used here; check_beginner.py scores them afterwards.

    python webapp/train_beginner.py --pig-dir data/PianoFingeringDataset_v1.2 --device cuda --seed 0 --out runs/beginner_s0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pig-dir", required=True)
    ap.add_argument("--init", default="runs/a2_s2/best.pt", help="checkpoint to continue (all weights)")
    ap.add_argument("--beginner", type=int, default=1500, help="generated beginner pieces added to training")
    ap.add_argument("--beginner-val", type=int, default=60, help="generated beginner pieces for selection")
    ap.add_argument("--steps", type=int, default=400_000)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--eps-start", type=float, default=0.2, help="lower than from scratch: the policy is already trained")
    ap.add_argument("--eval-every", type=int, default=25_000)
    ap.add_argument("--patience", type=int, default=150_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import torch

    torch.set_num_threads(args.threads)
    from beginner_data import beginner_segments
    from fingerly.dqn import Agent, TrainConfig, Trainer
    from fingerly.metrics import rollout, summarize
    from fingerly.synth import twohand_segments
    from fingerly.twohand.env import EnvConfig, SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig
    from fingerly.twohand.search import dp_segment, m0_costs

    t0 = time.time()
    src = Agent.load(args.init)
    meta0 = src.extra
    if meta0.get("mode") != "given":
        raise SystemExit("--init must be a mode-given (2b) checkpoint such as runs/a2_s2/best.pt")
    a0 = meta0["args"]
    prep = PrepConfig(**meta0["prep"])
    ctx = Context(args.pig_dir, prep, a0["vmax_percentile"], verbose=True)
    ecfg = EnvConfig(**{k: v for k, v in meta0["env"].items() if k in EnvConfig.__dataclass_fields__})
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    beg = beginner_segments(args.beginner, seed=10_000 + args.seed, prep=prep)
    train_segs = list(ctx.split.train) + twohand_segments(a0["synthetic"], seed=1000 + args.seed, prep=prep) + beg
    pool = SegmentPool(train_segs, ecfg, bonus=True, cache=False)
    val_pool = SegmentPool(ctx.split.val, ecfg, bonus=False)
    bval_pool = SegmentPool(beginner_segments(args.beginner_val, seed=20_000, prep=prep, name="beginner-val"), ecfg,
                            bonus=False, cache=False)
    m0 = m0_costs(val_pool, a0["val_beam"])
    bm0 = sum(dp_segment(i).cost for i in bval_pool.infos)
    bnotes = sum(i.seg.n_notes for i in bval_pool.infos)
    n_pig = len(ctx.split.train)
    print(f"training pool: {n_pig} PIG + {a0['synthetic']} synthetic + {len(beg)} beginner segments "
          f"({sum(len(s) for s in beg)} beginner events vs {sum(len(s) for s in ctx.split.train)} PIG events); "
          f"built in {time.time() - t0:.0f}s", flush=True)

    def evaluate(agent):
        s = summarize(rollout(val_pool, agent.greedy()), m0)
        cost = sum(r.rules + r.extra for e in rollout(bval_pool, agent.greedy()) for r in e.records)
        s["beginner_waste"] = (cost - bm0) / bnotes
        s["pig_waste"] = (s["cost"] - sum(m0.values())) / s["notes"]
        s["select"] = s["Mgen"] - 0.05 * s["beginner_waste"]
        print(f"  eval: PIG val Mgen {s['Mgen']:.3f}, waste/note {s['pig_waste']:.2f} | "
              f"beginner waste/note {s['beginner_waste']:.2f} | select {s['select']:.4f}", flush=True)
        return s

    t = src.cfg
    tcfg = TrainConfig(algo="ddqn", steps=args.steps, n_envs=t.n_envs, lr=args.lr, gamma=t.gamma, n_step=t.n_step,
                       buffer=t.buffer, batch=t.batch, train_every=t.train_every, learning_starts=t.learning_starts,
                       tau=t.tau, eps_start=args.eps_start, eps_end=t.eps_end, eps_frac=t.eps_frac, hidden=t.hidden,
                       double=t.double, dueling=t.dueling, elite=t.elite, demos=t.demos, eval_every=args.eval_every,
                       patience=args.patience, checkpoint_every=50_000, save_buffer=False, seed=args.seed,
                       device=args.device)
    meta = dict(meta0, args={**a0, "beginner": vars(args)}, seed=args.seed, select="beginner",
                beginner=dict(n=args.beginner, init=args.init))
    (out / "beginner_args.json").write_text(json.dumps(vars(args), indent=1))
    trainer = Trainer(pool, tcfg, out, evaluate, "select", 1.0, meta, bc_init=args.init)
    evaluate(trainer.agent)  # the starting point (A2), for comparison with the eval lines below
    trainer.train()
    print(f"done in {(time.time() - t0) / 60:.1f} min; checkpoints in {out}", flush=True)


if __name__ == "__main__":
    main()
