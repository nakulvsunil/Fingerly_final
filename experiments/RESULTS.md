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

## 7. Comparison with Iman & Ahn (2025)

30 PIG test pieces. The paper's numbers are from their Table 5 (stored as `paper_2025` in
`results/twohand_v2/main_v2.json`); ours are from `main_v2.json` and `finetune_test.json`. The paper
trains one model per test piece (about 45 GPU-days). Ours is one policy for all unseen pieces, plus
per-piece fine-tuning for the first two rows.

| Method | Type | Mgen | Mhigh | Msoft | Mrec | d_rel ↓ |
| --- | --- | --- | --- | --- | --- | --- |
| *Paper:* Uniform replay | RL | 62% | 67% | 75% | 70% | 0.81 |
| *Paper:* EER | RL | 61% | 66% | 75% | 69% | 0.81 |
| *Paper:* PER | RL | 59% | 67% | 75% | 69% | 0.84 |
| *Paper:* FHMM1 | HMM | 67% | 70% | 80% | 75% | 1.03 |
| *Paper:* FHMM2 | HMM | 70% | 74% | 85% | 80% | 0.97 |
| *Paper:* FHMM3 | HMM | 68% | 76% | 86% | 82% | 0.96 |
| *Paper:* Human | – | 73% | 75% | 79% | 77% | 1.00 |
| **Ours: v2 R3 + fine-tuning, best of 3** | RL | **63.9%** | 64.7% | 67.8% | 67.1% | 1.03 |
| Ours: v2 R3 + fine-tuning (mean of 3 seeds) | RL | 63.1% | 63.8% | 66.9% | 66.3% | 1.04 |
| Ours: v2 R2 | RL | 62.2% | 62.8% | 65.9% | 65.1% | 1.17 |
| Ours: v2 R3 | RL | 61.7% | 62.5% | 65.4% | 64.7% | 1.17 |
| Ours: v2 A2 | RL | 61.0% | 61.8% | 64.8% | 64.1% | 1.19 |
| Ours: v2 R1 | RL | 59.6% | 60.3% | 63.0% | 62.4% | 1.18 |
| Ours: v2 2c (also picks hands) | RL | 57.7% | 58.4% | 61.1% | 60.5% | 1.22 |
| Ours: original A2 | RL | 58.4% | 59.0% | 62.1% | 61.3% | 1.34 |
| Ours: original R3 / R1 | RL | 50.1% / 49.1% | 50.7% / 49.7% | 53.2% / 52.2% | 52.1% / 51.1% | 1.81 / 1.75 |
| *S1 (copies pianists)* | supervised | 61.8% | 62.4% | 65.5% | 64.8% | 1.19 |
| *S2 (HMM)* | HMM | 60.9% | 61.9% | 64.8% | 64.1% | 1.20 |
| *Greedy* | rule | 57.3% | 58.1% | 60.9% | 60.4% | 1.20 |
| *M0 (reward optimum)* | search | 68.1% | 68.8% | 72.1% | 71.4% | 0.87 |
| *Pianists vs each other* | – | 75.3% | – | – | – | 1.00 |

- **Mgen:** our best agent (63.9%) beats all three of the paper's RL agents (59–62%), on unseen
  pieces with one policy. Their HMM models (67–70%) remain higher.
- **d_rel:** the paper's RL is better (0.81–0.84 against 1.03). Even our reward's exact optimum only
  gets 0.87 under `balliauw15`. Training on `balliauw15` did not help (section 5).
- **Mhigh, Msoft and Mrec** are probably not computed identically. They are 4–23 points above Mgen
  in the paper but only 1–4 points above it here, so compare on Mgen.
- **d_rel aggregation:** ours is pooled over pieces (piece mean: 1.14 for the best agent); the
  paper's aggregation is not certain.
- **Absolute difficulty** values are on different scales and are left out.
- **Web app budget:** the 63.9% uses 100 fine-tuning episodes. The web app now uses at least 25,
  which matched 100 on validation (65.6% vs 65.1%, `results/twohand_v2/episodes_val.json`).

## 8. Robustness of the final agents (γ 0.5, λ 4)

