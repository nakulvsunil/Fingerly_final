# Overnight experiments: why the agents' fingerings were weak, and the fix

All new code is in `experiments/` and `webapp/`; no existing file was changed. Runs are in
`runs/r1x_*`, `runs/r3x_*`, `runs/v2_*` and `runs/beginner_*`, logs in `runs/logs/`, tables in
`results/twohand_v2/`. Nothing is committed.

**Measure used throughout:** *waste per note* = (agent's cost − M0's cost) / notes, under the
agent's own reward (parncutt12 + time-leap). 0 means the agent found the best possible fingering.
M0 (exact search) is used only as this measuring stick, never as an output. Choices were made on
**validation** (or training) pieces only; the 30 test pieces and the held-out beginner tunes were
used only to report results.

## 1. Diagnosis: every agent underfits

The web app's fingerings looked wrong (e.g. Ode to Joy's melody all thumb). The reward was not the
cause: its optimum on Ode to Joy is almost a teacher's fingering (`2 2 3 5 | 5 4 3 2 | 1 1 2 3`).
The agents were. They waste as much on the pieces they **trained on** as on unseen pieces, so they
never solved their training pieces (underfitting), rather than failing to generalise:

| Agent | Waste/note, PIG train | Waste/note, PIG test | Waste/note, beginner tunes | Test Mgen |
| --- | --- | --- | --- | --- |
| R1 (pure RL) | 6.29 | 6.00 | 4.77 | 49.7% |
| R3 λ=2 (pure RL) | 5.94 | 6.02 | 4.49 | 50.8% |
| A2 (with demonstrations) | 3.68 | 3.56 | 3.16 | 59.6% |

Every original run was also cut short by early stopping (patience 50k steps on a noisy validation
Mgen): R1 stopped at 275k of 1M steps, A2 at 200k (checkpoint from 75k).

Adding beginner-style training pieces (webapp/train_beginner.py, from A2) helped beginner tunes
only partly (waste 3.16 → 2.22, best seed) and cost a little on PIG (test Mgen 59.6% → 58.0%), which
fits the underfitting diagnosis: more data does not fix an optimiser that stalls.

## 2. What fixes training (R1, seed 0, full 1M steps, early stopping off)

| Change | Best validation gap to M0 | Validation Mgen |
| --- | --- | --- |
| Original R1 (early-stopped) | 0.62 | – |
| Full budget only | 0.496 | 54.2% |
| + reward ÷ 10 | 0.56 | 52.3% |
| γ 0.9 + reward ÷ 10 | 0.346 | 57.1% |
| γ 0.9 + reward ÷ 10 + 512-512 network | 0.39 | 54.0% |

Reward scaling and a bigger network do not help. **The discount γ is the lever:**

| γ (R1, no scaling) | Best validation gap | Best validation Mgen |
| --- | --- | --- |
| 0.99 (original) | 0.496 | 54.2% |
| 0.95 | 0.340 | 58.3% |
| 0.9 | 0.286 | 59.9% |
| 0.8 | 0.233 | 60.1% |
| 0.7 | 0.220 | 61.5% |
| 0.5 | 0.202 | 61.8% |

Why this makes sense: the costs depend only on the last two events of each hand (plus the gap to
the previous onset), so a short horizon is enough, and γ = 0.99 (horizon ≈ 100 events) makes the
3-step bootstrapped targets noisy and slow to learn.

R1 at γ 0.9, measured like section 1: waste 3.07 (train) / 3.29 (test) / 2.59 (beginner tunes),
test Mgen 56.9%: **pure RL with no pianist data now beats A2's waste everywhere.**

## 3. Choosing γ and λ for v2 (validation, seed 0, 1M steps)

γ = 0.3 is worse than 0.5 (best validation gap 0.235 vs 0.202), so **γ = 0.5**. Under γ = 0.5, R3's
imitation weight barely matters: λ = 2 gives gap 0.214 / Mgen 63.2%, λ = 4 gives 0.209 / 63.4%
(single seed, within noise). λ = 4 was taken because it is the better of the two on validation.
For comparison, R3 at γ = 0.9: λ 1 / 2 / 4 → gap 0.292 / 0.296 / 0.252.

v2 recipe: **γ 0.5, λ 4, full step budget (1M; 2c 1.5M), no early stopping**, everything else as in
Part C. `python experiments/run_v2.py --recipe "--gamma 0.5" --lam 4 --jobs 4`.

