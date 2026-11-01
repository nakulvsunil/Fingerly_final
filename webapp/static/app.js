"use strict";
// Piano Finger Buddy: shows 2 bars of the uploaded score at a time with the RL agent's fingers,
// and plays them on a small piano with the two hands drawn above it.

const FINGER_NAMES = ["", "Thumb", "Pointer", "Middle", "Ring", "Pinky"];
const css = getComputedStyle(document.documentElement);
const FINGER_COLORS = [null, 1, 2, 3, 4, 5].map((f) => (f ? css.getPropertyValue(`--f${f}`).trim() : "#999"));
const STEPS = "CDEFGAB";
const BLACK_PCS = new Set([1, 3, 6, 8, 10]);
const NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
const BARS_PER_PAGE = 2;

const $ = (id) => document.getElementById(id);
const el = {
  upload: $("upload"), drop: $("drop"), file: $("file"), examples: $("examples"), loading: $("loading"),
  error: $("error"), player: $("player"), title: $("title"), pageLabel: $("pageLabel"), warnings: $("warnings"),
  score: $("score"), prevPage: $("prevPage"), nextPage: $("nextPage"), seek: $("seek"), pageDots: $("pageDots"),
  play: $("play"), stepBack: $("stepBack"), stepFwd: $("stepFwd"), speed: $("speed"), speedOut: $("speedOut"),
  loopPage: $("loopPage"), handR: $("handR"), handL: $("handL"), sound: $("sound"), names: $("names"),
  piano: $("piano"), now: $("now"), legend: $("legend"), modelInfo: $("modelInfo"), newSong: $("newSong"),
  handL_svg: $("handLsvg"), handR_svg: $("handRsvg"),
};

// ------------------------------------------------------------------ state
const S = {
  data: null, notes: [], bars: [], groups: [], songEnd: 0,
  t: 0, playing: false, last: 0, next: 0, held: null,
  page: -1, activeKey: "", noteEls: new Map(), keyEls: new Map(),
};

const handOf = (n) => n.hand || (n.staff === 1 ? "R" : "L");
const handOn = (h) => (h === "R" ? el.handR.checked : el.handL.checked);
const speed = () => parseFloat(el.speed.value);
const pages = () => Math.ceil(S.bars.length / BARS_PER_PAGE);
const colorOf = (n) => FINGER_COLORS[n.finger || 0];
const pitchName = (p) => NAMES[p % 12] + (Math.floor(p / 12) - 1);

// ------------------------------------------------------------------ upload
async function loadExamples() {
  try {
    const names = await (await fetch("/api/examples")).json();
    el.examples.innerHTML = "";
    for (const name of names) {
      const b = document.createElement("button");
      b.className = "btn example";
      const pretty = name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      b.textContent = (/twinkle/i.test(name) ? "⭐ " : /joy/i.test(name) ? "🎉 " : "🎵 ") + pretty;
      b.onclick = () => request(fetch(`/api/examples/${encodeURIComponent(name)}${refineQuery()}`));
      el.examples.appendChild(b);
    }
  } catch (e) { /* examples are optional */ }
}

function refineQuery() {
  return $("refine") && !$("refine").checked ? "?refine=0" : "";
}

function uploadFile(file) {
  if (!file) return;
  request(fetch(`/api/finger${refineQuery()}`, { method: "POST", body: file, headers: { "X-Filename": encodeURIComponent(file.name) } }));
}

async function request(promise) {
  el.error.hidden = true;
  el.loading.hidden = false;
  const lt = $("loadingText");
  if (lt) lt.textContent = refineQuery() ? "The robot pianist is working out the fingers…"
                                         : "The robot pianist is practising this piece… (up to about 1½ minutes)";
  try {
    const res = await promise;
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || `Error ${res.status}`);
    start(body);
  } catch (e) {
    el.error.textContent = "😕 " + (e.message || "Something went wrong.");
    el.error.hidden = false;
  } finally {
    el.loading.hidden = true;
    el.file.value = "";
  }
}

