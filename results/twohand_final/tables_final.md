# Part C results (README §C.11.10)

## Final performance on the 30 test pieces

Mean ± std over seeds. Return = rule reward per event (no bonus). SR = segments with no infeasible transition and gap to M0 ≤ 10% (pooled over seeds, Wilson 95% interval). Rates in %.

| Method | Mode | Seeds | Return / event | Median | SR (95% CI) | N* (gap ≤ 15%) | Mgen | Mhigh | Msoft | Mrec | Hand acc. | d_rel | Diff./note p12 | Gap to M0 | Infeasible | Large stretch | Time-leap | Crossing | Hand switch | Weak finger | Thumb on black |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s1 | given | 3 | -12.634 ± 0.131 | -12.657 | 0.6 (0.1–3.2) | – | 61.8 ± 0.4 | 62.4 ± 0.4 | 65.5 ± 0.4 | 64.8 ± 0.4 | 100.0 | 1.188 ± 0.008 | 9.23 ± 0.01 | 0.442 ± 0.002 | 0.1 ± 0.0 | 19.2 ± 0.1 | 12.0 ± 0.1 | 3.4 ± 0.1 | 52.1 | 30.6 ± 1.6 | 10.0 ± 0.2 |
| v2_2c | assign | 3 | -12.637 ± 0.298 | -12.543 | 0.0 (-0.0–2.2) | –, –, – | 57.7 ± 0.7 | 58.4 ± 0.7 | 61.1 ± 0.7 | 60.5 ± 0.6 | 95.3 ± 1.3 | 1.221 ± 0.011 | 8.88 ± 0.06 | 0.479 ± 0.052 | 0.2 ± 0.0 | 15.6 ± 0.6 | 11.5 ± 0.2 | 5.5 ± 1.6 | 53.2 ± 0.1 | 32.9 ± 1.6 | 11.6 ± 0.4 |
| v2_a2 | given | 3 | -12.173 ± 0.041 | -12.163 | 1.8 (0.6–5.0) | –, –, – | 61.0 ± 0.4 | 61.8 ± 0.4 | 64.8 ± 0.4 | 64.1 ± 0.4 | 100.0 | 1.194 ± 0.002 | 8.92 ± 0.03 | 0.392 ± 0.004 | 0.2 ± 0.0 | 16.8 ± 0.4 | 11.7 ± 0.1 | 3.3 ± 0.1 | 52.1 | 32.0 ± 0.4 | 10.6 ± 0.4 |
| v2_r1 | given | 3 | -11.674 ± 0.096 | -11.641 | 4.7 (2.4–9.0) | –, –, – | 59.6 ± 0.8 | 60.3 ± 0.8 | 63.0 ± 0.7 | 62.4 ± 0.8 | 100.0 | 1.184 ± 0.011 | 8.63 ± 0.05 | 0.346 ± 0.008 | 0.2 ± 0.0 | 14.9 ± 0.2 | 11.1 ± 0.2 | 3.4 ± 0.2 | 52.1 | 34.3 ± 0.6 | 11.5 ± 0.3 |
| v2_r2 | given | 3 | -11.625 ± 0.219 | -11.634 | 2.3 (0.9–5.9) | –, –, – | 62.2 ± 0.3 | 62.8 ± 0.4 | 65.9 ± 0.4 | 65.1 ± 0.4 | 100.0 | 1.166 ± 0.020 | 8.55 ± 0.13 | 0.332 ± 0.021 | 0.2 ± 0.0 | 14.7 ± 0.6 | 11.3 ± 0.2 | 3.4 ± 0.1 | 52.1 | 33.4 ± 0.5 | 11.2 ± 0.3 |
| v2_r3 | given | 3 | -11.636 ± 0.081 | -11.655 | 1.2 (0.3–4.2) | –, –, – | 61.7 ± 0.3 | 62.5 ± 0.4 | 65.4 ± 0.3 | 64.7 ± 0.3 | 100.0 | 1.166 ± 0.010 | 8.55 ± 0.07 | 0.333 ± 0.010 | 0.2 ± 0.0 | 14.8 ± 0.5 | 11.0 ± 0.3 | 3.5 ± 0.2 | 52.1 | 32.9 ± 1.3 | 11.1 ± 0.2 |
| random-valid | given | 1 | -25.103 | -25.103 | 0.0 | – | 36.7 | 36.9 | 39.4 | 38.6 | 100.0 | 2.599 | 18.30 | 1.891 | 0.3 | 28.8 | 23.5 | 8.6 | 52.1 | 37.3 | 11.0 |
| greedy | given | 1 | -11.313 | -11.313 | 8.8 | – | 57.3 | 58.1 | 60.9 | 60.4 | 100.0 | 1.198 | 8.49 | 0.329 | 0.3 | 12.0 | 12.1 | 4.5 | 52.1 | 35.3 | 11.1 |
| S2 (HMM) | given | 1 | -13.652 | -13.652 | 0.0 | – | 60.9 | 61.9 | 64.8 | 64.1 | 100.0 | 1.197 | 9.52 | 0.481 | 3.8 | 17.2 | 11.8 | 3.7 | 52.1 | 29.9 | 11.5 |
| M0 (optimum) | given | 1 | -8.741 | -8.741 | 84.2 | – | 68.1 | 68.8 | 72.1 | 71.4 | 100.0 | 0.870 | 6.39 | 0.000 | 0.3 | 10.7 | 10.3 | 3.0 | 52.1 | 28.6 | 11.2 |
| Human (pianists) | given | 1 | – | nan | – | – | 75.3 | – | – | – | 100.0 | 1.000 | – | – | – | 15.6 | 9.0 | 2.7 | 53.6 | 29.6 | 9.1 |
| v2_r4best | given | 3 | -10.300 ± 0.052 | -10.316 | 18.7 (13.6–25.2) | – | 63.1 ± 0.1 | 63.8 ± 0.2 | 66.9 ± 0.2 | 66.3 ± 0.1 | 100.0 | 1.042 ± 0.001 | 7.59 ± 0.02 | 0.185 ± 0.003 | 0.0 | 12.6 ± 0.2 | 10.6 ± 0.1 | 3.6 ± 0.2 | 52.1 | 34.2 ± 0.1 | 10.9 ± 0.1 |
| v2_r4bestof3 | given | 1 | -10.175 | -10.175 | 21.1 (12.5–33.3) | – | 63.9 | 64.7 | 67.8 | 67.1 | 100.0 | 1.029 | 7.51 | 0.172 | 0.0 | 12.4 | 10.5 | 3.5 | 52.1 | 33.7 | 11.0 |