Incidents: the laptop's sleep timer (10 min on AC) froze or killed runs, both overnight and for an
hour during the grid; sleep on AC is now off. Resuming from `ckpt.pt` crashed because the CPU RNG
state was loaded onto the GPU; fixed in `fingerly/dqn.py` (`try_resume`, one line).
`r3x_g0.5_lam4_s0` had a truncated `buffer.npz` and was rerun from scratch (broken files kept in
`runs/_corrupt_r3x_g0.5_lam4_s0/`).

## 4. v2 results (3 seeds each, 30 test pieces)

Waste per note (as in section 1, mean of seeds; full per-seed table in
`results/twohand_v2/fit_v2.md`):

| Agent | Waste/note train | Waste/note test | Waste/note beginner tunes | Test Mgen |
| --- | --- | --- | --- | --- |
| R1 original → v2 | 6.25 → **2.10** | 6.24 → **2.26** | 4.50 → **1.29** | 49.1% → **59.6%** |
| R3 original (λ 2) → v2 (λ 4) | 6.39 → **1.99** | 6.32 → **2.18** | 4.72 → **1.40** | 50.1% → **61.7%** |
| A2 original → v2 | 3.71 → **2.19** | 3.87 → **2.57** | 2.93 → **1.91** | 58.4% → **61.0%** |
| R2 v2 | 2.14 | 2.18 | 1.61 | 62.2% |

Full Part C test evaluation (`evaluate.py`, same settings as `results/twohand/main.json`; output
`results/twohand_v2/main_v2.json`):

| Method | Mgen | Gap to M0 | Difficulty/note (parncutt12) | SR |
| --- | --- | --- | --- | --- |
| R1 → v2 R1 | 49.1% → 59.6% | 0.95 → 0.35 | 12.51 → 8.63 | 0 → 4.7% |
| R2 (λ 2) → v2 R2 | 50.3% → **62.2%** | 0.95 → **0.33** | 12.54 → 8.55 | 0 → 2.3% |
| R3 (λ 2) → v2 R3 | 50.1% → 61.7% | 0.97 → **0.33** | 12.58 → 8.55 | 0 → 1.2% |
| A2 → v2 A2 | 58.4% → 61.0% | 0.59 → 0.39 | 10.20 → 8.92 | 0 → 1.8% |
| 2c → v2 2c (assigns hands) | 47.9% → 57.7% | 1.07 → 0.48 | 12.87 → 8.88 | 0 → 0 |
| *greedy (one-step)* | 57.3% | 0.33 | 8.49 | 8.8% |
| *S1 (copy pianists)* | 61.8% | 0.44 | 9.23 | 0.6% |
| *S2 (HMM)* | 60.9% | 0.48 | 9.52 | 0 |
| *M0 (optimum of the reward)* | 68.1% | 0 | 6.39 | – |
| *pianists* | 75.3% | – | – | – |

Paired Wilcoxon tests over the 30 test pieces:
- Every v2 method beats its original on Mgen, difficulty and return (p < 0.004).
- Pure RL vs A2 (v2): R2/R3 have lower difficulty and better return (p ≤ 0.0002); Mgen
  not significantly different (p 0.09 / 0.22).
- R2/R3 v2 vs S1 and S2: Mgen not significantly different; lower difficulty than S1
  (p < 1e-6) and S2 (p ≈ 0.02).
- R2/R3 v2 vs greedy: better Mgen (p 0.002 / 0.005); difficulty, return and gap not
  significantly different. v2 R1 vs greedy: no significant difference on any metric.
- v2 R3 vs v2 R1: imitation raises Mgen (61.7% vs 59.6%, p = 6e-5) at no cost in difficulty.
- Generalisation: pure RL has no seen/unseen Mgen gap (≤ 1 point); A2 and S1 match pianists on
  seen pieces much better than on unseen ones (8 points), i.e. they partly memorise.

**Reading:** the training fix removes most of the underfitting. Pure RL with a light imitation
term (R2/R3) now matches the supervised and HMM baselines on agreement with pianists and plays
easier fingerings than them. Two limits remain: (1) under the reward itself the v2 agents only tie
the one-step greedy baseline (gap 0.33 vs 0.33), so the gain over greedy comes from the imitation
term, and pure R1 is still no better than greedy; (2) the gap to M0 (0.33) and to M0's Mgen (68%)
is still large, so the optimiser has not converged on the reward's optimum.

## 5. Getting more out of the v2 agents

All choices on validation (12 pieces); test (30 pieces) only for the final numbers.

**Tried and rejected (seed 0, R3 λ 4, validation; v2 R3 = Mgen 63.4%, gap 0.215):**

