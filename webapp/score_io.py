"""Read an uploaded score into one simple form the webapp can finger and draw.

Supported uploads (standard library only):
  * MusicXML: .musicxml / .xml, and compressed .mxl. This is what MuseScore, Finale, Sibelius,
    Dorico and sheet-music scanning apps export.
  * MIDI: .mid / .midi
  * PIG fingering files (.txt), the dataset format used by the rest of this project. They have no
    bar lines, so the bars are estimated from the rhythm.

Every reader returns a `Score`: notes positioned in quarter notes ("q") from the start, the bars,
and a tempo map that turns quarter positions into seconds for the RL agent and for playback.
"""

from __future__ import annotations

import io
import statistics
import struct
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MAX_NOTES = 6000
MAX_XML_BYTES = 30_000_000
STEPS = "CDEFGAB"
STEP_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
# spelling for MIDI / PIG input: (step, alter) per pitch class, using sharps
SHARP_SPELL = [("C", 0), ("C", 1), ("D", 0), ("D", 1), ("E", 0), ("F", 0), ("F", 1), ("G", 0), ("G", 1),
               ("A", 0), ("A", 1), ("B", 0)]


class ScoreError(ValueError):
    """The upload can't be read; the message is shown to the user."""


@dataclass
class ScoreNote:
    pitch: int  # MIDI number
    start_q: float  # quarter notes from the start of the piece
    dur_q: float
    staff: int  # 1 = upper (treble) staff, 2 = lower (bass) staff
    hand: str  # hand hint ("R"/"L") from the score; the agent may change it for single notes
    step: str
    alter: int
    octave: int


@dataclass
class Bar:
    number: int
    start_q: float
    len_q: float
    beats: int
    beat_type: int


@dataclass
class Score:
    title: str
    notes: List[ScoreNote]
    bars: List[Bar]
    tempo: List[Tuple[float, float]]  # (quarter position, quarter notes per minute), sorted
    source: str  # "musicxml" | "midi" | "pig"
    estimated_bars: bool = False
    warnings: List[str] = field(default_factory=list)

    def seconds(self, q: float) -> float:
        """Quarter position -> seconds, following the tempo map."""
        t, prev_q, bpm = 0.0, 0.0, self.tempo[0][1]
        for tq, tb in self.tempo[1:]:
            if tq >= q:
                break
            t += (tq - prev_q) * 60.0 / bpm
            prev_q, bpm = tq, tb
        return t + (q - prev_q) * 60.0 / bpm


def spell(pitch: int) -> Tuple[str, int, int]:
    step, alter = SHARP_SPELL[pitch % 12]
    return step, alter, pitch // 12 - 1


def read_score(name: str, data: bytes) -> Score:
    ext = Path(name).suffix.lower()
    title = Path(name).stem.replace("_", " ")
    if ext == ".mxl":
        return read_musicxml(_unzip_mxl(data), title)
    if ext in (".musicxml", ".xml"):
        return read_musicxml(data, title)
    if ext in (".mid", ".midi"):
        return read_midi(data, title)
    if ext == ".txt":
        return read_pig(data, title)
    raise ScoreError("Please upload a MusicXML (.musicxml, .xml, .mxl), MIDI (.mid) or PIG (.txt) file.")


# --------------------------------------------------------------------------------------
# MusicXML
# --------------------------------------------------------------------------------------
def _unzip_mxl(data: bytes) -> bytes:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise ScoreError("This .mxl file is not a valid compressed MusicXML file.")
    path = None
    if "META-INF/container.xml" in z.namelist():
        root = ET.fromstring(z.read("META-INF/container.xml"))
        _strip_ns(root)
        rf = root.find(".//rootfile")
        if rf is not None and rf.get("full-path") in z.namelist():
            path = rf.get("full-path")
    if path is None:
        path = next((n for n in z.namelist() if n.endswith((".xml", ".musicxml")) and not n.startswith("META-INF")),
                    None)
    if path is None:
        raise ScoreError("No score was found inside this .mxl file.")
    info = z.getinfo(path)
    if info.file_size > MAX_XML_BYTES:
        raise ScoreError("The score inside this .mxl file is too large.")
    return z.read(path)


def _strip_ns(root: ET.Element) -> None:
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]


def _num(el: Optional[ET.Element], default: float = 0.0) -> float:
    try:
        return float(el.text) if el is not None and el.text else default
    except ValueError:
        return default