Per hand and singles vs chords (Mgen, %):

| Method | Right | Left | Single notes | Chords | Chord exact match | Unreachable chords | Sequence breakdowns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s1 | 57.1 ± 0.7 | 66.2 ± 1.0 | 54.1 ± 0.2 | 72.3 ± 1.3 | 56.0 ± 1.1 | 0.0 ± 0.0 | 3.1 ± 0.3 |
| v2_2c | 52.9 ± 0.7 | 61.9 ± 0.5 | 45.6 ± 0.9 | 71.9 ± 1.1 | 53.8 ± 1.7 | 0.0 ± 0.0 | 2.5 ± 0.1 |
| v2_a2 | 55.7 ± 1.2 | 65.8 ± 0.1 | 52.6 ± 0.7 | 71.8 ± 0.9 | 52.5 ± 1.8 | 0.0 ± 0.0 | 2.8 ± 0.1 |
| v2_r1 | 54.6 ± 0.8 | 63.8 ± 0.8 | 50.5 ± 0.7 | 70.3 ± 0.1 | 49.9 ± 1.0 | 0.0 ± 0.0 | 2.6 ± 0.1 |
| v2_r2 | 57.3 ± 0.6 | 66.5 ± 0.8 | 52.8 ± 0.3 | 72.7 ± 2.1 | 53.5 ± 3.4 | 0.0 ± 0.0 | 2.7 ± 0.0 |
| v2_r3 | 56.8 ± 0.4 | 65.8 ± 0.8 | 53.1 ± 0.7 | 70.3 ± 0.2 | 49.6 ± 1.5 | 0.0 ± 0.0 | 2.7 ± 0.1 |
| random-valid | 35.4 | 37.9 | 26.6 | 50.1 | 22.1 | 0.0 | 2.6 |
| greedy | 54.8 | 60.8 | 47.7 | 70.2 | 51.7 | 0.0 | 2.9 |
| S2 (HMM) | 56.2 | 64.7 | 57.8 | 61.7 | 30.7 | 0.0 | 3.4 |
| M0 (optimum) | 64.2 | 71.5 | 61.4 | 75.7 | 61.6 | 0.0 | 2.4 |
| Human (pianists) | – | – | – | – | – | – | – |
| v2_r4best | 58.1 ± 0.8 | 67.1 ± 0.7 | 55.5 ± 0.7 | 70.8 ± 0.6 | 52.3 ± 1.3 | 0.0 ± 0.0 | 2.6 ± 0.0 |
| v2_r4bestof3 | 58.3 | 68.2 | 56.8 | 70.8 | 52.7 | 0.0 | 2.6 |

## Comparison with Iman & Ahn (2025), README §C.11.4

Their numbers are fitted to each test piece; ours are on unseen pieces. d_rel = difficulty ÷ the pianists' difficulty, `balliauw15`.

| Method | d_rel | Mgen | Mhigh | Msoft | Mrec |
| --- | --- | --- | --- | --- | --- |
| 2025 Uniform | 0.81 | 0.62 | 0.67 | 0.75 | 0.70 |
| 2025 EER | 0.81 | 0.61 | 0.66 | 0.75 | 0.69 |
| 2025 PER | 0.84 | 0.59 | 0.67 | 0.75 | 0.69 |
| 2025 FHMM1 | 1.03 | 0.67 | 0.70 | 0.80 | 0.75 |
| 2025 FHMM2 | 0.97 | 0.70 | 0.74 | 0.85 | 0.80 |
| 2025 FHMM3 | 0.96 | 0.68 | 0.76 | 0.86 | 0.82 |
| 2025 Human | 1.00 | 0.73 | 0.75 | 0.79 | 0.77 |
| s1 | 1.19 | 0.62 | 0.62 | 0.65 | 0.65 |
| v2_2c | 1.22 | 0.58 | 0.58 | 0.61 | 0.61 |
| v2_a2 | 1.19 | 0.61 | 0.62 | 0.65 | 0.64 |
| v2_r1 | 1.18 | 0.60 | 0.60 | 0.63 | 0.62 |
| v2_r2 | 1.17 | 0.62 | 0.63 | 0.66 | 0.65 |
| v2_r3 | 1.17 | 0.62 | 0.63 | 0.65 | 0.65 |
| random-valid | 2.60 | 0.37 | 0.37 | 0.39 | 0.39 |
| greedy | 1.20 | 0.57 | 0.58 | 0.61 | 0.60 |
| S2 (HMM) | 1.20 | 0.61 | 0.62 | 0.65 | 0.64 |
| M0 (optimum) | 0.87 | 0.68 | 0.69 | 0.72 | 0.71 |
| Human (pianists) | 1.00 | 0.75 | nan | nan | nan |
| v2_r4best | 1.04 | 0.63 | 0.64 | 0.67 | 0.66 |
| v2_r4bestof3 | 1.03 | 0.64 | 0.65 | 0.68 | 0.67 |

## RL-specific metrics (validation logs)

AUC = area under the validation return curve to 1M steps, scaled so random-valid = 0 and M0 = 1.

