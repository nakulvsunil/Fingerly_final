"""Tests for the web app's score readers and the RL fingering endpoint.

    pytest -q webapp
"""

from __future__ import annotations

import io
import struct
import sys
import zipfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]

from score_io import ScoreError, read_score  # noqa: E402

TWINKLE = HERE / "examples" / "twinkle_twinkle.musicxml"
ODE = HERE / "examples" / "ode_to_joy.musicxml"


def _midi(tracks, ppq=480, bpm=120, sig=(3, 4)):
    """A tiny format-1 MIDI file; tracks = [[(start_q, dur_q, pitch), ...], ...]."""
    def vlq(v):
        out = [v & 0x7F]
        while v > 0x7F:
            v >>= 7
            out.insert(0, (v & 0x7F) | 0x80)
        return bytes(out)

    def track(events):
        body, last = b"", 0
        for tick, data in sorted(events, key=lambda e: (e[0], e[1][0] == 0x90)):
            body += vlq(tick - last) + data
            last = tick
        body += b"\x00\xff\x2f\x00"
        return b"MTrk" + struct.pack(">I", len(body)) + body

    meta = [(0, b"\xff\x51\x03" + int(60_000_000 / bpm).to_bytes(3, "big")),
            (0, bytes([0xFF, 0x58, 4, sig[0], {2: 1, 4: 2, 8: 3}[sig[1]], 24, 8]))]
    chunks = [track(meta)]
    for ch, notes in enumerate(tracks):
        ev = []
        for s, d, p in notes:
            ev.append((int(s * ppq), bytes([0x90 | ch, p, 80])))
            ev.append((int((s + d) * ppq), bytes([0x80 | ch, p, 0])))
        chunks.append(track(ev))
    return b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), ppq) + b"".join(chunks)


def test_musicxml_example_bars_and_hands():
    s = read_score(TWINKLE.name, TWINKLE.read_bytes())
    assert s.title.startswith("Twinkle") and len(s.bars) == 12
    assert s.tempo[0][1] == 100
    right = [n for n in s.notes if n.staff == 1]
    assert [n.pitch for n in right[:4]] == [60, 60, 67, 67] and {n.hand for n in right} == {"R"}
    assert abs(s.seconds(4.0) - 2.4) < 1e-9  # one 4/4 bar at 100 bpm
    ode = read_score(ODE.name, ODE.read_bytes())
    chord = [n for n in ode.notes if n.staff == 2 and n.start_q == 0]
    assert sorted(n.pitch for n in chord) == [48, 52, 55]
    assert any(abs(n.dur_q - 1.5) < 1e-9 for n in ode.notes)  # dotted quarter


def test_mxl_is_unzipped():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="score.xml"/></rootfiles></container>')
        z.writestr("score.xml", TWINKLE.read_bytes())
    s = read_score("song.mxl", buf.getvalue())
    assert len(s.notes) == len(read_score(TWINKLE.name, TWINKLE.read_bytes()).notes)


def test_midi_tracks_hands_and_bars():
    rh = [(q, 1, 72 + q % 3) for q in range(6)]
    lh = [(0, 3, 48), (3, 3, 43)]
    s = read_score("waltz.mid", _midi([rh, lh]))
    assert len(s.notes) == 8 and len(s.bars) == 2 and s.bars[0].len_q == 3
    assert {n.hand for n in s.notes if n.pitch >= 72} == {"R"} and {n.hand for n in s.notes if n.pitch < 60} == {"L"}
    assert abs(s.seconds(3) - 1.5) < 1e-9


def test_bad_uploads_give_messages():
    for name, data in [("x.pdf", b"%PDF"), ("x.mid", b"nope"), ("x.musicxml", b"<html/>"), ("x.musicxml", b"<<")]:
        with pytest.raises(ScoreError):
            read_score(name, data)


@pytest.mark.skipif(not (HERE.parent / "runs" / "v2_r3_s0" / "best.pt").exists(), reason="needs the trained v2_r3_s0 checkpoint")
def test_agent_fingers_every_note():
    from agent_runner import Fingerer
    from server import score_json

    f = Fingerer()
    for name, data in [(TWINKLE.name, TWINKLE.read_bytes()), ("waltz.mid", _midi([[(q, 1, 72 + q % 5) for q in range(12)],
                                                                                   [(0, 3, 48), (3, 3, 43)]]))]:
        d = score_json(read_score(name, data), f)
        assert d["stats"]["fingered"] == d["stats"]["total"]
        assert all(n["finger"] in (1, 2, 3, 4, 5) and n["hand"] in ("L", "R") for n in d["notes"])
        assert all(0 <= n["bar"] < len(d["bars"]) for n in d["notes"])


@pytest.mark.skipif(not (HERE.parent / "runs" / "v2_r3_s0" / "best.pt").exists(), reason="needs the trained v2_r3_s0 checkpoint")
def test_refine_never_raises_the_cost(monkeypatch):
    import agent_runner
    from server import score_json

    monkeypatch.setattr(agent_runner, "REFINE_EPISODES", 5)  # keep the test fast
    f = agent_runner.Fingerer()
    d = score_json(read_score(TWINKLE.name, TWINKLE.read_bytes()), f, refine=True)
    r = d["stats"]["refined"]
    assert r is not None and r["cost_after"] <= r["cost_before"]
    assert d["stats"]["fingered"] == d["stats"]["total"]
    assert all(n["finger"] in (1, 2, 3, 4, 5) for n in d["notes"])
