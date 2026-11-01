"""Write the example scores (public-domain tunes, simple two-hand arrangements) as MusicXML.

    python webapp/examples/make_examples.py
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
DIV = 2  # divisions per quarter note: eighth notes are the shortest value
TYPES = {1: "eighth", 2: "quarter", 3: "quarter", 4: "half", 6: "half", 8: "whole"}

# a bar is a list of (pitches, length in eighths); pitches like "C4", "F#3", or a tuple for a chord


def _pitch_xml(p: str) -> str:
    step, rest = p[0], p[1:]
    alter = 1 if rest.startswith("#") else -1 if rest.startswith("b") else 0
    octave = rest.lstrip("#b")
    a = f"<alter>{alter}</alter>" if alter else ""
    return f"<pitch><step>{step}</step>{a}<octave>{octave}</octave></pitch>"


def _notes_xml(bar, staff: int) -> str:
    out = []
    for pitches, ln in bar:
        pitches = pitches if isinstance(pitches, tuple) else (pitches,)
        for k, p in enumerate(pitches):
            dot = "<dot/>" if ln in (3, 6) else ""
            chord = "<chord/>" if k else ""
            out.append(f"<note>{chord}{_pitch_xml(p)}<duration>{ln * DIV // 2}</duration><voice>{staff}</voice>"
                       f"<type>{TYPES[ln]}</type>{dot}<staff>{staff}</staff></note>")
    return "".join(out)


def write_score(path: Path, title: str, tempo: int, right, left) -> None:
    measures = []
    for i, (rb, lb) in enumerate(zip(right, left)):
        attrs = ""
        if i == 0:
            attrs = (f"<attributes><divisions>{DIV}</divisions><key><fifths>0</fifths></key>"
                     "<time><beats>4</beats><beat-type>4</beat-type></time><staves>2</staves>"
                     "<clef number=\"1\"><sign>G</sign><line>2</line></clef>"
                     "<clef number=\"2\"><sign>F</sign><line>4</line></clef></attributes>"
                     f"<direction placement=\"above\"><direction-type><metronome><beat-unit>quarter</beat-unit>"
                     f"<per-minute>{tempo}</per-minute></metronome></direction-type><sound tempo=\"{tempo}\"/>"
                     "</direction>")
        back = f"<backup><duration>{4 * DIV}</duration></backup>"
        measures.append(f"<measure number=\"{i + 1}\">{attrs}{_notes_xml(rb, 1)}{back}{_notes_xml(lb, 2)}</measure>")
    xml = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
           "<score-partwise version=\"3.1\">"
           f"<work><work-title>{escape(title)}</work-title></work>"
           "<part-list><score-part id=\"P1\"><part-name>Piano</part-name></score-part></part-list>"
           f"<part id=\"P1\">{''.join(measures)}</part></score-partwise>\n")
    path.write_text(xml, encoding="utf-8")


def q(p):
    return (p, 2)


def h(p):
    return (p, 4)


def twinkle():
    a = [[q("C4"), q("C4"), q("G4"), q("G4")], [q("A4"), q("A4"), h("G4")],
         [q("F4"), q("F4"), q("E4"), q("E4")], [q("D4"), q("D4"), h("C4")]]
    b = [[q("G4"), q("G4"), q("F4"), q("F4")], [q("E4"), q("E4"), h("D4")]]
    right = a + b + b + a
    la = [[h("C3"), h("E3")], [h("F3"), h("E3")], [h("D3"), h("C3")], [h("G2"), h("C3")]]
    lb = [[h("E3"), h("D3")], [h("C3"), h("G2")]]
    left = la + lb + lb + la
    write_score(HERE / "twinkle_twinkle.musicxml", "Twinkle, Twinkle, Little Star", 100, right, left)


def ode_to_joy():
    p1 = [[q("E4"), q("E4"), q("F4"), q("G4")], [q("G4"), q("F4"), q("E4"), q("D4")],
          [q("C4"), q("C4"), q("D4"), q("E4")]]
    right = (p1 + [[("E4", 3), ("D4", 1), h("D4")]] + p1 + [[("D4", 3), ("C4", 1), h("C4")]])
    c, g = ("C3", "E3", "G3"), ("B2", "D3", "G3")
    left = [[h(c), h(c)], [h(g), h(g)], [h(c), h(c)], [h(g), h(g)],
            [h(c), h(c)], [h(g), h(g)], [h(c), h(c)], [h(g), h(c)]]
    write_score(HERE / "ode_to_joy.musicxml", "Ode to Joy", 110, right, left)


if __name__ == "__main__":
    twinkle()
    ode_to_joy()
    print(f"wrote examples to {HERE}")