| Method | AUC (mean) | Return at 100k | 250k | 500k | 1M | N* Mgen ≥ 0.60 | Generalisation gap (return / Mgen / d_rel) | IQM Mgen [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v2_2c | 0.835 | -21.216 | -20.989 | -19.765 | -19.606 | –, –, – | -2.094 / 0.009 / -0.034 | 0.590 [0.583, 0.597] |
| v2_a2 | 0.776 | -18.785 | -18.296 | -18.182 | -18.077 | 400k, 100k, 725k | -2.206 / 0.078 / -0.018 | 0.611 [0.606, 0.615] |
| v2_r1 | 0.796 | -19.257 | -17.924 | -17.555 | -17.522 | – | -2.686 / -0.013 / 0.000 | 0.599 [0.591, 0.606] |
| v2_r2 | 0.806 | -19.002 | -17.674 | -17.289 | -17.243 | 250k, 175k, 200k | -2.716 / -0.006 / 0.025 | 0.630 [0.624, 0.636] |
| v2_r3 | 0.801 | -19.390 | -17.728 | -17.410 | -17.302 | 175k, 175k, 325k | -2.514 / 0.006 / 0.004 | 0.624 [0.618, 0.630] |

## Stability across seeds (final test scores)

| Method | Seeds | Return: std / CV / min–max | Mgen: std / CV / min–max | d_rel: std / CV / min–max |
| --- | --- | --- | --- | --- |
| s1 | 3 | 0.1314 / 0.010 / -12.752–-12.492 | 0.0037 / 0.006 / 0.613–0.620 | 0.0078 / 0.007 / 1.179–1.193 |
| v2_2c | 3 | 0.2985 / 0.024 / -12.971–-12.397 | 0.0066 / 0.011 / 0.571–0.584 | 0.0109 / 0.009 / 1.209–1.230 |
| v2_a2 | 3 | 0.0409 / 0.003 / -12.218–-12.139 | 0.0044 / 0.007 / 0.605–0.614 | 0.0020 / 0.002 / 1.192–1.196 |
| v2_r1 | 3 | 0.0959 / 0.008 / -11.782–-11.598 | 0.0078 / 0.013 / 0.587–0.603 | 0.0111 / 0.009 / 1.174–1.196 |
| v2_r2 | 3 | 0.2189 / 0.019 / -11.840–-11.402 | 0.0031 / 0.005 / 0.620–0.625 | 0.0201 / 0.017 / 1.144–1.185 |
| v2_r3 | 3 | 0.0807 / 0.007 / -11.705–-11.547 | 0.0031 / 0.005 / 0.614–0.620 | 0.0102 / 0.009 / 1.155–1.175 |
| v2_r4best | 3 | 0.0516 / 0.005 / -10.342–-10.242 | 0.0014 / 0.002 / 0.630–0.632 | 0.0006 / 0.001 / 1.042–1.043 |
| v2_r4bestof3 | 1 | 0.0000 / 0.000 / -10.175–-10.175 | 0.0000 / 0.000 / 0.639–0.639 | 0.0000 / 0.000 / 1.029–1.029 |

## Compute

Hardware: i7-12650H, RTX 3050 laptop GPU. The 2025 paper used about 45 GPU-days.

| Method | Device | Train min / run | CPU-hours (all seeds) | Steps/s | Params | Peak RAM (MB) | Inference ms/note | s/piece | Energy Wh (45 W est.) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s1 | None | 0.4 | 0.02 | nan | 91424 | nan | 0.075 | 0.03 | 0.8 |
| v2_2c | cuda | 16.7 | 0.84 | 1530 | 99391 | 1994 | 0.119 | 0.05 | 37.7 |
| v2_a2 | cuda | 13.3 | 0.67 | 1241 | 91424 | 1848 | 0.092 | 0.04 | 29.9 |
| v2_r1 | cuda | 13.5 | 0.67 | 1252 | 91424 | 1843 | 0.076 | 0.03 | 30.3 |
| v2_r2 | cuda | 57.3 | 2.87 | 499 | 91424 | 1844 | 0.074 | 0.03 | 129.0 |
| v2_r3 | cuda | 57.8 | 2.89 | 508 | 91424 | 1948 | 0.090 | 0.04 | 130.1 |
| v2_r4best | – | – | – | – | – | – | 0.020 | 0.01 | – |
| v2_r4bestof3 | – | – | – | – | – | – | 0.022 | 0.01 | – |

Total training time of the evaluated runs: 8.0 hours.

## Robustness (frozen policy): degradation Δ = clean − perturbed

Under transposition and hand size, Mgen still uses the original annotations, although a pianist might finger the changed passage differently.

| Method | Perturbation | Δ d_rel | Δ Mgen | Δ SR | Δ infeasible | d_rel | Mgen | SR | infeasible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s1 | tempo=0.75 | +0.002 | +0.003 | +0.018 | -0.000 | 1.189 | 0.618 | 0.000 | 0.002 |
| s1 | tempo=1.5 | +0.001 | +0.000 | +0.000 | -0.000 | 1.189 | 0.620 | 0.018 | 0.002 |
| s1 | transpose=-5 | +0.001 | +0.005 | +0.018 | -0.000 | 1.190 | 0.615 | 0.000 | 0.002 |
| s1 | transpose=-2 | +0.002 | +0.021 | +0.000 | -0.000 | 1.189 | 0.599 | 0.018 | 0.002 |
| s1 | transpose=-1 | +0.008 | +0.036 | +0.018 | -0.000 | 1.183 | 0.584 | 0.000 | 0.002 |
| s1 | transpose=1 | -0.001 | +0.035 | +0.018 | -0.000 | 1.191 | 0.585 | 0.000 | 0.002 |
| s1 | transpose=2 | -0.003 | +0.014 | +0.018 | -0.000 | 1.193 | 0.606 | 0.000 | 0.002 |
| s1 | transpose=5 | +0.002 | +0.006 | +0.018 | +0.000 | 1.188 | 0.615 | 0.000 | 0.002 |
| s1 | jitter=0.01 | -0.054 | +0.015 | +0.018 | -0.001 | 1.244 | 0.605 | 0.000 | 0.002 |
| s1 | jitter=0.02 | -0.272 | +0.037 | +0.001 | -0.007 | 1.462 | 0.584 | 0.017 | 0.009 |
| s1 | span=0.85 | -0.114 | +0.013 | -0.053 | -0.007 | 1.305 | 0.607 | 0.070 | 0.008 |
| s1 | span=1.15 | -0.046 | +0.018 | +0.018 | +0.000 | 1.237 | 0.602 | 0.000 | 0.001 |
| s1 | stress | – | – | -0.107 | +0.002 | – | – | 0.125 | 0.000 |

s1, by composer era (clean test results):

| Era | Pieces | Mgen | d_rel |
| --- | --- | --- | --- |
| Baroque | 3 | 0.514 | 1.415 |
| Classical | 8 | 0.620 | 1.270 |
| Romantic | 13 | 0.657 | 1.199 |
| Late Romantic / 20th c. | 6 | 0.593 | 1.829 |

| v2_r2 | tempo=0.75 | -0.001 | +0.003 | +0.018 | +0.000 | 1.169 | 0.616 | 0.018 | 0.002 |
| v2_r2 | tempo=1.5 | -0.012 | +0.005 | +0.018 | -0.001 | 1.179 | 0.614 | 0.018 | 0.003 |
| v2_r2 | transpose=-5 | +0.003 | +0.003 | +0.000 | +0.000 | 1.165 | 0.617 | 0.035 | 0.002 |
| v2_r2 | transpose=-2 | -0.001 | +0.007 | +0.018 | +0.000 | 1.169 | 0.613 | 0.018 | 0.002 |
| v2_r2 | transpose=-1 | -0.032 | +0.027 | +0.018 | +0.000 | 1.200 | 0.593 | 0.018 | 0.002 |
| v2_r2 | transpose=1 | -0.034 | +0.023 | +0.035 | +0.000 | 1.202 | 0.597 | 0.000 | 0.002 |
| v2_r2 | transpose=2 | +0.008 | +0.001 | +0.000 | +0.000 | 1.159 | 0.618 | 0.035 | 0.002 |
| v2_r2 | transpose=5 | -0.020 | +0.004 | +0.035 | +0.000 | 1.188 | 0.616 | 0.000 | 0.002 |
| v2_r2 | jitter=0.01 | -0.072 | +0.003 | +0.035 | -0.001 | 1.239 | 0.616 | 0.000 | 0.003 |
| v2_r2 | jitter=0.02 | -0.245 | +0.032 | +0.018 | -0.007 | 1.413 | 0.588 | 0.017 | 0.009 |
| v2_r2 | span=0.85 | -0.112 | -0.000 | +0.000 | -0.006 | 1.280 | 0.620 | 0.035 | 0.008 |
| v2_r2 | span=1.15 | -0.036 | +0.011 | +0.018 | +0.000 | 1.204 | 0.609 | 0.018 | 0.002 |
| v2_r2 | stress | – | – | -0.140 | +0.002 | – | – | 0.175 | 0.000 |

v2_r2, by composer era (clean test results):

| Era | Pieces | Mgen | d_rel |
| --- | --- | --- | --- |
| Baroque | 3 | 0.590 | 1.489 |
| Classical | 8 | 0.575 | 1.237 |
| Romantic | 13 | 0.656 | 1.322 |
| Late Romantic / 20th c. | 6 | 0.615 | 1.590 |

| v2_r3 | tempo=0.75 | -0.000 | -0.003 | +0.000 | -0.000 | 1.155 | 0.621 | 0.018 | 0.002 |
| v2_r3 | tempo=1.5 | -0.007 | -0.001 | +0.000 | -0.001 | 1.162 | 0.619 | 0.018 | 0.003 |
| v2_r3 | transpose=-5 | +0.008 | -0.005 | -0.018 | +0.000 | 1.147 | 0.623 | 0.035 | 0.002 |
| v2_r3 | transpose=-2 | -0.003 | +0.007 | +0.000 | -0.000 | 1.158 | 0.611 | 0.018 | 0.002 |
| v2_r3 | transpose=-1 | -0.003 | +0.034 | +0.000 | -0.000 | 1.158 | 0.584 | 0.018 | 0.002 |
| v2_r3 | transpose=1 | -0.004 | +0.027 | +0.000 | -0.000 | 1.159 | 0.591 | 0.018 | 0.002 |
| v2_r3 | transpose=2 | +0.006 | +0.001 | +0.000 | -0.000 | 1.149 | 0.617 | 0.018 | 0.002 |
| v2_r3 | transpose=5 | +0.005 | -0.002 | -0.018 | -0.000 | 1.150 | 0.620 | 0.035 | 0.002 |
| v2_r3 | jitter=0.01 | -0.062 | +0.003 | +0.018 | -0.001 | 1.217 | 0.615 | 0.000 | 0.003 |
| v2_r3 | jitter=0.02 | -0.257 | +0.029 | +0.001 | -0.007 | 1.412 | 0.589 | 0.017 | 0.009 |
| v2_r3 | span=0.85 | -0.121 | +0.004 | -0.088 | -0.006 | 1.276 | 0.614 | 0.105 | 0.008 |
| v2_r3 | span=1.15 | -0.032 | +0.013 | +0.000 | +0.000 | 1.187 | 0.605 | 0.018 | 0.002 |
| v2_r3 | stress | – | – | -0.182 | +0.002 | – | – | 0.200 | 0.000 |

v2_r3, by composer era (clean test results):

| Era | Pieces | Mgen | d_rel |
| --- | --- | --- | --- |
| Baroque | 3 | 0.546 | 1.818 |
| Classical | 8 | 0.564 | 1.240 |
| Romantic | 13 | 0.662 | 1.211 |
| Late Romantic / 20th c. | 6 | 0.631 | 1.572 |


## Wilcoxon signed-rank tests over the test pieces (main methods)

| Metric | A | B | Pieces | mean A | mean B | p | Better |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mgen | M0 (optimum) | S2 (HMM) | 30 | 0.681 | 0.609 | 0.000608* | M0 (optimum) |
| Mgen | M0 (optimum) | greedy | 30 | 0.681 | 0.573 | 8.33e-07* | M0 (optimum) |
| Mgen | M0 (optimum) | random-valid | 30 | 0.681 | 0.367 | 1.86e-09* | M0 (optimum) |
| Mgen | M0 (optimum) | s1 | 30 | 0.681 | 0.618 | 2.37e-05* | M0 (optimum) |
| Mgen | M0 (optimum) | v2_2c | 30 | 0.681 | 0.577 | 2.05e-07* | M0 (optimum) |
| Mgen | M0 (optimum) | v2_a2 | 30 | 0.681 | 0.610 | 7.25e-05* | M0 (optimum) |
| Mgen | M0 (optimum) | v2_r1 | 30 | 0.681 | 0.596 | 2.55e-07* | M0 (optimum) |
| Mgen | M0 (optimum) | v2_r2 | 30 | 0.681 | 0.622 | 5.59e-05* | M0 (optimum) |
| Mgen | M0 (optimum) | v2_r3 | 30 | 0.681 | 0.617 | 4.41e-05* | M0 (optimum) |
| Mgen | S2 (HMM) | greedy | 30 | 0.609 | 0.573 | 0.112 | S2 (HMM) |
| Mgen | S2 (HMM) | random-valid | 30 | 0.609 | 0.367 | 5.59e-09* | S2 (HMM) |
| Mgen | S2 (HMM) | s1 | 30 | 0.609 | 0.618 | 0.49 | s1 |
| Mgen | S2 (HMM) | v2_2c | 30 | 0.609 | 0.577 | 0.262 | S2 (HMM) |
| Mgen | S2 (HMM) | v2_a2 | 30 | 0.609 | 0.610 | 0.808 | v2_a2 |
| Mgen | S2 (HMM) | v2_r1 | 30 | 0.609 | 0.596 | 0.543 | S2 (HMM) |
| Mgen | S2 (HMM) | v2_r2 | 30 | 0.609 | 0.622 | 0.404 | v2_r2 |
| Mgen | S2 (HMM) | v2_r3 | 30 | 0.609 | 0.617 | 0.584 | v2_r3 |
| Mgen | greedy | random-valid | 30 | 0.573 | 0.367 | 3.73e-09* | greedy |
| Mgen | greedy | s1 | 30 | 0.573 | 0.618 | 0.00538* | s1 |
| Mgen | greedy | v2_2c | 30 | 0.573 | 0.577 | 0.641 | v2_2c |
| Mgen | greedy | v2_a2 | 30 | 0.573 | 0.610 | 0.0234* | v2_a2 |
| Mgen | greedy | v2_r1 | 30 | 0.573 | 0.596 | 0.191 | v2_r1 |
| Mgen | greedy | v2_r2 | 30 | 0.573 | 0.622 | 0.00219* | v2_r2 |
| Mgen | greedy | v2_r3 | 30 | 0.573 | 0.617 | 0.00501* | v2_r3 |
| Mgen | random-valid | s1 | 30 | 0.367 | 0.618 | 1.86e-09* | s1 |
| Mgen | random-valid | v2_2c | 30 | 0.367 | 0.577 | 1.86e-09* | v2_2c |
| Mgen | random-valid | v2_a2 | 30 | 0.367 | 0.610 | 1.86e-09* | v2_a2 |
| Mgen | random-valid | v2_r1 | 30 | 0.367 | 0.596 | 1.86e-09* | v2_r1 |
| Mgen | random-valid | v2_r2 | 30 | 0.367 | 0.622 | 1.86e-09* | v2_r2 |
| Mgen | random-valid | v2_r3 | 30 | 0.367 | 0.617 | 1.86e-09* | v2_r3 |
| Mgen | s1 | v2_2c | 30 | 0.618 | 0.577 | 0.000153* | s1 |
| Mgen | s1 | v2_a2 | 30 | 0.618 | 0.610 | 0.393 | s1 |
| Mgen | s1 | v2_r1 | 30 | 0.618 | 0.596 | 0.0197* | s1 |
| Mgen | s1 | v2_r2 | 30 | 0.618 | 0.622 | 0.524 | v2_r2 |
| Mgen | s1 | v2_r3 | 30 | 0.618 | 0.617 | 0.839 | s1 |
| Mgen | v2_2c | v2_a2 | 30 | 0.577 | 0.610 | 0.00073* | v2_a2 |
| Mgen | v2_2c | v2_r1 | 30 | 0.577 | 0.596 | 0.0327* | v2_r1 |
| Mgen | v2_2c | v2_r2 | 30 | 0.577 | 0.622 | 4.66e-08* | v2_r2 |
| Mgen | v2_2c | v2_r3 | 30 | 0.577 | 0.617 | 1.45e-05* | v2_r3 |
| Mgen | v2_a2 | v2_r1 | 30 | 0.610 | 0.596 | 0.0767 | v2_a2 |
| Mgen | v2_a2 | v2_r2 | 30 | 0.610 | 0.622 | 0.0856 | v2_r2 |
| Mgen | v2_a2 | v2_r3 | 30 | 0.610 | 0.617 | 0.221 | v2_r3 |
| Mgen | v2_r1 | v2_r2 | 30 | 0.596 | 0.622 | 3.79e-06* | v2_r2 |
| Mgen | v2_r1 | v2_r3 | 30 | 0.596 | 0.617 | 6.29e-05* | v2_r3 |
| Mgen | v2_r2 | v2_r3 | 30 | 0.622 | 0.617 | 0.158 | v2_r2 |
| d_rel_balliauw15 | M0 (optimum) | S2 (HMM) | 30 | 0.903 | 1.228 | 0.000256* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | greedy | 30 | 0.903 | 1.582 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | random-valid | 30 | 0.903 | 4.367 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | s1 | 30 | 0.903 | 1.355 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | v2_2c | 30 | 0.903 | 1.474 | 5.59e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | v2_a2 | 30 | 0.903 | 1.400 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | v2_r1 | 30 | 0.903 | 1.402 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | v2_r2 | 30 | 0.903 | 1.372 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | M0 (optimum) | v2_r3 | 30 | 0.903 | 1.365 | 1.86e-09* | M0 (optimum) |
| d_rel_balliauw15 | S2 (HMM) | greedy | 30 | 1.228 | 1.582 | 0.516 | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | random-valid | 30 | 1.228 | 4.367 | 1.3e-08* | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | s1 | 30 | 1.228 | 1.355 | 0.477 | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | v2_2c | 30 | 1.228 | 1.474 | 0.271 | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | v2_a2 | 30 | 1.228 | 1.400 | 0.393 | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | v2_r1 | 30 | 1.228 | 1.402 | 0.477 | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | v2_r2 | 30 | 1.228 | 1.372 | 0.503 | S2 (HMM) |
| d_rel_balliauw15 | S2 (HMM) | v2_r3 | 30 | 1.228 | 1.365 | 0.465 | S2 (HMM) |
| d_rel_balliauw15 | greedy | random-valid | 30 | 1.582 | 4.367 | 1.86e-09* | greedy |
| d_rel_balliauw15 | greedy | s1 | 30 | 1.582 | 1.355 | 0.452 | s1 |
| d_rel_balliauw15 | greedy | v2_2c | 30 | 1.582 | 1.474 | 0.968 | v2_2c |
| d_rel_balliauw15 | greedy | v2_a2 | 30 | 1.582 | 1.400 | 0.404 | v2_a2 |
| d_rel_balliauw15 | greedy | v2_r1 | 30 | 1.582 | 1.402 | 0.503 | v2_r1 |
| d_rel_balliauw15 | greedy | v2_r2 | 30 | 1.582 | 1.372 | 0.452 | v2_r2 |
| d_rel_balliauw15 | greedy | v2_r3 | 30 | 1.582 | 1.365 | 0.28 | v2_r3 |
| d_rel_balliauw15 | random-valid | s1 | 30 | 4.367 | 1.355 | 1.86e-09* | s1 |
| d_rel_balliauw15 | random-valid | v2_2c | 30 | 4.367 | 1.474 | 1.86e-09* | v2_2c |
| d_rel_balliauw15 | random-valid | v2_a2 | 30 | 4.367 | 1.400 | 1.86e-09* | v2_a2 |
| d_rel_balliauw15 | random-valid | v2_r1 | 30 | 4.367 | 1.402 | 1.86e-09* | v2_r1 |
| d_rel_balliauw15 | random-valid | v2_r2 | 30 | 4.367 | 1.372 | 1.86e-09* | v2_r2 |
| d_rel_balliauw15 | random-valid | v2_r3 | 30 | 4.367 | 1.365 | 1.86e-09* | v2_r3 |
| d_rel_balliauw15 | s1 | v2_2c | 30 | 1.355 | 1.474 | 0.184 | s1 |
| d_rel_balliauw15 | s1 | v2_a2 | 30 | 1.355 | 1.400 | 0.903 | s1 |
| d_rel_balliauw15 | s1 | v2_r1 | 30 | 1.355 | 1.402 | 0.73 | s1 |
| d_rel_balliauw15 | s1 | v2_r2 | 30 | 1.355 | 1.372 | 0.871 | s1 |
| d_rel_balliauw15 | s1 | v2_r3 | 30 | 1.355 | 1.365 | 0.761 | s1 |
| d_rel_balliauw15 | v2_2c | v2_a2 | 30 | 1.474 | 1.400 | 0.371 | v2_a2 |
| d_rel_balliauw15 | v2_2c | v2_r1 | 30 | 1.474 | 1.402 | 0.171 | v2_r1 |
| d_rel_balliauw15 | v2_2c | v2_r2 | 30 | 1.474 | 1.372 | 0.0364* | v2_r2 |
| d_rel_balliauw15 | v2_2c | v2_r3 | 30 | 1.474 | 1.365 | 0.00219* | v2_r3 |
| d_rel_balliauw15 | v2_a2 | v2_r1 | 30 | 1.400 | 1.402 | 0.839 | v2_a2 |
| d_rel_balliauw15 | v2_a2 | v2_r2 | 30 | 1.400 | 1.372 | 0.465 | v2_r2 |
| d_rel_balliauw15 | v2_a2 | v2_r3 | 30 | 1.400 | 1.365 | 0.49 | v2_r3 |
| d_rel_balliauw15 | v2_r1 | v2_r2 | 30 | 1.402 | 1.372 | 0.556 | v2_r2 |
| d_rel_balliauw15 | v2_r1 | v2_r3 | 30 | 1.402 | 1.365 | 0.229 | v2_r3 |
| d_rel_balliauw15 | v2_r2 | v2_r3 | 30 | 1.372 | 1.365 | 1 | v2_r3 |
| difficulty_per_note_parncutt12 | M0 (optimum) | S2 (HMM) | 30 | 6.497 | 10.459 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | greedy | 30 | 6.497 | 8.521 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | random-valid | 30 | 6.497 | 18.673 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | s1 | 30 | 6.497 | 9.486 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | v2_2c | 30 | 6.497 | 8.906 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | v2_a2 | 30 | 6.497 | 9.075 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | v2_r1 | 30 | 6.497 | 8.708 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | v2_r2 | 30 | 6.497 | 8.724 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | M0 (optimum) | v2_r3 | 30 | 6.497 | 8.685 | 1.86e-09* | M0 (optimum) |
| difficulty_per_note_parncutt12 | S2 (HMM) | greedy | 30 | 10.459 | 8.521 | 0.0427* | greedy |
| difficulty_per_note_parncutt12 | S2 (HMM) | random-valid | 30 | 10.459 | 18.673 | 6.91e-07* | S2 (HMM) |
| difficulty_per_note_parncutt12 | S2 (HMM) | s1 | 30 | 10.459 | 9.486 | 0.289 | s1 |
| difficulty_per_note_parncutt12 | S2 (HMM) | v2_2c | 30 | 10.459 | 8.906 | 0.0961 | v2_2c |
| difficulty_per_note_parncutt12 | S2 (HMM) | v2_a2 | 30 | 10.459 | 9.075 | 0.109 | v2_a2 |
| difficulty_per_note_parncutt12 | S2 (HMM) | v2_r1 | 30 | 10.459 | 8.708 | 0.0364* | v2_r1 |
| difficulty_per_note_parncutt12 | S2 (HMM) | v2_r2 | 30 | 10.459 | 8.724 | 0.0234* | v2_r2 |
| difficulty_per_note_parncutt12 | S2 (HMM) | v2_r3 | 30 | 10.459 | 8.685 | 0.0221* | v2_r3 |
| difficulty_per_note_parncutt12 | greedy | random-valid | 30 | 8.521 | 18.673 | 1.86e-09* | greedy |
| difficulty_per_note_parncutt12 | greedy | s1 | 30 | 8.521 | 9.486 | 0.00374* | greedy |
| difficulty_per_note_parncutt12 | greedy | v2_2c | 30 | 8.521 | 8.906 | 0.0919 | greedy |
| difficulty_per_note_parncutt12 | greedy | v2_a2 | 30 | 8.521 | 9.075 | 0.031* | greedy |
| difficulty_per_note_parncutt12 | greedy | v2_r1 | 30 | 8.521 | 8.708 | 0.221 | greedy |
| difficulty_per_note_parncutt12 | greedy | v2_r2 | 30 | 8.521 | 8.724 | 0.289 | greedy |
| difficulty_per_note_parncutt12 | greedy | v2_r3 | 30 | 8.521 | 8.685 | 0.393 | greedy |
| difficulty_per_note_parncutt12 | random-valid | s1 | 30 | 18.673 | 9.486 | 1.86e-09* | s1 |
| difficulty_per_note_parncutt12 | random-valid | v2_2c | 30 | 18.673 | 8.906 | 1.86e-09* | v2_2c |
| difficulty_per_note_parncutt12 | random-valid | v2_a2 | 30 | 18.673 | 9.075 | 1.86e-09* | v2_a2 |
| difficulty_per_note_parncutt12 | random-valid | v2_r1 | 30 | 18.673 | 8.708 | 1.86e-09* | v2_r1 |
| difficulty_per_note_parncutt12 | random-valid | v2_r2 | 30 | 18.673 | 8.724 | 1.86e-09* | v2_r2 |
| difficulty_per_note_parncutt12 | random-valid | v2_r3 | 30 | 18.673 | 8.685 | 1.86e-09* | v2_r3 |
| difficulty_per_note_parncutt12 | s1 | v2_2c | 30 | 9.486 | 8.906 | 0.0497* | v2_2c |
| difficulty_per_note_parncutt12 | s1 | v2_a2 | 30 | 9.486 | 9.075 | 0.000111* | v2_a2 |
| difficulty_per_note_parncutt12 | s1 | v2_r1 | 30 | 9.486 | 8.708 | 3.79e-06* | v2_r1 |
| difficulty_per_note_parncutt12 | s1 | v2_r2 | 30 | 9.486 | 8.724 | 4.71e-07* | v2_r2 |
| difficulty_per_note_parncutt12 | s1 | v2_r3 | 30 | 9.486 | 8.685 | 2.05e-07* | v2_r3 |
| difficulty_per_note_parncutt12 | v2_2c | v2_a2 | 30 | 8.906 | 9.075 | 1 | v2_2c |
| difficulty_per_note_parncutt12 | v2_2c | v2_r1 | 30 | 8.906 | 8.708 | 0.0145* | v2_r1 |
| difficulty_per_note_parncutt12 | v2_2c | v2_r2 | 30 | 8.906 | 8.724 | 0.00374* | v2_r2 |
| difficulty_per_note_parncutt12 | v2_2c | v2_r3 | 30 | 8.906 | 8.685 | 0.00046* | v2_r3 |
| difficulty_per_note_parncutt12 | v2_a2 | v2_r1 | 30 | 9.075 | 8.708 | 0.00434* | v2_r1 |
| difficulty_per_note_parncutt12 | v2_a2 | v2_r2 | 30 | 9.075 | 8.724 | 0.000137* | v2_r2 |
| difficulty_per_note_parncutt12 | v2_a2 | v2_r3 | 30 | 9.075 | 8.685 | 0.00017* | v2_r3 |
| difficulty_per_note_parncutt12 | v2_r1 | v2_r2 | 30 | 8.708 | 8.724 | 0.465 | v2_r1 |
| difficulty_per_note_parncutt12 | v2_r1 | v2_r3 | 30 | 8.708 | 8.685 | 0.529 | v2_r3 |
| difficulty_per_note_parncutt12 | v2_r2 | v2_r3 | 30 | 8.724 | 8.685 | 0.839 | v2_r3 |
| infeasible_rate | M0 (optimum) | S2 (HMM) | 30 | 0.007 | 0.051 | 5.61e-06* | M0 (optimum) |
| infeasible_rate | M0 (optimum) | greedy | 30 | 0.007 | 0.003 | 0.401 | greedy |
| infeasible_rate | M0 (optimum) | random-valid | 30 | 0.007 | 0.005 | 0.674 | random-valid |
| infeasible_rate | M0 (optimum) | s1 | 30 | 0.007 | 0.002 | 0.123 | s1 |
| infeasible_rate | M0 (optimum) | v2_2c | 30 | 0.007 | 0.002 | 0.208 | v2_2c |
| infeasible_rate | M0 (optimum) | v2_a2 | 30 | 0.007 | 0.002 | 0.161 | v2_a2 |
| infeasible_rate | M0 (optimum) | v2_r1 | 30 | 0.007 | 0.002 | 0.161 | v2_r1 |
| infeasible_rate | M0 (optimum) | v2_r2 | 30 | 0.007 | 0.003 | 0.161 | v2_r2 |
| infeasible_rate | M0 (optimum) | v2_r3 | 30 | 0.007 | 0.003 | 0.161 | v2_r3 |
| infeasible_rate | S2 (HMM) | greedy | 30 | 0.051 | 0.003 | 5.61e-06* | greedy |
| infeasible_rate | S2 (HMM) | random-valid | 30 | 0.051 | 0.005 | 8.3e-06* | random-valid |
| infeasible_rate | S2 (HMM) | s1 | 30 | 0.051 | 0.002 | 5.61e-06* | s1 |
| infeasible_rate | S2 (HMM) | v2_2c | 30 | 0.051 | 0.002 | 5.61e-06* | v2_2c |
| infeasible_rate | S2 (HMM) | v2_a2 | 30 | 0.051 | 0.002 | 5.61e-06* | v2_a2 |
| infeasible_rate | S2 (HMM) | v2_r1 | 30 | 0.051 | 0.002 | 5.61e-06* | v2_r1 |
| infeasible_rate | S2 (HMM) | v2_r2 | 30 | 0.051 | 0.003 | 5.61e-06* | v2_r2 |
| infeasible_rate | S2 (HMM) | v2_r3 | 30 | 0.051 | 0.003 | 5.61e-06* | v2_r3 |
| infeasible_rate | greedy | random-valid | 30 | 0.003 | 0.005 | 0.225 | greedy |
| infeasible_rate | greedy | s1 | 30 | 0.003 | 0.002 | 0.018* | s1 |
| infeasible_rate | greedy | v2_2c | 30 | 0.003 | 0.002 | 0.116 | v2_2c |
| infeasible_rate | greedy | v2_a2 | 30 | 0.003 | 0.002 | 0.0277* | v2_a2 |
| infeasible_rate | greedy | v2_r1 | 30 | 0.003 | 0.002 | 0.116 | v2_r1 |
| infeasible_rate | greedy | v2_r2 | 30 | 0.003 | 0.003 | 0.0431* | v2_r2 |
| infeasible_rate | greedy | v2_r3 | 30 | 0.003 | 0.003 | 0.173 | v2_r3 |
| infeasible_rate | random-valid | s1 | 30 | 0.005 | 0.002 | 0.018* | s1 |
| infeasible_rate | random-valid | v2_2c | 30 | 0.005 | 0.002 | 0.0747 | v2_2c |
| infeasible_rate | random-valid | v2_a2 | 30 | 0.005 | 0.002 | 0.116 | v2_a2 |
| infeasible_rate | random-valid | v2_r1 | 30 | 0.005 | 0.002 | 0.173 | v2_r1 |
| infeasible_rate | random-valid | v2_r2 | 30 | 0.005 | 0.003 | 0.225 | v2_r2 |
| infeasible_rate | random-valid | v2_r3 | 30 | 0.005 | 0.003 | 0.463 | v2_r3 |
| infeasible_rate | s1 | v2_2c | 30 | 0.002 | 0.002 | 0.0464* | s1 |
| infeasible_rate | s1 | v2_a2 | 30 | 0.002 | 0.002 | 0.273 | s1 |
| infeasible_rate | s1 | v2_r1 | 30 | 0.002 | 0.002 | 0.109 | s1 |
| infeasible_rate | s1 | v2_r2 | 30 | 0.002 | 0.003 | 0.0431* | s1 |
| infeasible_rate | s1 | v2_r3 | 30 | 0.002 | 0.003 | 0.0679 | s1 |
| infeasible_rate | v2_2c | v2_a2 | 30 | 0.002 | 0.002 | 0.753 | v2_a2 |
| infeasible_rate | v2_2c | v2_r1 | 30 | 0.002 | 0.002 | 0.6 | v2_2c |
| infeasible_rate | v2_2c | v2_r2 | 30 | 0.002 | 0.003 | 1 | v2_2c |
| infeasible_rate | v2_2c | v2_r3 | 30 | 0.002 | 0.003 | 0.753 | v2_2c |
| infeasible_rate | v2_a2 | v2_r1 | 30 | 0.002 | 0.002 | 0.273 | v2_a2 |
| infeasible_rate | v2_a2 | v2_r2 | 30 | 0.002 | 0.003 | 0.465 | v2_a2 |
| infeasible_rate | v2_a2 | v2_r3 | 30 | 0.002 | 0.003 | 0.593 | v2_a2 |
| infeasible_rate | v2_r1 | v2_r2 | 30 | 0.002 | 0.003 | 0.593 | v2_r1 |
| infeasible_rate | v2_r1 | v2_r3 | 30 | 0.002 | 0.003 | 0.655 | v2_r1 |
| infeasible_rate | v2_r2 | v2_r3 | 30 | 0.003 | 0.003 | 1 | v2_r2 |
| return_per_event | M0 (optimum) | S2 (HMM) | 30 | -10.219 | -16.994 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | greedy | 30 | -10.219 | -13.016 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | random-valid | 30 | -10.219 | -28.010 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | s1 | 30 | -10.219 | -14.714 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | v2_2c | 30 | -10.219 | -14.302 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | v2_a2 | 30 | -10.219 | -14.106 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | v2_r1 | 30 | -10.219 | -13.469 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | v2_r2 | 30 | -10.219 | -13.543 | 1.86e-09* | M0 (optimum) |
| return_per_event | M0 (optimum) | v2_r3 | 30 | -10.219 | -13.472 | 1.86e-09* | M0 (optimum) |
| return_per_event | S2 (HMM) | greedy | 30 | -16.994 | -13.016 | 0.0327* | greedy |
| return_per_event | S2 (HMM) | random-valid | 30 | -16.994 | -28.010 | 4.42e-06* | S2 (HMM) |
| return_per_event | S2 (HMM) | s1 | 30 | -16.994 | -14.714 | 0.205 | s1 |
| return_per_event | S2 (HMM) | v2_2c | 30 | -16.994 | -14.302 | 0.184 | v2_2c |
| return_per_event | S2 (HMM) | v2_a2 | 30 | -16.994 | -14.106 | 0.1 | v2_a2 |
| return_per_event | S2 (HMM) | v2_r1 | 30 | -16.994 | -13.469 | 0.0277* | v2_r1 |
| return_per_event | S2 (HMM) | v2_r2 | 30 | -16.994 | -13.543 | 0.0208* | v2_r2 |
| return_per_event | S2 (HMM) | v2_r3 | 30 | -16.994 | -13.472 | 0.0221* | v2_r3 |
| return_per_event | greedy | random-valid | 30 | -13.016 | -28.010 | 1.86e-09* | greedy |
| return_per_event | greedy | s1 | 30 | -13.016 | -14.714 | 0.00172* | greedy |
| return_per_event | greedy | v2_2c | 30 | -13.016 | -14.302 | 0.0137* | greedy |
| return_per_event | greedy | v2_a2 | 30 | -13.016 | -14.106 | 0.0234* | greedy |
| return_per_event | greedy | v2_r1 | 30 | -13.016 | -13.469 | 0.146 | greedy |
| return_per_event | greedy | v2_r2 | 30 | -13.016 | -13.543 | 0.237 | greedy |
| return_per_event | greedy | v2_r3 | 30 | -13.016 | -13.472 | 0.309 | greedy |
| return_per_event | random-valid | s1 | 30 | -28.010 | -14.714 | 1.86e-09* | s1 |
| return_per_event | random-valid | v2_2c | 30 | -28.010 | -14.302 | 1.86e-09* | v2_2c |
| return_per_event | random-valid | v2_a2 | 30 | -28.010 | -14.106 | 1.86e-09* | v2_a2 |
| return_per_event | random-valid | v2_r1 | 30 | -28.010 | -13.469 | 1.86e-09* | v2_r1 |
| return_per_event | random-valid | v2_r2 | 30 | -28.010 | -13.543 | 1.86e-09* | v2_r2 |
| return_per_event | random-valid | v2_r3 | 30 | -28.010 | -13.472 | 1.86e-09* | v2_r3 |
| return_per_event | s1 | v2_2c | 30 | -14.714 | -14.302 | 0.416 | v2_2c |
| return_per_event | s1 | v2_a2 | 30 | -14.714 | -14.106 | 5.59e-05* | v2_a2 |
| return_per_event | s1 | v2_r1 | 30 | -14.714 | -13.469 | 5.97e-06* | v2_r1 |
| return_per_event | s1 | v2_r2 | 30 | -14.714 | -13.543 | 3.15e-07* | v2_r2 |
| return_per_event | s1 | v2_r3 | 30 | -14.714 | -13.472 | 3.86e-07* | v2_r3 |
| return_per_event | v2_2c | v2_a2 | 30 | -14.302 | -14.106 | 0.452 | v2_a2 |
| return_per_event | v2_2c | v2_r1 | 30 | -14.302 | -13.469 | 0.00158* | v2_r1 |
| return_per_event | v2_2c | v2_r2 | 30 | -14.302 | -13.543 | 0.000505* | v2_r2 |
| return_per_event | v2_2c | v2_r3 | 30 | -14.302 | -13.472 | 3.45e-05* | v2_r3 |
| return_per_event | v2_a2 | v2_r1 | 30 | -14.106 | -13.469 | 0.00501* | v2_r1 |
| return_per_event | v2_a2 | v2_r2 | 30 | -14.106 | -13.543 | 0.00017* | v2_r2 |
| return_per_event | v2_a2 | v2_r3 | 30 | -14.106 | -13.472 | 0.00017* | v2_r3 |
| return_per_event | v2_r1 | v2_r2 | 30 | -13.469 | -13.543 | 0.416 | v2_r1 |
| return_per_event | v2_r1 | v2_r3 | 30 | -13.469 | -13.472 | 0.641 | v2_r1 |
| return_per_event | v2_r2 | v2_r3 | 30 | -13.543 | -13.472 | 0.919 | v2_r3 |
