"""Fingerly web app: upload a piano score, watch the RL agent's fingering played on a piano.

    python webapp/server.py                 # then open http://127.0.0.1:8000
    python webapp/server.py --port 8080 --open

Standard library only (plus the project's own requirements). The page is served from
webapp/static; the score is fingered by the latest trained RL agent (see agent_runner.py).
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent))  # the fingerly package and evaluate.py

from agent_runner import CKPT, Fingerer  # noqa: E402
from score_io import Score, ScoreError, read_score  # noqa: E402

STATIC = HERE / "static"
EXAMPLES = HERE / "examples"
MAX_UPLOAD = 8 * 1024 * 1024
EXAMPLE_EXT = (".musicxml", ".xml", ".mxl", ".mid", ".midi", ".txt")


def score_json(score: Score, fingerer: Fingerer, refine: bool = False) -> dict:
    fingers, stats = fingerer.finger(score, refine)
    bars = []
    for b in score.bars:
        bars.append(dict(number=b.number, start_q=b.start_q, len_q=b.len_q, beats=b.beats, beat_type=b.beat_type,
                         start_s=score.seconds(b.start_q), end_s=score.seconds(b.start_q + b.len_q)))
    starts = [b.start_q for b in score.bars]
    notes = []
    for n, f in zip(score.notes, fingers):
        bar = max(0, next((k for k in range(len(starts) - 1, -1, -1) if starts[k] <= n.start_q + 1e-6), 0))
        notes.append(dict(pitch=n.pitch, start_q=n.start_q, dur_q=n.dur_q, start_s=score.seconds(n.start_q),
                          end_s=score.seconds(n.start_q + n.dur_q), staff=n.staff, step=n.step, alter=n.alter,
                          octave=n.octave, bar=bar, hand=f["hand"] if f else None, finger=f["finger"] if f else None))
    return dict(title=score.title, model=fingerer.label, source=score.source, estimated_bars=score.estimated_bars,
                warnings=score.warnings, stats=stats, bars=bars, notes=notes)


class Handler(BaseHTTPRequestHandler):
    fingerer: Fingerer = None  # set in main()
    refine: bool = True  # fine-tune on each piece unless ?refine=0 (or --no-refine)

    def log_message(self, fmt, *args):  # quieter console
        sys.stderr.write("  " + fmt % args + "\n")

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj).encode(), "application/json")

    def _finger(self, name: str, data: bytes):
        refine = self.refine and "refine=0" not in (urlparse(self.path).query or "")
        try:
            score = read_score(name, data)
            self._json(200, score_json(score, self.fingerer, refine))
        except ScoreError as e:
            self._json(400, dict(error=str(e)))
        except Exception as e:  # noqa: BLE001 - report, don't kill the server
            traceback.print_exc()
            self._json(500, dict(error=f"Something went wrong while fingering this score ({type(e).__name__}: {e})."))

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/":
            path = "/index.html"
        if path == "/api/info":
            label = self.fingerer.label + (f", {self.fingerer.refine_label}" if self.refine else "")
            return self._json(200, dict(model=label, refine=self.refine))
        if path == "/api/examples":
            names = sorted(p.name for p in EXAMPLES.iterdir() if p.suffix.lower() in EXAMPLE_EXT)
            return self._json(200, names)
        if path.startswith("/api/examples/"):
            f = (EXAMPLES / path[len("/api/examples/"):]).resolve()
            if f.parent != EXAMPLES or not f.is_file():
                return self._json(404, dict(error="no such example"))
            return self._finger(f.name, f.read_bytes())
        f = (STATIC / path.lstrip("/")).resolve()
        if STATIC not in f.parents or not f.is_file():
            return self._send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            ctype += "; charset=utf-8"
        self._send(200, f.read_bytes(), ctype)

    def do_POST(self):
        if urlparse(self.path).path != "/api/finger":
            return self._json(404, dict(error="not found"))
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return self._json(400, dict(error="The upload was empty."))
        if n > MAX_UPLOAD:
            return self._json(413, dict(error="That file is too big (8 MB at most)."))
        name = unquote(self.headers.get("X-Filename") or "score.musicxml")
        self._finger(name, self.rfile.read(n))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--open", action="store_true", help="open the page in the browser")
    ap.add_argument("--ckpt", type=Path, default=CKPT, help="default: runs/v2_r3_s0/best.pt")
    ap.add_argument("--no-refine", action="store_true", help="greedy policy only, no per-piece fine-tuning")
    args = ap.parse_args()

    Handler.fingerer = Fingerer(args.ckpt)
    Handler.refine = not args.no_refine
    print(f"model: {Handler.fingerer.label}")
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"Fingerly web app running at {url}  (Ctrl+C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
