"""Beginner-style music for training and checking the RL agent.

PIG is mostly advanced repertoire; the agent trained on it fingers simple beginner tunes badly
(about 30x the M0 optimum, against about 2x on PIG). This module provides:

* `beginner_segments(n, seed)`: random beginner pieces for training: melodies in a five-finger
  position with steps, repeated notes and small skips, occasional position shifts and scale runs,
  in common easy keys, over simple left-hand parts (held roots, block triads, broken chords,
  Alberti bass, the melody in the left hand, or both hands in octaves). No labels: rule reward only.
* `heldout_tunes()`: real public-domain beginner tunes with simple left-hand parts. They are the
  test set: never trained on and never used to select a checkpoint.

Notes use the project's `Note` type; onsets in seconds, full written durations (as the web app
reads scores).
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from fingerly.pig import Note

MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
KEYS = [0, 0, 0, 7, 7, 5, 5, 2, 10, 9, 3, 4]  # tonic pitch classes, easy keys more often
CHORDS = {"I": [0, 2, 4], "IV": [3, 5, 7], "V": [4, 6, 8]}  # scale degrees
RHYTHMS = {
    4: [[1, 1, 1, 1], [1, 1, 1, 1], [2, 1, 1], [1, 1, 2], [2, 2], [0.5, 0.5, 1, 1, 1], [1, 1, 0.5, 0.5, 1],
        [1.5, 0.5, 1, 1], [1, 1, 1.5, 0.5], [0.5, 0.5, 0.5, 0.5, 1, 1], [4], [3, 1]],
    3: [[1, 1, 1], [1, 1, 1], [2, 1], [1, 2], [3], [0.5, 0.5, 1, 1], [1.5, 0.5, 1]],
}


def _pitch(tonic_midi: int, scale: Sequence[int], degree: int) -> int:
    o, d = divmod(degree, 7)
    return tonic_midi + 12 * o + scale[d]


class _Piece:
    def __init__(self, bpm: float):
        self.notes: List[Note] = []
        self.spb = 60.0 / bpm

    def add(self, beat: float, beats: float, pitch: int, hand: str):
        t = round(beat * self.spb, 4)
        self.notes.append(Note(len(self.notes), t, round(t + beats * self.spb, 4), int(pitch), 0 if hand == "R" else 1,
                               hand, None))


def beginner_piece(rng: random.Random) -> List[Note]:
    tonic = rng.choice(KEYS)
    scale = MAJOR if rng.random() < 0.85 else MINOR
    meter = 4 if rng.random() < 0.75 else 3
    n_bars = rng.choice([8, 8, 12, 16])
    piece = _Piece(rng.uniform(60, 140))
    rh_tonic = 60 + tonic if tonic <= 7 else 48 + tonic  # tonic between F3+12 and G4
    style = rng.choices(["none", "roots", "blocks", "broken", "alberti", "lh_melody", "octaves"],
                        [8, 22, 22, 16, 12, 10, 10])[0]
    lh_tonic = rh_tonic - 12 * (1 if style in ("lh_melody", "octaves") else rng.choice([1, 1, 2]))

    # right-hand melody as scale degrees, in a five-finger position [pos, pos + 4]
    pos = rng.choice([0, 0, 0, 2, 4, -3])
    deg = pos + rng.choice([0, 2, 4])
    melody: List[Tuple[float, float, int]] = []  # (beat, beats, degree)
    bar_chords: List[str] = []
    beat = 0.0
    run_left = 0
    for b in range(n_bars):
        if b % 2 == 0 and b and rng.random() < 0.3:  # move the hand to a new position
            pos += rng.choice([-4, -3, -2, 2, 3, 4])
            pos = max(-5, min(7, pos))
            deg = pos + rng.randrange(5)
        if b % 2 == 0 and rng.random() < 0.12:
            run_left = rng.choice([5, 6, 8])  # a scale run: thumb under / finger over
            run_dir = rng.choice([-1, 1])
        rhythm = rng.choice(RHYTHMS[meter])
        if b == n_bars - 1:
            rhythm = [meter]
        for k, d in enumerate(rhythm):
            if b == n_bars - 1:
                deg = round(deg / 7) * 7  # end on the tonic
            elif run_left:
                deg += run_dir
                run_left -= 1
            elif k or b:
                step = rng.choices([0, 1, -1, 2, -2, 3, -3, 4, -4], [16, 22, 22, 10, 10, 4, 4, 2, 2])[0]
                nd = deg + step
                if not pos <= nd <= pos + 4 and rng.random() < 0.85:
                    nd = deg - step  # stay in the position
                deg = max(-7, min(11, nd))
            melody.append((beat, d, deg))
            beat += d
        first = melody[-len(rhythm)][2] % 7
        fits = [c for c, ds in CHORDS.items() if first in [x % 7 for x in ds]]
        bar_chords.append(rng.choice(fits) if fits else "I")
    bar_chords[-1] = "I"

    lh_melody = style == "lh_melody"
    for bt, d, dg in melody:
        piece.add(bt, d, _pitch(lh_tonic if lh_melody else rh_tonic, scale, dg), "L" if lh_melody else "R")
        if style == "octaves":
            piece.add(bt, d, _pitch(rh_tonic - 12, scale, dg), "L")

    # the other hand
    for b, c in enumerate(bar_chords):
        b0 = b * meter
        ds = CHORDS[c]
        # close position near the hand's tonic (I: 0 2 4, IV: 0 3 5, V: -1 1 4 as degrees)
        close = {"I": [0, 2, 4], "IV": [0, 3, 5], "V": [-1, 1, 4]}[c]
        if style == "roots":
            if rng.random() < 0.5:
                piece.add(b0, meter, _pitch(lh_tonic, scale, ds[0] if ds[0] < 4 else ds[0] - 7), "L")
            else:
                for k in range(0, meter, 2 if meter == 4 else 3):
                    piece.add(b0 + k, min(2, meter - k), _pitch(lh_tonic, scale, [ds[0], ds[2]][(k // 2) % 2] - (7 if ds[0] >= 4 else 0)), "L")
        elif style == "blocks":
            hold = meter if rng.random() < 0.4 else (2 if meter == 4 else 1)
            for k in range(0, meter, hold):
                for x in close:
                    piece.add(b0 + k, min(hold, meter - k), _pitch(lh_tonic, scale, x), "L")
        elif style in ("broken", "alberti"):
            low, mid, high = (_pitch(lh_tonic, scale, x) for x in close)
            pat = [low, high, mid, high] if style == "alberti" else rng.choice([[low, mid, high, mid], [low, high, mid, high], [low, mid, high]])
            unit = 0.5 if style == "alberti" or rng.random() < 0.4 else 1.0
            k = 0.0
            i = 0
            while k < meter - 1e-9:
                piece.add(b0 + k, unit, pat[i % len(pat)], "L")
                k += unit
                i += 1
        elif style == "lh_melody":  # right hand: held chord or single notes above
            if rng.random() < 0.6:
                for x in close:
                    piece.add(b0, meter, _pitch(rh_tonic, scale, x), "R")
            else:
                piece.add(b0, meter, _pitch(rh_tonic, scale, close[rng.randrange(3)] + 7 * (close[0] < 0)), "R")
    for n in piece.notes:  # keep to a beginner's range, C2-E6
        while n.pitch < 36:
            n.pitch += 12
        while n.pitch > 88:
            n.pitch -= 12
    return piece.notes


def beginner_segments(n: int, seed: int = 0, prep=None, name: str = "beginner"):
    """n beginner pieces as segments (synthetic: no labels, no imitation bonus)."""
    from fingerly.twohand.prepare import PrepConfig, piece_events, segment_stream

    prep = prep or PrepConfig()
    rng = random.Random(seed)
    out = []
    for k in range(n):
        ev = piece_events([beginner_piece(rng)], prep)
        for e in ev:
            e.labels = []
        for s in segment_stream(f"{name}:{k}", ev, prep, min_len=4):
            s.synthetic = True
            out.append(s)
    return out


# --------------------------------------------------------------------------------------
# Held-out real beginner tunes (public domain). (pitch, beats); a tuple of pitches is a chord.
# --------------------------------------------------------------------------------------
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _m(name: str) -> int:
    step, rest = name[0], name[1:]
    alt = rest.count("#") - rest.count("b")
    return 12 * (int(rest.lstrip("#b")) + 1) + _PC[step] + alt


def _line(spec: str) -> List[Tuple[Tuple[int, ...], float]]:
    """'E4:1 D4:1 C4+E4+G4:2 ...' -> [((pitches), beats), ...]; bars '|' are ignored."""
    out = []
    for tok in spec.replace("|", " ").split():
        p, d = tok.split(":")
        out.append((tuple(_m(x) for x in p.split("+")), float(d)))
    return out


TUNES = {
    "Mary Had a Little Lamb": (100, 0,
        "E4:1 D4:1 C4:1 D4:1 | E4:1 E4:1 E4:2 | D4:1 D4:1 D4:2 | E4:1 G4:1 G4:2 | E4:1 D4:1 C4:1 D4:1 | E4:1 E4:1 E4:1 E4:1 | D4:1 D4:1 E4:1 D4:1 | C4:4",
        "C3:4 | C3:4 | G2:4 | C3:4 | C3:4 | C3:4 | G2:4 | C3:4"),
    "Hot Cross Buns (G major)": (96, 7,
        "E4:1 D4:1 C4:2 | E4:1 D4:1 C4:2 | C4:0.5 C4:0.5 C4:0.5 C4:0.5 D4:0.5 D4:0.5 D4:0.5 D4:0.5 | E4:1 D4:1 C4:2",
        "C3+G3:4 | C3+G3:4 | C3+G3:2 G2+D3:2 | C3+G3:4"),
    "Jingle Bells (chorus)": (120, 0,
        "B4:1 B4:1 B4:2 | B4:1 B4:1 B4:2 | B4:1 D5:1 G4:1.5 A4:0.5 | B4:4 | C5:1 C5:1 C5:1.5 C5:0.5 | C5:1 B4:1 B4:1 B4:0.5 B4:0.5 | B4:1 A4:1 A4:1 B4:1 | A4:2 D5:2",
        "G2+D3:2 G2+D3:2 | G2+D3:2 G2+D3:2 | G2+D3:2 G2+D3:2 | G2+D3:4 | C3+G3:2 C3+G3:2 | G2+D3:2 G2+D3:2 | D3+A3:2 D3+A3:2 | D3+A3:2 D3+F#3:2"),
    "Au Clair de la Lune": (90, 0,
        "C4:1 C4:1 C4:1 D4:1 | E4:2 D4:2 | C4:1 E4:1 D4:1 D4:1 | C4:4 | C4:1 C4:1 C4:1 D4:1 | E4:2 D4:2 | C4:1 E4:1 D4:1 D4:1 | C4:4",
        "C3:2 G3:2 | C3:2 G2:2 | C3:2 G2:2 | C3:4 | C3:2 G3:2 | C3:2 G2:2 | C3:2 G2:2 | C3:4"),
    "Lightly Row (F major)": (104, 5,
        "G4:1 E4:1 E4:2 | F4:1 D4:1 D4:2 | C4:1 D4:1 E4:1 F4:1 | G4:1 G4:1 G4:2 | G4:1 E4:1 E4:2 | F4:1 D4:1 D4:2 | C4:1 E4:1 G4:1 G4:1 | C4:4",
        " ".join(["C3:0.5 G3:0.5 E3:0.5 G3:0.5"] * 2) + " | " + " ".join(["B2:0.5 G3:0.5 D3:0.5 G3:0.5"] * 2) + " | "
        + " ".join(["C3:0.5 G3:0.5 E3:0.5 G3:0.5"] * 4) + " | " + " ".join(["C3:0.5 G3:0.5 E3:0.5 G3:0.5"] * 2) + " | "
        + " ".join(["B2:0.5 G3:0.5 D3:0.5 G3:0.5"] * 2) + " | " + " ".join(["C3:0.5 G3:0.5 E3:0.5 G3:0.5"] * 2) + " | C3+E3+G3:4"),
    "Frere Jacques": (110, 0,
        "C4:1 D4:1 E4:1 C4:1 | C4:1 D4:1 E4:1 C4:1 | E4:1 F4:1 G4:2 | E4:1 F4:1 G4:2 | G4:0.5 A4:0.5 G4:0.5 F4:0.5 E4:1 C4:1 | G4:0.5 A4:0.5 G4:0.5 F4:0.5 E4:1 C4:1 | C4:1 G3:1 C4:2 | C4:1 G3:1 C4:2",
        "C3:2 G2:2 | C3:2 G2:2 | C3:2 G2:2 | C3:2 G2:2 | C3:2 G2:2 | C3:2 G2:2 | C3:4 | C3:4"),
}


def _tune_notes(bpm: float, shift: int, rh: str, lh: str) -> List[Note]:
    piece = _Piece(bpm)
    for spec, hand in ((rh, "R"), (lh, "L")):
        beat = 0.0
        for ps, d in _line(spec):
            for p in ps:
                piece.add(beat, d, p + shift, hand)
            beat += d
    return piece.notes


def heldout_tunes() -> Dict[str, List[Note]]:
    """The test set: the tunes above plus the web app's two example scores."""
    out = {name: _tune_notes(*spec) for name, spec in TUNES.items()}
    from score_io import read_score

    for f in sorted((Path(__file__).resolve().parent / "examples").glob("*.musicxml")):
        sc = read_score(f.name, f.read_bytes())
        out[sc.title] = [Note(k, sc.seconds(n.start_q), sc.seconds(n.start_q + n.dur_q), n.pitch,
                              0 if n.hand == "R" else 1, n.hand, None) for k, n in enumerate(sc.notes)]
    return out