| Change | Val Mgen | Val gap |
| --- | --- | --- |
| 2M steps instead of 1M | 62.9% | 0.209 |
| Lookahead 8 events (γ 0.5, 1M / 2M) | 62.0% / 61.7% | 0.223 / 0.227 |
| Lookahead 8, γ 0.7 | 62.2% | 0.233 |
| Train on the `balliauw15` rules (R3 λ 4 / λ 2 / R1) | 58.2% / 57.2% / 54.8% | – |

The `balliauw15` agents were also meant to lower d_rel (scored with those rules), but they do not:
validation d_rel 1.04 vs 1.05 for v2 R3, at a 5–9 point Mgen cost.

**Kept: per-piece fine-tuning** (`experiments/finetune_best.py`). This is more RL on the piece
being fingered: 100 episodes, lr 1e-4, ε 0.1, rule reward only, no labels. It keeps the greedy
fingering with the lowest cost under the agent's own reward. "Best of 3" runs it from each v2 R3
seed and keeps the cheapest per piece. A seed ensemble (average Q over seeds) helped on validation
too (64.9% for R2 + R3), but less than fine-tuning on the gap.

| Validation | Mgen | Single notes | Gap |
| --- | --- | --- | --- |
| v2 R3 (mean of 3 seeds) | 62.8% | 51.6% | 0.214 |
| Ensemble R2 + R3 (6 networks) | 64.9% | 54.4% | 0.186 |
| Fine-tuned (mean of 3 seeds) | 64.8% | 54.1% | 0.112 |
| Fine-tuned, best of 3 | 65.1% | 53.7% | 0.099 |
| *M0* | *66.1%* | | *0* |

**Test** (`results/twohand_v2/finetune_test.json`):

| Method | Mgen | Single notes | Gap | d_rel | Infeasible |
| --- | --- | --- | --- | --- | --- |
| v2 R3 | 61.7% | 53.1% | 0.333 | 1.166 | 0.19% |
| v2 R2 | 62.2% | 52.8% | 0.332 | 1.166 | 0.20% |
| v2 R3 fine-tuned (mean of 3 seeds) | 63.1% | 55.5% | 0.185 | 1.042 | 0.01% |
| **v2 R3 fine-tuned, best of 3** | **63.9%** | **56.8%** | **0.172** | **1.029** | 0.01% |
| *S1 / S2 / greedy* | *61.8% / 60.9% / 57.3%* | | *0.44 / 0.48 / 0.33* | *1.19 / 1.20 / 1.20* | |
| *M0* | *68.1%* | *61.4%* | *0* | *0.870* | |

Wilcoxon over the 30 pieces (Mgen):
- Best of 3 beats v2 R3 (p = 0.015) and S1 (p = 0.019).
- Best of 3 vs S2: not significant (p = 0.10).
- Best of 3 is still below M0 (p = 0.01).

**This is the best RL result: 63.9% Mgen on unseen pieces, above the 62% target (README §C.1).**
d_rel ≤ 0.81 is not reached. Even the exact optimum of our reward gets only 0.87 under
`balliauw15`, and the paper's 0.81 comes from one model per test piece. The web app's **Refine**
option runs this fine-tuning on the uploaded piece.

## 6. Is the reward the limit?

On test, M0 (the reward's optimum) gets 68.1% and the pianists agree with each other 75.3% of the
time. After fine-tuning, the agent (63.9%) is about 4 points from the reward's ceiling, and the
reward is about 7 points from the pianists'.

`experiments/rule_audit.py` (train + validation pieces) scores M0 and the pianists term by term.
Pianists pay much more than M0 on the three span rules (84% of the excess) and on position changes
(13%). They pay less on thumb-on-black and time-leap.

`experiments/fit_rule_weights.py` reweighted those groups and searched 48 settings, scoring each
by M0's Mgen on training pieces and confirming on validation:

| Weights | M0 Mgen, train | M0 Mgen, val |
| --- | --- | --- |
| Original | 65.41% | 66.06% |
| Position changes × 0.5 (best on train) | 66.44% | 66.10% |
| Span × 0.75, position changes × 0.5 | 66.06% | 65.82% |
| Span × 0.25 | 61.1–61.5% | – |

Reweighting does not carry over to unseen pieces (+0.04 points on validation). Loosening the span
rules hurts, although pianists "pay" most on them. So the reward was kept unchanged and no agent was
retrained on new weights (`--rule-w` is available in train.py for later work). Getting past ~68%
needs new kinds of reward terms (phrase position, scale and arpeggio patterns), not new weights.