The robustness results in `results/twohand/robustness.json` and `tables.md` used the original
γ = 0.99 agents. These are re-measured on the final v2 agents (3 seeds each, 30 test pieces, policy
frozen): `results/twohand_final/robustness_final.json`, full table in
`results/twohand_final/tables_final.md`. Degradation Δ = clean − perturbed, so a positive Δ Mgen is a
loss and a negative Δ d_rel is a loss.

| Perturbation | v2 R3 Δ Mgen | v2 R3 Δ d_rel | v2 R2 Δ Mgen | v2 R2 Δ d_rel | *S1 Δ Mgen* |
| --- | --- | --- | --- | --- | --- |
| Tempo × 0.75 / × 1.5 | −0.3 / −0.1 pts | −0.000 / −0.007 | +0.3 / +0.5 pts | −0.001 / −0.012 | *+0.3 / +0.0* |
| Transpose ± 1 | +3.4 / +2.7 pts | −0.003 / −0.004 | +2.7 / +2.3 pts | −0.032 / −0.034 | *+3.6 / +3.5* |
| Transpose ± 2 | +0.7 / +0.1 pts | −0.003 / +0.006 | +0.7 / +0.1 pts | −0.001 / +0.008 | *+2.1 / +1.4* |
| Transpose ± 5 | −0.5 / −0.2 pts | +0.008 / +0.005 | +0.3 / +0.4 pts | +0.003 / −0.020 | *+0.5 / +0.6* |
| Timing jitter 10 / 20 ms | +0.3 / +2.9 pts | −0.062 / −0.257 | +0.3 / +3.2 pts | −0.072 / −0.245 | *+1.5 / +3.7* |
| Hand span × 0.85 / × 1.15 | +0.4 / +1.3 pts | −0.121 / −0.032 | −0.0 / +1.1 pts | −0.112 / −0.036 | *+1.3 / +1.8* |
| Stress set (SR) | SR 0.20 (clean 0.02) | – | SR 0.18 | – | *SR 0.13* |

- **Tempo and transposition by ± 2 or ± 5** barely matter (under 1 point). Transposing by one
  semitone costs about 3 points of Mgen because the black/white key pattern changes; Mgen still uses
  the original annotations, so part of this is the caveat in README §C.11.7, not a fault.
- **Timing jitter of 20 ms** is the worst case: chord grouping breaks, d_rel worsens by about 0.25
  and Mgen drops about 3 points. A smaller hand (span × 0.85) worsens d_rel by about 0.12.
- The final RL agents degrade **no more than S1** under any perturbation, and R3 is the most stable
  on d_rel under transposition.
- By composer era (clean), v2 R3 is best on Romantic (66.2%) and Late Romantic (63.1%) pieces and
  weakest on Baroque (54.6%, 3 pieces).

## 9. Ablations of the final method (γ 0.5, λ 4)

Each variant removes or replaces one component of v2 R3 and is trained exactly like it (γ 0.5, λ 4,
1M steps, no early stopping), 2 seeds each (`python experiments/run_v2_ablsens.py`; runs `v2_abl_*`).
Evaluated on the 30 test pieces: `results/twohand_final/ablations_final.json`. Wilcoxon signed-rank
tests over the pieces against the full method: `ablations_wilcoxon.json`. Figure:
`report/figures/fig_ablation.png`. The crossing term exists only when the agent picks the hand, so
that variant is compared with v2 2c instead of R3. The first ablations (`runs/abl_*`, γ 0.99) are
superseded.

