"""Finger an uploaded score with a trained Part C RL agent.

The default is `v2_r3_s0`: R3 (masked Double DQN, elite replay, imitation λ = 4) retrained with the
v2 recipe (γ 0.5, full budget; experiments/RESULTS.md), seed chosen on validation. It runs in mode
`given`: the hands come from the score (upper staff = right hand). A 2c checkpoint (mode `assign`,
the agent also chooses the hand for single notes) can be passed instead.

The score goes through the same pipeline as training: notes -> events (overlaps, chords) -> merged
stream -> segments, then the greedy policy fingers every segment (no imitation bonus, as in
evaluation).

Refine (optional, slower): the agent keeps learning on the uploaded piece itself, by RL with the
rule reward only (experiments/finetune_best.py: 100 episodes from each of the v2 R3 seeds), and the
fingering with the lowest cost under that reward is kept. The three seeds run in parallel worker
processes (on the GPU when there is one); no new episode starts after REFINE_SECONDS, so long pieces
get fewer episodes than the 100 used in the evaluation. On the PIG test pieces this raises Mgen
from 61.7% to 63.9% (experiments/RESULTS.md, section 5). No pianist fingerings are used.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from score_io import Score

ROOT = Path(__file__).resolve().parent.parent
CKPT = ROOT / "runs" / "v2_r3_s0" / "best.pt"
REFINE_CKPTS = [ROOT / "runs" / f"v2_r3_s{s}" / "best.pt" for s in range(3)]
REFINE_EPISODES = 100
REFINE_SECONDS = 90  # time budget per upload: no new episode starts after it (short tunes finish well before)
_EXECUTOR = None  # worker processes for refine, one per seed, started on first use and kept


def _refine_one(job):
    """Fine-tune one seed on the piece (runs in a worker process): (lowest cost, fingering)."""
    import sys

    import torch

    sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
    torch.set_num_threads(1)
    from evaluate import _env_cfg
    from finetune_best import finetune_best
    from fingerly.twohand.env import SegmentPool

    ckpt, segs, env, v_max, episodes, deadline = job
    pool = SegmentPool(segs, _env_cfg(env, v_max), bonus=False, cache=False)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    curve, _, fing = finetune_best(ckpt, pool, episodes, 1e-4, 0.1, 0, device, deadline=deadline)
    return min(curve), fing, len(curve) - 1


def _executor(n: int):
    global _EXECUTOR
    if _EXECUTOR is None:
        from concurrent.futures import ProcessPoolExecutor

        _EXECUTOR = ProcessPoolExecutor(max_workers=n)
    return _EXECUTOR


class Fingerer:
    def __init__(self, ckpt: Path = CKPT):
        import torch

        from fingerly.dqn import Agent

        if not ckpt.exists():
            raise SystemExit(f"checkpoint {ckpt} not found: train it first (README §C.13)")
        torch.set_num_threads(1)
        self.ckpt = ckpt
        self.agent = Agent.load(str(ckpt))
        self.meta = self.agent.extra
        if self.meta.get("mode") not in ("assign", "given"):
            raise SystemExit(f"{ckpt} is not a two-hand (Part C) checkpoint")
        self.policy = self.agent.greedy()
        self.lock = threading.Lock()

    @property
    def label(self) -> str:
        if self.meta.get("mode") == "assign":
            return f"{self.ckpt.parent.name} (Part C 2c: masked Double DQN that also chooses the hand)"
        return f"{self.ckpt.parent.name} (Part C: masked Double DQN, hands from the score)"

    @property
    def refine_label(self) -> str:
        return f"fine-tuned on each piece, best of {', '.join(p.parent.name for p in self.refine_ckpts())}"

    def refine_ckpts(self) -> List[Path]:
        """Seeds used by refine: the v2 R3 seeds when they match the loaded agent's settings."""
        import torch

        out = []
        for p in [self.ckpt] + [c for c in REFINE_CKPTS if c.resolve() != self.ckpt.resolve()]:
            if p.exists():
                m = torch.load(str(p), map_location="cpu", weights_only=False).get("extra", {})
                if m.get("env") == self.meta.get("env") and m.get("prep") == self.meta.get("prep"):
                    out.append(p)
        return out

    def finger(self, score: Score, refine: bool = False) -> Tuple[List[Dict], Dict]:
        """Per score note: dict(hand, finger) or None if the agent did not reach it, plus stats.
        refine: fine-tune on this piece first (RL, rule reward only) and keep the cheapest fingering."""
        from evaluate import _env_cfg
        from fingerly.metrics import rollout
        from fingerly.pig import Note
        from fingerly.twohand.actions import fingers_of
        from fingerly.twohand.env import SegmentPool
        from fingerly.twohand.prepare import PrepConfig, piece_events, segment_stream

        prep = PrepConfig(**self.meta.get("prep", {}))
        notes, index = [], {}
        for k, n in enumerate(score.notes):
            onset = score.seconds(n.start_q)
            offset = max(score.seconds(n.start_q + n.dur_q), onset + 0.02)
            pn = Note(k, onset, offset, n.pitch, 0 if n.hand == "R" else 1, n.hand, None)
            index.setdefault(pn.key, []).append(k)
            notes.append(pn)
        events = piece_events([notes], prep)
        segs = segment_stream("upload", events, prep, min_len=1)
        # no on-disk table cache: every upload is a new piece
        pool = SegmentPool(segs, _env_cfg(self.meta["env"], self.meta["v_max"]), bonus=False, cache=False)
        refined = None
        with self.lock:
            eps = rollout(pool, self.policy)
            if refine and self.meta.get("mode") == "given":
                from fingerly.metrics import replay

                cost0 = sum(r.rules + r.extra for e in eps for r in e.records)
                cks = self.refine_ckpts()
                # one process per seed, in parallel; same settings as the evaluated runs (seed 0 each)
                import time

                deadline = time.time() + REFINE_SECONDS if REFINE_SECONDS else None
                jobs = [(str(ck), segs, self.meta["env"], self.meta["v_max"], REFINE_EPISODES, deadline) for ck in cks]
                runs = list(_executor(len(cks)).map(_refine_one, jobs))
                best = min(runs, key=lambda r: r[0], default=None)
                if best is not None and best[0] < cost0:
                    eps = replay(pool, {(f["piece"], f["index"]): [tuple(x) for x in f["fingering"]] for f in best[1]})
                refined = dict(cost_before=cost0, cost_after=min(cost0, best[0]) if best else cost0,
                               episodes=min((r[2] for r in runs), default=0), episodes_max=REFINE_EPISODES)

        out: List[Optional[Dict]] = [None] * len(score.notes)
        effort, forced = 0.0, 0
        for ep in eps:
            seg = ep.info.seg
            for r in ep.records:
                e = seg.events[r.event]
                effort += r.rules + r.extra
                forced += int(r.forced)
                for key, f in zip(e.keys, fingers_of(r.set, r.hand)):
                    for k in index.get(key, []):
                        if out[k] is None:
                            out[k] = dict(hand=r.hand, finger=int(f))
                            break
        done = sum(o is not None for o in out)
        stats = dict(fingered=done, total=len(out), segments=len(segs), effort_per_note=effort / max(done, 1),
                     forced=forced, refined=refined)
        return out, stats
