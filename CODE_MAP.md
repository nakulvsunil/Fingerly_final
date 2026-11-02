# Code map: which file does what

Fingerly has three parts (see `README.md`):

- **Part A:** reproduces Iman & Ahn (2024): right hand, four pieces.
- **Part B:** one hand at a time on the whole of PIG.
- **Part C:** the current project: both hands, chords, one RL policy for unseen pieces.

All final results come from **Part C with the v2 recipe**: γ 0.5, λ 4, no early stopping.

Several top-level scripts serve both Part B and Part C. With `--mode lh|given|assign` they run
Part C; without it they run Part B. This applies to `train.py`, `evaluate.py`, `plot.py` and
`visualize.py`.

## The final pipeline at a glance

```
PIG data ──> fingerly/twohand/prepare.py   (notes -> events, chords, segments, splits)
         ──> fingerly/twohand/env.py       (the RL environment: state, masked actions, reward)
                 uses actions.py, features.py, rules.py, costs.py
         ──> train.py --mode given         (masked Double DQN agent, fingerly/dqn.py)
                 run for all v2 methods by experiments/run_v2.py
         ──> experiments/finetune_best.py  (optional per-piece fine-tuning: the 63.9% result)
         ──> evaluate.py --mode given      (all metrics, statistics, robustness; fingerly/metrics.py)
         ──> plot.py                       (figures and tables)
         ──> webapp/                       (upload a score, see the agent's fingering)
```

M0 (`search.py`, `fingerly/twohand/search.py`) and S1/S2 (`train_bc.py`, `fingerly/baselines.py`)
are **measuring sticks only**. They are never the reported answer, and the agent never uses M0
during training.

---

## Part C: core library (`fingerly/twohand/`)

