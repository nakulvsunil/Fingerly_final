"""`train.py --mode ...` (Part C) with one extra option: --reward-scale.

The learner sees reward / scale; everything that is evaluated (costs, difficulty, gap, Mgen) uses the
environment's records, which are not scaled. All other options are train.py's own.

    python experiments/train_variant.py --reward-scale 10 --pig-dir data/PianoFingeringDataset_v1.2 \
        --mode given --lam 0 --device cuda --seed 0 --out runs/r1x_scale_s0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--reward-scale", type=float, default=1.0)
    args, rest = ap.parse_known_args()

    if args.reward_scale != 1.0:
        from fingerly.twohand import env

        step = env.Episode.step

        def scaled_step(self, action):
            r, done = step(self, action)
            return r / args.reward_scale, done

        env.Episode.step = scaled_step

    import train

    out = Path(rest[rest.index("--out") + 1])
    out.mkdir(parents=True, exist_ok=True)
    (out / "variant.json").write_text(json.dumps(dict(reward_scale=args.reward_scale, argv=rest), indent=1))
    train.twohand_main(rest)


if __name__ == "__main__":
    main()