el.file.addEventListener("change", () => uploadFile(el.file.files[0]));
el.drop.addEventListener("click", (e) => { if (e.target === el.drop || !e.target.closest("label")) el.file.click(); });
el.drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); el.file.click(); } });
["dragenter", "dragover"].forEach((ev) => el.drop.addEventListener(ev, (e) => { e.preventDefault(); el.drop.classList.add("over"); }));
["dragleave", "drop"].forEach((ev) => el.drop.addEventListener(ev, (e) => { e.preventDefault(); el.drop.classList.remove("over"); }));
el.drop.addEventListener("drop", (e) => uploadFile(e.dataTransfer.files[0]));
el.newSong.onclick = () => { pause(); el.player.hidden = true; el.upload.hidden = false; window.scrollTo({ top: 0, behavior: "smooth" }); };

// ------------------------------------------------------------------ start a song
function start(data) {
  pause();
  S.data = data;
  S.notes = data.notes.map((n, i) => ({ ...n, i }));
  S.bars = data.bars;
  S.songEnd = Math.max(...S.notes.map((n) => n.end_s), 0);
  const byT = new Map();
  for (const n of S.notes) {
    const k = Math.round(n.start_s * 1000);
    if (!byT.has(k)) byT.set(k, { t: n.start_s, notes: [] });
    byT.get(k).notes.push(n);
  }
  S.groups = [...byT.values()].sort((a, b) => a.t - b.t);
  S.t = 0; S.next = 0; S.held = null; S.page = -1; S.activeKey = "";

  el.title.textContent = data.title;
  el.warnings.innerHTML = data.warnings.map((w) => `<div class="warn">ℹ️ ${escapeHtml(w)}</div>`).join("");
  const st = data.stats;
  el.modelInfo.textContent = `Fingering by the RL agent ${data.model}. ${st.fingered} of ${st.total} notes fingered.`;
  el.seek.max = S.songEnd.toFixed(2);
  buildPiano();
  buildDots();
  el.upload.hidden = true;
  el.player.hidden = false;
  update(true);
  el.player.scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// ------------------------------------------------------------------ score drawing (2 bars per page)
const W = 1000, H = 380;
const X0 = 100, X1 = 985, BAR_W = (X1 - X0) / BARS_PER_PAGE;
const TOP1 = 110, TOP2 = 230; // top lines of the treble and bass staves
const diatonic = (n) => n.octave * 7 + STEPS.indexOf(n.step);
const yOf = (d, staff) => (staff === 1 ? TOP1 + 40 - (d - 30) * 5 : TOP2 + 40 - (d - 18) * 5);
const barX = (k) => X0 + k * BAR_W;
const xOf = (q, bar, k) => barX(k) + 26 + ((q - bar.start_q) / bar.len_q) * (BAR_W - 44);

function kind(dq) {
  if (dq >= 3.5) return { hollow: true, stem: false, flags: 0, dot: dq >= 5.5 };
  if (dq >= 1.75) return { hollow: true, stem: true, flags: 0, dot: dq >= 2.75 };
  if (dq >= 0.875) return { hollow: false, stem: true, flags: 0, dot: dq >= 1.375 };
  if (dq >= 0.4375) return { hollow: false, stem: true, flags: 1, dot: dq >= 0.6875 };
  return { hollow: false, stem: true, flags: 2, dot: false };
}

function ledgers(d, staff, x) {
  const out = [];
  const lo = staff === 1 ? 28 : 16, hi = staff === 1 ? 40 : 28; // first ledger below / above the staff
  if (d <= lo) for (let L = lo; L >= d; L -= 2) out.push(L);
  if (d >= hi) for (let L = hi; L <= d; L += 2) out.push(L);
  return out.map((L) => `<line class="ledger" x1="${x - 11}" x2="${x + 11}" y1="${yOf(L, staff)}" y2="${yOf(L, staff)}"/>`).join("");
}

function renderScore(page) {
  const bars = S.bars.slice(page * BARS_PER_PAGE, page * BARS_PER_PAGE + BARS_PER_PAGE);
  const first = page * BARS_PER_PAGE;
  const svg = [];
  // staves, clefs, time signature
  for (const top of [TOP1, TOP2]) {
    for (let k = 0; k < 5; k++) svg.push(`<line class="staff-line" x1="12" x2="${barX(bars.length)}" y1="${top + k * 10}" y2="${top + k * 10}"/>`);
  }
  svg.push(`<line class="bar-line" x1="12" x2="12" y1="${TOP1}" y2="${TOP2 + 40}"/>`);
  svg.push(`<text class="clef" x="18" y="${TOP1 + 37}" font-size="58">𝄞</text>`);
  svg.push(`<text class="clef" x="20" y="${TOP2 + 33}" font-size="44">𝄢</text>`);
  svg.push(`<text class="staff-name" x="14" y="${TOP1 - 62}">Right hand ✋</text>`);
  svg.push(`<text class="staff-name" x="14" y="${TOP2 + 108}">Left hand 🤚</text>`);
  if (bars.length) {
    const b = bars[0];
    for (const top of [TOP1, TOP2]) {
      svg.push(`<text class="timesig" x="78" y="${top + 19}" text-anchor="middle">${b.beats}</text>`);
      svg.push(`<text class="timesig" x="78" y="${top + 39}" text-anchor="middle">${b.beat_type}</text>`);
    }
  }
  bars.forEach((b, k) => {
    const x = barX(k + 1);
    const final = first + k === S.bars.length - 1;
    svg.push(`<line class="bar-line" x1="${x}" x2="${x}" y1="${TOP1}" y2="${TOP2 + 40}" ${final ? 'style="stroke-width:4"' : ""}/>`);
    svg.push(`<text class="bar-num" x="${barX(k) + 6}" y="${TOP1 - 8}">${S.data.estimated_bars ? "~" : ""}${b.number}</text>`);
  });

  // notes of this page, grouped by staff + onset (shared stem, stacked fingers)
  const pageNotes = S.notes.filter((n) => n.bar >= first && n.bar < first + bars.length);
  const chords = new Map();
  for (const n of pageNotes) {
    const key = `${n.staff}|${Math.round(n.start_q * 1000)}`;
    if (!chords.has(key)) chords.set(key, []);
    chords.get(key).push(n);
  }
  for (const group of chords.values()) {
    const n0 = group[0];
    const k = n0.bar - first;
    const x = xOf(n0.start_q, bars[k], k);
    const staff = n0.staff;
    group.sort((a, b) => diatonic(a) - diatonic(b) || a.pitch - b.pitch);
    const ds = group.map(diatonic);
    const mid = staff === 1 ? 34 : 22;
    const up = ds.reduce((a, b) => a + b, 0) / ds.length < mid;
    const kd = kind(Math.max(...group.map((n) => n.dur_q)));
    const shifted = group.map(() => false);
    for (let i = 1; i < group.length; i++) if (ds[i] - ds[i - 1] <= 1 && !shifted[i - 1]) shifted[i] = true;
    const ys = ds.map((d) => yOf(d, staff));
    // stem + flags
    let stemEnd = null;
    if (kd.stem) {
      const sx = up ? x + 6.5 : x - 6.5;
      const yA = up ? Math.max(...ys) : Math.min(...ys);
      stemEnd = up ? Math.min(...ys) - 34 : Math.max(...ys) + 34;
      let s = `<g class="note-stem"><line class="stem" style="stroke:var(--ink);stroke-width:1.6" x1="${sx}" x2="${sx}" y1="${yA}" y2="${stemEnd}"/>`;
      for (let f = 0; f < kd.flags; f++) {
        const y = stemEnd + (up ? f * 9 : -f * 9);
        s += `<path style="stroke:var(--ink);stroke-width:2;fill:none" d="M${sx} ${y} q 12 ${up ? 8 : -8} 9 ${up ? 22 : -22}"/>`;
      }
      svg.push(s + "</g>");
    }
    // fingers stacked above the treble staff / below the bass staff
    const fy0 = staff === 1
      ? Math.min(TOP1 - 4, ...ys, stemEnd !== null && up ? stemEnd : Infinity) - 16
      : Math.max(TOP2 + 44, ...ys, stemEnd !== null && !up ? stemEnd : -Infinity) + 16;
    group.forEach((n, i) => {
      const hx = x + (shifted[i] ? (up ? 13 : -13) : 0);
      const y = ys[i];
      const fy = staff === 1 ? fy0 - i * 24 : fy0 + (group.length - 1 - i) * 24;
      const fill = n.finger ? (kd.hollow ? "#fff" : "var(--ink)") : "#bbb";
      const acc = n.alter ? `<text class="acc" x="${hx - 22}" y="${y + 6}">${{ 1: "♯", "-1": "♭", 2: "𝄪", "-2": "♭♭" }[n.alter] || ""}</text>` : "";
      const dot = kd.dot ? `<circle cx="${hx + 12}" cy="${ds[i] % 2 === 0 ? y - 5 : y}" r="2.4" fill="var(--ink)"/>` : "";
      let fing = "";
      if (n.finger) {
        const badge = handOf(n) !== (staff === 1 ? "R" : "L") ? `<text class="badge" x="${x + 15}" y="${fy - 8}">${handOf(n)}</text>` : "";
        fing = `<g class="fing"><circle cx="${x}" cy="${fy}" r="10" fill="${colorOf(n)}"/><text x="${x}" y="${fy + 1}">${n.finger}</text>${badge}</g>`;
      }
      svg.push(`<g class="note" data-i="${n.i}" style="--fc:${colorOf(n)}">${ledgers(ds[i], staff, hx)}${acc}` +
        `<ellipse class="head" cx="${hx}" cy="${y}" rx="6.8" ry="5" transform="rotate(-20 ${hx} ${y})" fill="${fill}"/>${dot}${fing}` +
        `<title>${pitchName(n.pitch)}${n.finger ? ` · ${handOf(n) === "R" ? "right" : "left"} hand finger ${n.finger} (${FINGER_NAMES[n.finger]})` : ""}</title></g>`);
    });
  }
  svg.push(`<line id="playhead" class="playhead" x1="-10" x2="-10" y1="${TOP1 - 14}" y2="${TOP2 + 54}"/>`);
  el.score.innerHTML = svg.join("");
  S.noteEls = new Map([...el.score.querySelectorAll(".note")].map((g) => [+g.dataset.i, g]));
  S.page = page;
  S.activeKey = "";
  // labels and page buttons
  const a = bars[0]?.number ?? 1, b = bars[bars.length - 1]?.number ?? a;
  el.pageLabel.textContent = `${a === b ? `Bar ${a}` : `Bars ${a}–${b}`} of ${S.bars.length}` + (S.data.estimated_bars ? " (estimated)" : "");
  el.prevPage.disabled = page === 0;
  el.nextPage.disabled = page >= pages() - 1;
  [...el.pageDots.children].forEach((d, k) => d.classList.toggle("on", k === page));
}

el.score.addEventListener("click", (e) => {
  const g = e.target.closest(".note");
  if (!g) return;
  const n = S.notes[+g.dataset.i];
  const grp = S.groups.find((x) => Math.abs(x.t - n.start_s) < 1e-6);
  pause();
  showGroup(grp);
});

function buildDots() {
  el.pageDots.innerHTML = "";
  for (let p = 0; p < pages(); p++) {
    const d = document.createElement("button");
    d.setAttribute("aria-label", `Bars ${p * BARS_PER_PAGE + 1}–${p * BARS_PER_PAGE + BARS_PER_PAGE}`);
    d.onclick = () => goPage(p);
    el.pageDots.appendChild(d);
  }
}

// ------------------------------------------------------------------ piano + hands
function buildPiano() {
  const ps = S.notes.map((n) => n.pitch);
  let lo = Math.min(...ps), hi = Math.max(...ps);
  lo -= lo % 12;
  hi += 11 - (hi % 12);
  while (hi - lo + 1 < 24) { lo = Math.max(21, lo - 12); if (hi - lo + 1 < 24) hi += 12; }
  const whites = [];
  for (let p = lo; p <= hi; p++) if (!BLACK_PCS.has(p % 12)) whites.push(p);
  const ww = 100 / whites.length;
  el.piano.innerHTML = "";
  el.piano.style.minWidth = `${whites.length * 26}px`;
  S.keyEls = new Map();
  whites.forEach((p) => {
    const k = document.createElement("div");
    k.className = "wkey";
    k.innerHTML = `<span class="key-name${p === 60 ? " c4" : ""}">${p === 60 ? "C4" : NAMES[p % 12]}</span><span class="key-tag"></span>`;
    k.onpointerdown = () => tone(p, 0.6, true);
    el.piano.appendChild(k);
    S.keyEls.set(p, k);
  });
  for (let p = lo; p <= hi; p++) {
    if (!BLACK_PCS.has(p % 12)) continue;
    const wi = whites.indexOf(p - 1);
    const k = document.createElement("div");
    k.className = "bkey";
    k.style.left = `${(wi + 1) * ww - ww * 0.31}%`;
    k.style.width = `${ww * 0.62}%`;
    k.innerHTML = `<span class="key-tag"></span>`;
    k.onpointerdown = () => tone(p, 0.6, true);
    el.piano.appendChild(k);
    S.keyEls.set(p, k);
  }
  el.piano.classList.toggle("names", el.names.checked);
}

function drawHand(svg, hand) {
  // right hand seen from above: thumb on the left; the left hand is its mirror image
  const fingers = [[1, 8, 104, 34, 66], [2, 46, 30, 32, 104], [3, 84, 14, 32, 114], [4, 122, 28, 32, 104], [5, 158, 58, 30, 80]];
  let s = "";
  for (const [f, x0, y, w, h] of fingers) {
    const x = hand === "R" ? x0 : 200 - x0 - w;
    s += `<g class="finger" data-f="${f}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${w / 2}"/>` +
      `<text x="${x + w / 2}" y="${y + 24}">${f}</text></g>`;
  }
  s += `<rect class="palm" x="34" y="112" width="132" height="92" rx="34"/>`;
  s += `<text x="100" y="168" text-anchor="middle" font-size="30" font-weight="900" fill="#d29b74">${hand}</text>`;
  svg.innerHTML = s;
}

function buildLegend() {
  el.legend.innerHTML = [1, 2, 3, 4, 5].map((f) => `<span><b style="background:${FINGER_COLORS[f]}">${f}</b>${FINGER_NAMES[f]}</span>`).join("");
}

// ------------------------------------------------------------------ sound
let actx = null, master = null;
function audio() {
  if (!actx) {
    actx = new (window.AudioContext || window.webkitAudioContext)();
    master = actx.createGain();
    master.gain.value = 0.2;
    const comp = actx.createDynamicsCompressor();
    master.connect(comp).connect(actx.destination);
  }
  if (actx.state === "suspended") actx.resume();
  return actx;
}

function tone(pitch, dur, force = false) {
  if (!el.sound.checked && !force) return;
  const c = audio();
  const f = 440 * 2 ** ((pitch - 69) / 12);
  const t0 = c.currentTime + 0.005;
  const end = t0 + Math.max(0.12, Math.min(dur, 4));
  const g = c.createGain();
  g.gain.setValueAtTime(0, t0);
  g.gain.linearRampToValueAtTime(1, t0 + 0.008);
  g.gain.exponentialRampToValueAtTime(0.3, t0 + 0.35);
  g.gain.setTargetAtTime(0.0001, end, 0.07);
  const lp = c.createBiquadFilter();
  lp.type = "lowpass";
  lp.frequency.value = Math.min(9000, f * 6);
  lp.connect(g).connect(master);
  for (const [mult, type, amp] of [[1, "triangle", 0.8], [2, "sine", 0.25], [3, "sine", 0.07]]) {
    const o = c.createOscillator(), og = c.createGain();
    o.type = type;
    o.frequency.value = f * mult;
    og.gain.value = amp;
    o.connect(og).connect(lp);
    o.start(t0);
    o.stop(end + 0.6);
  }
}

// ------------------------------------------------------------------ playback
function barAt(t) {
  let k = 0;
  for (let i = 0; i < S.bars.length; i++) if (S.bars[i].start_s <= t + 1e-6) k = i;
  return k;
}

function lowerBound(t) {
  let lo = 0, hi = S.notes.length;
  while (lo < hi) { const m = (lo + hi) >> 1; if (S.notes[m].start_s < t - 1e-6) lo = m + 1; else hi = m; }
  return lo;
}

function setTime(t) {
  S.t = Math.max(0, Math.min(t, S.songEnd));
  S.next = lowerBound(S.t);
}

function play() {
  if (!S.data) return;
  audio();
  if (S.t >= S.songEnd - 0.01) setTime(0);
  S.held = null;
  S.next = lowerBound(S.t);
  S.playing = true;
  S.last = performance.now();
  el.play.textContent = "⏸";
  el.play.setAttribute("aria-label", "Pause");
  requestAnimationFrame(frame);
}

function pause() {
  S.playing = false;
  el.play.textContent = "▶";
  el.play.setAttribute("aria-label", "Play");
}

function pageSpan(p) {
  const a = S.bars[p * BARS_PER_PAGE], b = S.bars[Math.min(S.bars.length, (p + 1) * BARS_PER_PAGE) - 1];
  return [a.start_s, b.end_s];
}

function frame(now) {
  if (!S.playing) return;
  const dt = Math.min(0.1, (now - S.last) / 1000) * speed();
  S.last = now;
  const page = Math.floor(barAt(S.t) / BARS_PER_PAGE);
  S.t += dt;
  if (el.loopPage.checked) {
    const [a, b] = pageSpan(page);
    if (S.t >= b) setTime(a);
  }
  while (S.next < S.notes.length && S.notes[S.next].start_s < S.t) {
    const n = S.notes[S.next++];
    if (handOn(handOf(n))) tone(n.pitch, (n.end_s - n.start_s) / speed());
  }
  if (S.t >= S.songEnd + 0.4) {
    S.t = S.songEnd;
    pause();
  }
  update();
  if (S.playing) requestAnimationFrame(frame);
}

function showGroup(g) {
  if (!g) return;
  setTime(g.t);
  S.held = g.notes.filter((n) => handOn(handOf(n)));
  for (const n of S.held) tone(n.pitch, Math.min(1.5, (n.end_s - n.start_s) / speed()));
  update();
}

function stepBy(dir) {
  pause();
  const ok = (g) => g.notes.some((n) => handOn(handOf(n)));
  if (dir > 0) showGroup(S.groups.find((g) => g.t > S.t + 1e-6 && ok(g)) || (S.held ? null : S.groups.find(ok)));
  else showGroup([...S.groups].reverse().find((g) => g.t < S.t - 1e-6 && ok(g)));
}

function goPage(p) {
  p = Math.max(0, Math.min(pages() - 1, p));
  setTime(S.bars[p * BARS_PER_PAGE].start_s);
  S.held = null;
  if (!S.playing) {
    const [a, b] = pageSpan(p);
    const g = S.groups.find((x) => x.t >= a - 1e-6 && x.t < b && x.notes.some((n) => handOn(handOf(n))));
    if (g) { setTime(g.t); S.held = g.notes.filter((n) => handOn(handOf(n))); }
  }
  update();
}

// ------------------------------------------------------------------ view update
function activeNotes() {
  if (S.held && !S.playing) return S.held;
  return S.notes.filter((n) => n.start_s <= S.t + 1e-6 && S.t < n.end_s && handOn(handOf(n)));
}

function update(force = false) {
  const page = Math.floor(barAt(S.t) / BARS_PER_PAGE);
  if (page !== S.page || force) renderScore(page);
  const act = activeNotes();
  const key = act.map((n) => n.i).join(",");
  if (key !== S.activeKey || force) {
    S.activeKey = key;
    const on = new Set(act.map((n) => n.i));
    for (const [i, g] of S.noteEls) {
      const n = S.notes[i];
      g.classList.toggle("on", on.has(i));
      g.classList.toggle("past", !on.has(i) && n.end_s <= S.t);
      g.classList.toggle("muted", !handOn(handOf(n)));
    }
    for (const k of S.keyEls.values()) k.classList.remove("on");
    for (const n of act) {
      const k = S.keyEls.get(n.pitch);
      if (!k) continue;
      k.classList.add("on");
      k.style.setProperty("--fc", colorOf(n));
      k.querySelector(".key-tag").textContent = n.finger || "?";
      k.title = `${handOf(n) === "R" ? "Right" : "Left"} hand, finger ${n.finger}`;
    }
    for (const [hand, svg] of [["L", el.handL_svg], ["R", el.handR_svg]]) {
      for (const g of svg.querySelectorAll(".finger")) {
        const n = act.find((m) => handOf(m) === hand && m.finger === +g.dataset.f);
        g.classList.toggle("on", !!n);
        if (n) g.style.setProperty("--fc", colorOf(n));
      }
    }
    el.now.innerHTML = act.length ? describe(act)
      : (S.t === 0 && !S.playing ? "Press ▶ to start, or ⏭ to go one note at a time." : "&nbsp;");
  }
  // playhead
  const bi = barAt(S.t), b = S.bars[bi], k = bi - S.page * BARS_PER_PAGE;
  const ph = document.getElementById("playhead");
  if (ph && b && k >= 0 && k < BARS_PER_PAGE) {
    const frac = Math.max(0, Math.min(1, (S.t - b.start_s) / Math.max(1e-6, b.end_s - b.start_s)));
    const x = xOf(b.start_q + frac * b.len_q, b, k);
    ph.setAttribute("x1", x); ph.setAttribute("x2", x);
  }
  if (document.activeElement !== el.seek) el.seek.value = S.t.toFixed(2);
}

function describe(act) {
  const rows = [];
  for (const hand of ["R", "L"]) {
    const ns = act.filter((n) => handOf(n) === hand).sort((a, b) => b.pitch - a.pitch);
    if (!ns.length) continue;
    const pills = ns.map((n) => `<span class="pill" style="background:${colorOf(n)}">${n.finger ?? "?"} ${n.finger ? FINGER_NAMES[n.finger] : ""} · ${pitchName(n.pitch)}</span>`).join("");
    rows.push(`<div>${hand === "R" ? "Right ✋" : "Left 🤚"} ${pills}</div>`);
  }
  return rows.join("");
}

// ------------------------------------------------------------------ controls
el.play.onclick = () => (S.playing ? pause() : play());
el.stepFwd.onclick = () => stepBy(1);
el.stepBack.onclick = () => stepBy(-1);
el.prevPage.onclick = () => goPage(S.page - 1);
el.nextPage.onclick = () => goPage(S.page + 1);
el.speed.oninput = () => { el.speedOut.textContent = `${Math.round(speed() * 100)}%`; };
el.seek.oninput = () => { setTime(parseFloat(el.seek.value)); S.held = null; update(); };
el.names.onchange = () => el.piano.classList.toggle("names", el.names.checked);
[el.handR, el.handL].forEach((c) => (c.onchange = () => { S.held = S.held && S.held.filter((n) => handOn(handOf(n))); update(true); }));

document.addEventListener("keydown", (e) => {
  if (el.player.hidden) return;
  // a focused button / checkbox / slider already handles these keys itself
  if (e.target.closest("button, input, select, textarea, summary") && (e.key === " " || e.target.type === "range")) return;
  const map = { " ": () => (S.playing ? pause() : play()), ArrowRight: () => stepBy(1), ArrowLeft: () => stepBy(-1),
    PageDown: () => goPage(S.page + 1), PageUp: () => goPage(S.page - 1) };
  if (map[e.key]) { e.preventDefault(); map[e.key](); }
});

drawHand(el.handL_svg, "L");
drawHand(el.handR_svg, "R");
buildLegend();
loadExamples();
// ?example=<file> opens an example straight away; &t=<seconds> starts there
const params = new URLSearchParams(location.search);
if (params.get("example")) {
  request(fetch(`/api/examples/${encodeURIComponent(params.get("example"))}`)).then(() => {
    if (params.get("t") && S.data) { setTime(parseFloat(params.get("t"))); S.held = null; update(true); }
  });
}
fetch("/api/info").then((r) => r.json()).then((d) => { el.modelInfo.textContent = `Fingering by the RL agent ${d.model}.`; }).catch(() => {});