| Variant | Mgen | Δ Mgen (p) | d_rel ↓ | Δ d_rel (p) | Infeasible |
| --- | --- | --- | --- | --- | --- |
| **Full method (v2 R3, 3 seeds)** | **61.7% ± 0.3** | – | 1.166 | – | 0.19% |
| − elite replay | 62.3% ± 0.4 | +0.5 (0.28) | 1.156 | −0.010 (0.06) | 0.20% |
| − action masking (impossible-move penalty instead) | 62.1% ± 0.9 | +0.3 (0.60) | 1.129 | −0.036 (**0.02**, better) | **2.25%** (p < 0.001) |
| − overlap tolerance | 61.5% ± 0.3 | −0.2 (0.44) | 1.153 | −0.012 (0.32) | **2.03%** (p = 0.004) |
| − Double DQN and dueling | 61.4% ± 0.0 | −0.3 (0.82) | 1.181 | +0.015 (0.84) | 0.19% |
| − hand-position features | 61.1% ± 0.1 | −0.6 (0.43) | 1.206 | +0.040 (**< 0.001**, worse) | 0.20% |
| − n-step (n = 1) | 61.0% ± 0.1 | −0.7 (0.24) | 1.162 | −0.004 (0.54) | 0.17% |
| − imitation bonus (λ = 0) | 60.6% ± 0.3 | −1.1 (0.12) | 1.174 | +0.008 (0.34) | 0.19% |
| − time-leap term | 60.6% ± 0.1 | −1.1 (0.09) | 1.187 | +0.021 (0.27) | 0.20% |
| − look-ahead (K = 0) | 57.8% ± 0.3 | **−3.9 (< 0.001)** | 1.279 | +0.114 (**< 0.001**, worse) | 0.25% |
| Trained on `balliauw15` rules | 56.9% ± 0.7 | **−4.8 (< 0.001)** | 1.083 | −0.083 (**0.001**, better) | 0.19% |
| − crossing term (2c; vs v2 2c 57.7%) | 52.5% ± 3.7 | **−5.2 (0.002)** | 1.246 | +0.025 (0.56) | 0.22% |
| − full chords (`--chords reduce`) | 45.1%* | – | 1.245 | – | 0.15% |

Mgen is mean ± std over seeds. Δ is variant minus full method, in Mgen points; p is the Wilcoxon p
over the 30 pieces, in bold when p < 0.05. *With reduced chords, only one note of each chord is
fingered, so Mgen counts single notes only. Compare it with the full method's single-note Mgen,
53.2%, not with 61.7%.

- **The look-ahead matters most** among the single components: without the next 4 events in the
  state, Mgen drops 3.9 points and d_rel worsens by 0.11. Fingering is planning ahead.
- **The crossing term is essential when the agent picks the hands** (2c): without it, Mgen falls
  5.2 points and the seeds become unstable (± 3.7).
- **The reward's rules matter.** Training on the 2025 paper's `balliauw15` rules gives fingerings
  that score better under those same rules (d_rel −0.08) but agree less with pianists (−4.8
  points). Our `parncutt12` rules are closer to how pianists play.
- **Masking is about safety, not agreement.** Without masks, Mgen is unchanged and d_rel slightly
  better, but 2.25% of moves are physically impossible, against 0.19%. The overlap tolerance does
  the same for held notes (2.0% impossible moves without it).
- **The hand-position features** do not change Mgen but keep the fingerings easier (d_rel +0.04
  without them).
- **Not significant with the v2 recipe:** elite replay, Double DQN with dueling, n-step returns, the
  imitation bonus and the time-leap term (each within about 1 point, p > 0.05). Elite replay, which
  defines R3, even comes out slightly ahead when removed (+0.5, not significant). This matches
  the main results, where v2 R2 (62.2%) is level with v2 R3 (61.7%). With γ 0.5 the agent learns
  well without it, so it should not be claimed as a source of the improvement. The imitation bonus
  helps by about 1 point, consistent with R1 59.6% vs R2 62.2% in the 3-seed main results.

## 10. Sensitivity of the final method

One setting changed at a time from v2 R3; 1 seed, 500k steps, scored on the 14 validation segments
(`runs/v2_sens_*`, `results/twohand_final/sensitivity_final.json`, figure
`report/figures/fig_sensitivity.png`). The centre run (γ 0.5, λ 4, all other settings at their
defaults, 500k steps) scores **61.2%** validation Mgen, gap 0.254. Training is deterministic for a
fixed seed, so the four runs that repeat a default setting (elite 0.25, lr 3 × 10⁻⁴, tolerances
0.03 / 0.05 s, v_max 95th percentile) give exactly the centre run's numbers.

| Setting | Values → validation Mgen (gap to optimum) |
| --- | --- |
| γ | 0.3 → 62.4% (0.230) · **0.5 → 61.2% (0.254)** · 0.7 → 61.1% (0.250) · 0.9 → 60.9% (0.318) · 0.99 → **53.3% (0.532)** |
| λ | 0 → 59.4% (0.237) · 1 → 61.8% (0.244) · 2 → 59.9% (0.253) · **4 → 61.2% (0.254)** · 8 → 63.9% (0.236) |
| Elite share | 0.1 → 62.3% (0.213) · **0.25 → 61.2% (0.254)** · 0.5 → 61.5% (0.240) |
| Learning rate | 1 × 10⁻⁴ → 59.8% (0.270) · **3 × 10⁻⁴ → 61.2% (0.254)** · 1 × 10⁻³ → 61.5% (0.251) |
| chord_tol / overlap_tol | 0.02 / 0.03 s → 62.4% (0.246) · **0.03 / 0.05 → 61.2% (0.254)** · 0.05 / 0.08 → 61.8% (0.249) |
| v_max percentile | 90 → 61.9% (0.232) · **95 → 61.2% (0.254)** · 99 → 61.6% (0.233) |

