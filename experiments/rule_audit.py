"""Which reward terms disagree with the pianists? For every segment, the reward's exact optimum (M0)
and each pianist's fingering are scored term by term (parncutt12's 12 rules + time-leap). A term
where pianists pay much more than M0 is one the reward punishes but pianists accept: M0 avoids it,
and in doing so moves away from what pianists play. Training + validation pieces only (no test).

    python experiments/rule_audit.py --splits train val --out results/twohand_v2/rule_audit.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def term_costs(model, stream, v_max, w_time):
    """[12 rules..., time-leap] of a stream [(hand, pitches, fingers, onset)]; also per-event counts."""
    from fingerly.twohand.rules import merged_cost, thumb_position, time_leap

    rules = merged_cost(model, [(h, p, f) for h, p, f, _ in stream])
    leap, last = 0.0, {}
    for h, p, f, t in stream:
        th = thumb_position(h, p, f)
        if h in last:
            leap += time_leap(th - last[h][0], t - last[h][1], v_max, w_time)
        last[h] = (th, t)
    return np.append(rules, leap)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pig-dir", default="data/PianoFingeringDataset_v1.2")
    ap.add_argument("--ckpt", default="runs/v2_r3_s0/best.pt", help="only for its settings (reward, v_max)")
    ap.add_argument("--splits", nargs="+", default=["train", "val"], choices=["train", "val"])
    ap.add_argument("--out")
    args = ap.parse_args()

    import torch

    from evaluate import _env_cfg
    from fingerly.metrics import human_items
    from fingerly.paper.rules import RULE_NAMES
    from fingerly.twohand.actions import fingers_of
    from fingerly.twohand.env import SegmentPool
    from fingerly.twohand.prepare import Context, PrepConfig
    from fingerly.twohand.search import dp_segment

    meta = torch.load(args.ckpt, map_location="cpu", weights_only=False)["extra"]
    ctx = Context(args.pig_dir, PrepConfig(**meta["prep"]))
    cfg = _env_cfg(meta["env"], meta["v_max"])
    names = list(RULE_NAMES) + ["time-leap"]

    m0_tot, hum_tot, notes, n_ann = np.zeros(13), np.zeros(13), 0, 0
    m0_hits, hum_hits = np.zeros(13), np.zeros(13)
    for split in args.splits:
        pool = SegmentPool(ctx.segments(split), cfg, bonus=False)
        model = pool.model
        for info in pool.infos:
            seg, order = info.seg, info.order
            K = seg.n_annotators
            if not K:
                continue
            res = dp_segment(info)
            m0 = [(h, seg.events[i].pitches, fingers_of(int(s), h), seg.events[i].onset)
                  for i, (h, s) in zip(order, res.fingering)]
            c = term_costs(model, m0, cfg.v_max, cfg.w_time)
            m0_tot += c * K  # weight like the annotators so both sides count each segment K times
            m0_hits += (c > 0) * K
            for k in range(K):
                hs = [(h, ps, fs, t) for _, h, ps, fs, t in human_items(seg, order, k)]
                c = term_costs(model, hs, cfg.v_max, cfg.w_time)
                hum_tot += c
                hum_hits += c > 0
            notes += seg.n_notes * K
            n_ann += K

    excess = hum_tot - m0_tot
    order_ = np.argsort(-excess)
    pos = excess[excess > 0].sum()
    lines = [f"Pieces: {' + '.join(args.splits)}; {n_ann} annotator-segments, {notes} annotator-notes. "
             "Points per 100 notes (reward weight 1 for every term).", "",
             "| Term | Pianists | M0 (reward optimum) | Pianists − M0 | Share of excess |",
             "| --- | --- | --- | --- | --- |"]
    for j in order_:
        lines.append(f"| {names[j]} | {100 * hum_tot[j] / notes:.2f} | {100 * m0_tot[j] / notes:.2f} | "
                     f"{100 * excess[j] / notes:+.2f} | {100 * max(excess[j], 0) / pos:.0f}% |")
    lines.append(f"| **total** | {100 * hum_tot.sum() / notes:.2f} | {100 * m0_tot.sum() / notes:.2f} | "
                 f"{100 * excess.sum() / notes:+.2f} | |")
    text = "\n".join(lines)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