| File | What it does |
| --- | --- |
| `prepare.py` | Data pipeline. It turns PIG notes into **events**: a single note, or a chord played by one hand. It handles legato overlaps and held notes, merges both hands in onset order, cuts the result into segments, and makes the train/validation/test split. |
| `env.py` | The **RL environment**, with modes 2a (`lh`, left hand alone), 2b (`given`, both hands, hand given) and 2c (`assign`, the agent also picks the hand). It builds the state, applies the action masks and computes the reward: −(difficulty + time-leap + crossing) + λ·(match with a pianist). `SegmentPool` serves training and validation segments. |
| `actions.py` | **Finger-set actions.** There are 31 finger sets per hand (every set of 1–5 fingers), or 62 when the agent also chooses the hand. Chord notes get their fingers in pitch order. |
| `features.py` | **State features:** 67 relative numbers covering the current event, a 4-event look-ahead, each hand's recent keys and fingers, and chord size and span. |
| `rules.py` | **Reward rules.** Two cost models: `parncutt12` (used for training) and `balliauw15` (the 2025 paper's rules, used for comparison). The left hand is handled by mirroring the keyboard. |
| `costs.py` | **Precomputed cost tables.** Each event's cost depends only on the last three finger sets, so the costs are looked up from tables instead of recomputed. This is where the training speed comes from. |
| `search.py` | **M0, the optimum reference.** It finds the exact lowest-cost fingering by dynamic programming (DP), or by beam search when the agent chooses hands. It is used for regret, gap and success rate, never for training. |
| `robust.py` | **Robustness perturbations** for evaluation: tempo, transposition, timing jitter, hand size, composer era and a synthetic stress set. |

## Shared library (`fingerly/`)

| File | What it does |
| --- | --- |
| `dqn.py` | **The RL agent.** DQN / Double DQN in PyTorch with action masking, a dueling head, n-step returns, a replay buffer, elite replay and demonstrations. It holds the training loop, checkpoints and validation used by every RL method in Part B and Part C. |
| `metrics.py` | **Evaluation metrics:** the PIG match rates Mgen, Mhigh, Msoft and Mrec (Nakamura et al., 2020), d_rel, success rate, regret, convergence and sample efficiency. Statistics include bootstrap and Wilson intervals, interquartile mean (IQM), Wilcoxon tests and seed stability. |
| `baselines.py` | **Non-RL baselines:** random-valid, greedy, the optimal-cost DP (Part B), and the HMM baseline S2 (`HMMSets`, Part C). |
| `qlearn.py` | **Tabular Q-learning benchmark** (Part C, §C.9.5), one Q-table per test piece. |
| `synth.py` | **Synthetic exercises:** scales, arpeggios, broken thirds and random melodies, used for 2c's curriculum and for extra practice. |
| `pig.py` | Reads PIG fingering files. It also cuts one-hand monophonic passages for Part B. |
| `cost.py` | Part B's one-hand effort cost model. |
| `env.py` | Part B's one-hand Gymnasium environment. |
| `data.py` | Part B: turns command-line options into passages. |
| `export.py` | Exports a Part B fingering as JSON for the pygame player. |
| `fake_pig.py` | Writes a fake PIG-format dataset, so the pipeline can be tested without the real data. |

## Part A: paper reproduction (`fingerly/paper/`, `reproduce.py`)

| File | What it does |
| --- | --- |
| `reproduce.py` | Entry point for Part A: build the pieces, check the reward, train all agents and write the report. |
| `fingerly/paper/agents.py` | The paper's four agents: DQN, Double DQN, REINFORCE with a baseline, and A2C. |
| `fingerly/paper/env.py` | The paper's environment: one-hot state, no action mask. |
| `fingerly/paper/rules.py` | The paper's 12 difficulty rules (after Parncutt et al.). |
| `fingerly/paper/dp.py` | Exact lowest-difficulty fingering by DP, used as a check. |
| `fingerly/paper/pieces.py` | The paper's four pieces: Beyer No. 12 plus three PIG pieces. |

---

## Top-level scripts

| File | What it does |
| --- | --- |
| `train.py` | **Trains an RL agent.** With `--mode`, it trains the Part C methods R1, R2, R3, A1–A3 and 2c, plus DQN and Q-learning via `--algo`. Defaults are the v2 recipe (γ 0.5, no early stopping). Without `--mode`, it trains Part B's one-hand agent. |
| `train_bc.py` | **S1**, the copy-only baseline: the same network, trained by supervised learning to copy pianists. Not RL. |
| `train_ppo.py` | **MaskablePPO benchmark** (sb3-contrib), with the same features and masks. |
| `finetune.py` | **R4 (original):** fine-tunes a trained agent on each test piece with the rule reward only, and keeps the last fingering. |
| `search.py` | Runs **M0** on a split, writing `results/twohand/m0_*.json`. With `--brute-check`, it checks the beam search against brute force. |
| `evaluate.py` | **Evaluates** checkpoints, fine-tuned fingerings and baselines with every metric. Options cover the cost models, M0 reference, seen vs unseen, Wilcoxon, bootstrap, compute and robustness. Results are cached in `cache/twohand/eval`. |
| `plot.py` | **Figures and tables:** learning curves, success, regret, seen vs unseen, seeds, the λ curve, fine-tuning (`--r4`, `--r4-runs`), sensitivity, result tables and excerpts. |
| `check_reward.py` | **Reward checks without training:** the 2025 paper's Table A1, mirroring, chord masks and v_max. |
| `prepare_twohand.py` | Writes the data pipeline's **coverage report**: split sizes and overlap histograms. |
| `run_twohand.py` | Runs the whole **original Part C experiment grid** (E0–E12), with the first recipe at γ 0.99. Kept for the record; v2 uses `experiments/`. |
| `predict.py` | Part B: fingers a PIG file with a one-hand agent. |
| `visualize.py` | Plays a fingering on the **pygame piano**. Part C uses `--mode given\|assign --ckpt ...`, and `--json` saves the fingering. |
| `run_seeds.sh` | Part B: trains, evaluates and plots three seeds. |
| `conftest.py` | Lets pytest import the package from the repo root. |

## Experiments (`experiments/`): v2 and the analyses behind it

| File | What it does |
| --- | --- |
| `run_v2.py` | **Trains all final v2 agents**: R1, R2, R3, A2 and 2c, seeds 0–2, written to `runs/v2_*`. |
| `run_v2_ablsens.py` | **Ablations and sensitivity on the v2 setup**, written to `runs/v2_abl_*` and `runs/v2_sens_*`. It then evaluates them into `results/twohand_final/`. |
| `run_v2_bench.py` | **Benchmarks on the v2 setup:** DQN, MaskablePPO and Q-learning, written to `results/twohand_final/benchmarks_final.json` (`RESULTS.md` §11). |
| `plot_ablsens.py` | Report figures for the ablations, sensitivity and benchmarks (`report/figures/fig_ablation.png`, `fig_sensitivity.png`, `fig_benchmarks.png`). |
| `finetune_best.py` | **Per-piece fine-tuning that keeps the best fingering found.** This gives the 63.9% result, and the web app's Refine uses the same method. |
| `train_variant.py` | Wraps `train.py` with one extra option, `--reward-scale` (used in the diagnosis experiments). |
| `check_fit.py` | Underfitting check: waste per note on training pieces, test pieces and beginner tunes. |
| `ensemble.py` | Seed ensemble that averages Q over checkpoints. Tried and rejected. |
| `rule_audit.py` | Shows which reward rules pianists break most compared with M0. |
| `fit_rule_weights.py` | Refits the reward rule weights against the pianists. Tried and not adopted. |
| `RESULTS.md` | **The results write-up:** the diagnosis, the γ fix, v2 results, the 2025 comparison, robustness, ablations, sensitivity and benchmarks. |

## Web app (`webapp/`)

| File | What it does |
| --- | --- |
| `server.py` | The web server (standard library only). Run `python webapp/server.py --open`. |
| `agent_runner.py` | **Fingers an uploaded score with the final agent** (`runs/v2_r3_s0`). Refine fine-tunes the three v2 R3 seeds on the piece and keeps the best result. |
| `score_io.py` | Reads MusicXML (`.musicxml`, `.xml`, `.mxl`), MIDI and PIG files into notes the agent can finger. |
| `static/index.html`, `app.js`, `style.css` | The page: upload, score drawing and the piano playback with fingers shown. |
| `examples/make_examples.py` | Writes the example scores (Ode to Joy, Twinkle Twinkle). |
| `beginner_data.py` | Beginner-style tunes, for training and for the held-out check. |
| `train_beginner.py`, `check_beginner.py` | An earlier "beginner model" experiment from the old A2 agent. Superseded by v2 and not used by the app. |
| `test_webapp.py` | Tests for the score readers and the fingering endpoint. |

## Piano player (`visual/piano/`)

| File | What it does |
| --- | --- |
| `fingering_player.py` | Replays an exported fingering JSON on the pygame piano. |
| `main.py`, `hand.py`, `piano_lists.py` | The pygame piano itself: keys, sounds and the drawn hand. |

## Tests (`tests/`)

| File | What it covers |
| --- | --- |
| `test_twohand.py` | Part C: data pipeline, actions, cost models, environments, M0. |
| `test_dqn.py` | The DQN agent, including n-step returns and a short training run. |
| `test_fingerly.py` | Part B: PIG reading, cost, environment, baselines, metrics. |
| `test_paper.py` | Part A: reward, DP, environment, Mrec. |

Run everything with `pytest -q`.

---

## Where the outputs are

| Folder | Contents |
| --- | --- |
| `runs/v2_*` | Final trained agents (`best.pt`). Only these are in git. |
| `results/twohand_v2/` | v2 main results (`main_v2.json`), fine-tuning results and the diagnosis tables. |
| `results/twohand_final/` | Final-setup robustness, ablations, sensitivity, figures, tables and fingerings. |
| `results/twohand/` | The first Part C run (γ 0.99). The M0, coverage and reward-check files here are still valid; the rest is superseded. |
| `report/figures/` | Figures for the report. |