def read_musicxml(data: bytes, title: str) -> Score:
    if len(data) > MAX_XML_BYTES:
        raise ScoreError("This score file is too large.")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise ScoreError(f"This MusicXML file could not be read ({e}).")
    _strip_ns(root)
    if root.tag == "score-timewise":
        raise ScoreError("Time-wise MusicXML is not supported; please export a normal (part-wise) MusicXML file.")
    if root.tag != "score-partwise":
        raise ScoreError("This file is not a MusicXML score.")
    t = root.findtext("work/work-title") or root.findtext("movement-title")
    if t and t.strip():
        title = t.strip()

    parts = root.findall("part")
    if not parts:
        raise ScoreError("This score has no parts.")
    warnings: List[str] = []
    notes: List[ScoreNote] = []
    tempo: Dict[float, float] = {}
    bars: List[Bar] = []
    # several single-staff parts (e.g. a duet layout): part 1 -> upper staff, the rest -> lower staff
    single_staff_parts = all(int(_num(p.find("measure/attributes/staves"), 1)) == 1 for p in parts)
    if len(parts) > 2:
        warnings.append(f"The score has {len(parts)} parts; they are all played on one piano.")

    for pi, part in enumerate(parts):
        divisions = 1.0
        beats, beat_type = 4, 4
        pos = 0.0  # quarter position of the current measure
        clefs: Dict[int, str] = {1: "G", 2: "F"}
        ties: Dict[Tuple[int, int], ScoreNote] = {}  # (staff, pitch) -> note waiting for its tie end
        for mi, meas in enumerate(part.findall("measure")):
            cur = 0.0  # position inside the measure, quarters
            longest = 0.0
            last_start = 0.0
            for el in meas:
                if el.tag == "attributes":
                    divisions = _num(el.find("divisions"), divisions) or divisions
                    ts = el.find("time")
                    if ts is not None and ts.find("beats") is not None:
                        try:
                            beats = int(ts.findtext("beats").split("+")[0])
                            beat_type = int(ts.findtext("beat-type"))
                        except (TypeError, ValueError):
                            pass
                    for c in el.findall("clef"):
                        clefs[int(c.get("number", "1"))] = (c.findtext("sign") or "G").upper()
                elif el.tag == "sound" and el.get("tempo"):
                    tempo.setdefault(pos + cur, float(el.get("tempo")))
                elif el.tag == "direction":
                    s = el.find("sound")
                    if s is not None and s.get("tempo"):
                        tempo.setdefault(pos + cur, float(s.get("tempo")))
                    else:
                        m = el.find("direction-type/metronome")
                        if m is not None and m.findtext("per-minute"):
                            unit = {"whole": 4, "half": 2, "quarter": 1, "eighth": 0.5, "16th": 0.25}.get(
                                m.findtext("beat-unit") or "quarter", 1)
                            if m.find("beat-unit-dot") is not None:
                                unit *= 1.5
                            try:
                                tempo.setdefault(pos + cur, float(m.findtext("per-minute")) * unit)
                            except ValueError:
                                pass
                elif el.tag == "backup":
                    cur -= _num(el.find("duration")) / divisions
                elif el.tag == "forward":
                    cur += _num(el.find("duration")) / divisions
                    longest = max(longest, cur)
                elif el.tag == "note":
                    if el.find("grace") is not None or el.find("cue") is not None:
                        continue
                    dur = _num(el.find("duration")) / divisions
                    chord = el.find("chord") is not None
                    start = last_start if chord else cur
                    if not chord:
                        cur += dur
                        last_start = start
                    longest = max(longest, cur)
                    pitch_el = el.find("pitch")
                    if el.find("rest") is not None or pitch_el is None:
                        continue
                    step = (pitch_el.findtext("step") or "C").upper()
                    alter = int(round(_num(pitch_el.find("alter"))))
                    octave = int(_num(pitch_el.find("octave"), 4))
                    pitch = 12 * (octave + 1) + STEP_PC.get(step, 0) + alter
                    if single_staff_parts:
                        staff = 1 if pi == 0 and (len(parts) > 1 or clefs.get(1, "G") != "F") else 2
                    else:
                        staff = 2 if int(_num(el.find("staff"), 1)) >= 2 else 1
                    tie_types = {t.get("type") for t in el.findall("tie")}
                    key = (staff, pitch)
                    if "stop" in tie_types and key in ties:
                        prev = ties.pop(key)
                        prev.dur_q = pos + start + dur - prev.start_q
                        if "start" in tie_types:
                            ties[key] = prev
                        continue
                    n = ScoreNote(pitch, pos + start, dur, staff, "R" if staff == 1 else "L", step, alter, octave)
                    notes.append(n)
                    if "start" in tie_types:
                        ties[key] = n
            if pi == 0:
                nominal = beats * 4.0 / beat_type
                length = longest if meas.get("implicit") == "yes" and longest > 0 else max(nominal, longest)
                bars.append(Bar(len(bars) + 1, pos, length, beats, beat_type))
            pos += bars[mi].len_q if mi < len(bars) else max(longest, beats * 4.0 / beat_type)
            if len(notes) > MAX_NOTES:
                raise ScoreError(f"This score is too long for the web app (more than {MAX_NOTES} notes).")
    if not notes:
        raise ScoreError("No notes were found in this score.")
    tmap = sorted(tempo.items()) or [(0.0, 100.0)]
    if tmap[0][0] > 0:
        tmap.insert(0, (0.0, tmap[0][1]))
    if not tempo:
        warnings.append("No tempo marking found; using 100 beats per minute.")
    return Score(title, sorted(notes, key=lambda n: (n.start_q, n.pitch)), _trim_bars(bars, notes), tmap,
                 "musicxml", warnings=warnings)