- **γ is the only setting that matters a lot.** Everything from 0.3 to 0.9 lands within 1.5
  points, but γ 0.99 collapses to 53.3% with twice the gap. This confirms the γ fix
  (sections 2–3) under a different budget and a fresh seed. Most of a move's cost depends on the
  last few events, so a short horizon is enough.
- **Everything else is flat:** within about ±1.5 points of the centre, which is the single-seed
  noise level (section 3 found λ 2 and λ 4 within noise). A slightly lower learning rate
  (1 × 10⁻⁴) is the only other setting that is a little worse at this budget.
- **λ 8** gives the highest validation Mgen (63.9%), but the λ curve is not monotonic
  (1 → 61.8%, 2 → 59.9%), so on one seed this is within noise. Confirming it needs several seeds.
  λ = 0 is the lowest, consistent with the ablation.
- The method is therefore robust to its settings except the discount. The defaults are reasonable,
  and none of the alternatives is clearly better on this evidence.

## 11. RL benchmarks on the final setup

The benchmark algorithms of README §C.9.5, retrained on exactly the v2 setup: γ 0.5, λ 4,
1M steps, no early stopping, 3 seeds. Tabular Q-learning uses the rule reward only, with one Q-table
per test piece (500 episodes each). Run with `python experiments/run_v2_bench.py --jobs 4`; results
in `results/twohand_final/benchmarks_final.json`, figure `report/figures/fig_benchmarks.png`. The
first benchmarks (`runs/dqn_*`, `ppo_*`, `qlearn`; γ 0.99, λ 0.5) are superseded.

| Method | Test Mgen | d_rel ↓ | Gap to optimum ↓ | Train min / run | Params | Wilcoxon vs R3 (Mgen / d_rel) |
| --- | --- | --- | --- | --- | --- | --- |
| **Ours: v2 R3** (masked Double DQN, dueling, 3-step, elite replay) | 61.7% ± 0.3 | 1.17 | 0.33 | 58 | 91k | – |
| DQN (masked; no Double, no dueling, n = 1, no elite) | **62.3% ± 0.6** | **1.13** | **0.30** | 8 | 91k | p = 0.29 / **p < 0.001, better** |
| MaskablePPO (sb3-contrib) | 59.9% ± 0.8 | 1.23 | 0.40 | 7 | 175k | **p = 0.016, worse** / **p = 0.003, worse** |
| Tabular Q-learning (per test piece) | 48.7% | 1.80 | 0.99 | 3 (all pieces) | – | **p < 0.001, worse** / **p < 0.001, worse** |

Mgen is mean ± std over seeds; d_rel and gap are pooled means. The Wilcoxon tests are over the 30
test pieces (per-piece values averaged over seeds).

- **Value-based deep RL suits this task.** Both DQN variants beat MaskablePPO (−1.8 points of Mgen
  for PPO, significant) and are far ahead of tabular Q-learning. Q-learning cannot generalise
  between states and, even trained on each test piece, ends about twice as far from the optimum.
- **The plain DQN is as good as R3, and slightly easier to play** (d_rel 1.13 vs 1.17, significant),
  while training about 7× faster. This agrees with the ablations (section 9): with the v2 recipe,
  Double DQN, dueling, n-step returns and elite replay each make no significant difference. **The
  gains come from the problem formulation, not from the DQN variant.** That formulation is:
  - γ 0.5 (sections 2–3);
  - finger-set actions with feasibility masks;
  - the relative state with look-ahead (−3.9 points without it);
  - the `parncutt12` rules (−4.8 points with `balliauw15`).
- The reported model stays v2 R3. All fine-tuning, robustness and web app results use it, and
  its Mgen is not significantly different from DQN's. DQN is the cheaper equivalent and the natural
  base for future work.
