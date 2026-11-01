# Piano Finger Buddy (web app)

A beginner- and child-friendly web app for the application side of Fingerly. Upload a piano score
and the trained RL agent fingers it. The app then shows the score **two bars at a time**
with a finger number on every note, and plays it on a small piano with both hands drawn above it.
When the two bars finish, the next two appear, until the song ends.

This folder is a self-contained add-on: it changes no file outside `webapp/` and needs nothing
beyond `requirements.txt` (the server uses only Python's standard library, plus torch for the agent).

## Run

```powershell
.venv\Scripts\Activate.ps1
python webapp/server.py --open          # http://127.0.0.1:8000
```

`--port 8080` changes the port. `--ckpt <path>` loads another Part C checkpoint (default below).

## Which agent

The default is **`runs/v2_r3_s0/best.pt`**: R3 (masked Double DQN with elite replay and a small
imitation term, λ = 4) retrained with the v2 recipe (γ 0.5, full 1M steps, no early stopping;
`experiments/RESULTS.md`). The seed was chosen on validation (Mgen 63.4%). On the test pieces v2
R3 has Mgen 61.7% and wastes about a third as much effort per note as the original agents
(`results/twohand_v2/`). The previous default, `runs/a2_s2/best.pt`, still loads with `--ckpt`.
It runs in mode `given`: the agent fingers both hands and chords, and **the hands come from the score**. The score goes through the same
pipeline as evaluation (`fingerly.twohand.prepare` → `SegmentPool` → greedy rollout, no imitation
bonus).

**Refine is on by default.** Before answering, the agent keeps learning on the uploaded piece
itself, by RL with the rule reward only. To get the instant, unrefined fingering, untick the box
under the upload area, add `?refine=0` to the request, or start the server with `--no-refine`.
That means 100 episodes from each of the three v2 R3 seeds, keeping the fingering with the lowest
cost (`experiments/finetune_best.py`). No pianist fingerings are used. On the PIG test pieces this
raises Mgen from 61.7% to 63.9%. The three seeds run in parallel, on the GPU when there is one.

The budget is set in `agent_runner.py`. Every piece gets at least 25 episodes: on the validation
pieces, 25 episodes match pianists as well as 100 (Mgen 65.6% vs 65.1%). A piece keeps practising
up to 100 episodes while the upload is under 30 s, and nothing goes past 90 s. Measured times
(plugged in, GPU):

| Piece | Notes | Time | Episodes |
| --- | --- | --- | --- |
| Ode to Joy | 78 | 14 s | 100 |
| Chopin, Waltz Op. 64 No. 1 | 393 | 32 s | 30 |
| Bach, Invention No. 1 | 469 | 34 s | 25 |
| Chopin, Fantaisie-Impromptu | 555 | 31 s | 28 |
| Chopin, Étude Op. 10 No. 12 | 2082 | 73 s | 25 |

Refine applies to mode `given` only.

`--ckpt runs/v2_2c_s0/best.pt` switches to mode 2c, where the agent also chooses the hand for single
notes; a small **L** or **R** next to a finger number then marks a note moved to the other hand.

## Uploads

| Format | Notes |
| --- | --- |
| MusicXML (`.musicxml`, `.xml`, `.mxl`) | Best choice. Bars, time signatures, tempo and staves come from the file. Upper staff → right hand, lower staff → left hand |
| MIDI (`.mid`) | Bars come from the time signature. With two or more tracks, the highest track is the right hand; with one track, notes are split at middle C |
| PIG (`.txt`) | The project's dataset format. It has no bar lines, so bars are estimated (4 beats each) |

A PDF or a photo of sheet music has to be converted first: open it in MuseScore (File → Import PDF),
or use a sheet-music scanning app, and export MusicXML. Without a tempo marking, 100 BPM is used;
the tempo affects the agent's time-leap cost.

## Using the player

- **▶ / ⏸** plays and pauses. The 🐢–🐇 slider sets the speed (60% by default).
- **⏮ / ⏭** go one note (or chord) at a time. Clicking any note in the score jumps to it.
- **‹ / ›** or the dots go to the previous or next two bars. **Repeat these 2 bars** loops them.
- **Right hand / Left hand** turn a hand off, to practise one hand at a time.
- Finger colours: 1 thumb (orange), 2 pointer (yellow), 3 middle (green), 4 ring (blue), 5 pinky
  (purple).
- Keys: Space = play/pause, ← → = one note, PageUp/PageDown = two bars.
- `/?example=ode_to_joy.musicxml` opens an example directly.

## Files

| File | What it does |
| --- | --- |
| `server.py` | HTTP server: the page, `POST /api/finger` (file body, name in `X-Filename`), examples |
| `score_io.py` | MusicXML / MXL / MIDI / PIG readers → notes in quarter notes, bars, tempo map |
| `agent_runner.py` | Runs the RL agent on a score and maps the fingers back to its notes |
| `static/` | The page: score drawing, piano, hands, playback and sound (Web Audio) |
| `examples/` | Two public-domain songs; `make_examples.py` rewrites them |
| `test_webapp.py` | `pytest -q webapp` |

The score drawing is simplified for beginners: every sharp or flat is written next to its note (no
key signature), and rests and ties are not drawn.