def _trim_bars(bars: List[Bar], notes: List[ScoreNote]) -> List[Bar]:
    """Drop empty bars after the last note."""
    end = max(n.start_q for n in notes)
    return [b for b in bars if b.start_q <= end + 1e-6] or bars[:1]


# --------------------------------------------------------------------------------------
# MIDI
# --------------------------------------------------------------------------------------
def _vlq(data: bytes, i: int) -> Tuple[int, int]:
    v = 0
    while True:
        if i >= len(data):
            raise ScoreError("This MIDI file is cut short.")
        b = data[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def read_midi(data: bytes, title: str) -> Score:
    if data[:4] != b"MThd" or len(data) < 14:
        raise ScoreError("This is not a MIDI file.")
    hlen = struct.unpack(">I", data[4:8])[0]
    _fmt, ntrk, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise ScoreError("MIDI files with SMPTE timing are not supported.")
    ppq = float(division)
    i = 8 + hlen
    tracks: List[List[Tuple[int, int, int, int]]] = []  # per track: (start tick, end tick, pitch, channel)
    tempos: Dict[int, float] = {}
    timesigs: Dict[int, Tuple[int, int]] = {}
    track_names: List[str] = []
    for _ in range(ntrk):
        if data[i:i + 4] != b"MTrk":
            break
        tlen = struct.unpack(">I", data[i + 4:i + 8])[0]
        j, end = i + 8, i + 8 + tlen
        i = end
        tick, status, on, out, name = 0, 0, {}, [], ""
        while j < end:
            dt, j = _vlq(data, j)
            tick += dt
            b = data[j]
            if b == 0xFF:
                mtype = data[j + 1]
                ln, j = _vlq(data, j + 2)
                body = data[j:j + ln]
                j += ln
                if mtype == 0x51 and ln == 3:
                    tempos.setdefault(tick, 60_000_000 / int.from_bytes(body, "big"))
                elif mtype == 0x58 and ln >= 2:
                    timesigs.setdefault(tick, (body[0], 2 ** body[1]))
                elif mtype == 0x03:
                    name = body.decode("latin-1", "replace").strip()
                continue
            if b in (0xF0, 0xF7):
                ln, j = _vlq(data, j + 1)
                j += ln
                continue
            if b & 0x80:
                status = b
                j += 1
            kind, ch = status & 0xF0, status & 0x0F
            if kind in (0xC0, 0xD0):
                j += 1
                continue
            a, v = data[j], data[j + 1]
            j += 2
            if kind == 0x90 and v > 0:
                on.setdefault((ch, a), []).append(tick)
            elif kind == 0x80 or (kind == 0x90 and v == 0):
                starts = on.get((ch, a))
                if starts:
                    s = starts.pop(0)
                    out.append((s, max(tick, s + 1), a, ch))
        tracks.append(out)
        track_names.append(name)
    note_tracks = [(k, t) for k, t in enumerate(tracks) if t and all(n[3] != 9 for n in t)]  # skip drums
    if not note_tracks:
        raise ScoreError("No piano notes were found in this MIDI file.")
    if sum(len(t) for _, t in note_tracks) > MAX_NOTES:
        raise ScoreError(f"This MIDI file is too long for the web app (more than {MAX_NOTES} notes).")

    # hands: two or more tracks -> the highest-sounding track is the right hand; one track with two
    # channels -> the same by channel; otherwise split at middle C
    groups: Dict[object, List[Tuple[int, int, int, int]]] = {}
    if len(note_tracks) >= 2:
        for k, t in note_tracks:
            groups[("t", k)] = t
    else:
        for n in note_tracks[0][1]:
            groups.setdefault(("c", n[3]), []).append(n)
    warnings: List[str] = []
    if len(groups) >= 2:
        upper = max(groups, key=lambda g: statistics.mean(n[2] for n in groups[g]))
        hand_of = {g: ("R" if g == upper else "L") for g in groups}
        split = None
    else:
        hand_of, split = {}, 60
        warnings.append("The MIDI file has one part, so notes from middle C up start in the right hand.")
    notes = []
    for g, ns in groups.items():
        for s, e, p, _ch in ns:
            hand = hand_of.get(g) or ("R" if p >= split else "L")
            step, alter, octave = spell(p)
            notes.append(ScoreNote(p, s / ppq, (e - s) / ppq, 1 if hand == "R" else 2, hand, step, alter, octave))
    notes.sort(key=lambda n: (n.start_q, n.pitch))

    tmap = sorted((t / ppq, bpm) for t, bpm in tempos.items()) or [(0.0, 120.0)]
    if tmap[0][0] > 0:
        tmap.insert(0, (0.0, tmap[0][1]))
    sigs = sorted((t / ppq, s) for t, s in timesigs.items()) or [(0.0, (4, 4))]
    if sigs[0][0] > 0:
        sigs.insert(0, (0.0, sigs[0][1]))
    end_q = max(n.start_q for n in notes)
    bars, q, k = [], 0.0, 0
    while q <= end_q + 1e-6:
        while k + 1 < len(sigs) and sigs[k + 1][0] <= q + 1e-6:
            k += 1
        beats, bt = sigs[k][1]
        ln = beats * 4.0 / bt
        bars.append(Bar(len(bars) + 1, q, ln, beats, bt))
        q += ln
    return Score(title, notes, bars, tmap, "midi", warnings=warnings)


# --------------------------------------------------------------------------------------
# PIG fingering files
# --------------------------------------------------------------------------------------
def read_pig(data: bytes, title: str) -> Score:
    from fingerly.pig import read_fingering_file  # the project's reader
    import tempfile
    import os

    fd, path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        try:
            pig = read_fingering_file(path)
        except (ValueError, KeyError, IndexError) as e:
            raise ScoreError(f"This PIG file could not be read ({e}).")
    finally:
        os.unlink(path)
    if not pig:
        raise ScoreError("No notes were found. PIG files have one note per line: id, onset, offset, pitch, ...")
    if len(pig) > MAX_NOTES:
        raise ScoreError(f"This file is too long for the web app (more than {MAX_NOTES} notes).")

    beat = _estimate_beat([n.onset for n in pig])
    notes = []
    for n in pig:
        step, alter, octave = spell(n.pitch)
        notes.append(ScoreNote(n.pitch, n.onset / beat, max(n.offset - n.onset, 0.05) / beat,
                               1 if n.hand == "R" else 2, n.hand or "R", step, alter, octave))
    end_q = max(n.start_q for n in notes)
    bars = [Bar(k + 1, 4.0 * k, 4.0, 4, 4) for k in range(int(end_q // 4) + 1)]
    return Score(title.split("_")[0], notes, bars, [(0.0, 60.0 / beat)], "pig", estimated_bars=True,
                 warnings=["PIG files have no bar lines, so the bars shown are estimated (4 beats each)."])


def _estimate_beat(onsets: List[float]) -> float:
    """A beat length in seconds: the most common gap between note starts, scaled into 0.4-1.0 s."""
    ts = sorted(set(round(t, 3) for t in onsets))
    gaps = [b - a for a, b in zip(ts, ts[1:]) if b - a > 0.06]
    if not gaps:
        return 0.6
    hist: Dict[int, int] = {}
    for g in gaps:
        hist[round(g / 0.02)] = hist.get(round(g / 0.02), 0) + 1
    beat = max(hist, key=lambda k: (hist[k], -k)) * 0.02
    while beat < 0.4:
        beat *= 2
    while beat > 1.0:
        beat /= 2
    return beat
