# Generates assets/hero.svg: a terminal that types out who I am and what I've shipped, next to a
# small neural network with signals moving through it. Pure SVG (CSS + SMIL animation), no external
# fonts, images or services, so GitHub renders it directly and nothing can rate-limit or break.
# The card is dark with a transparent surround, so it works on GitHub's light and dark themes.
#
#   python tools/build_hero.py
import html
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "hero.svg"
W, H = 1000, 470
FONT = "ui-monospace, 'JetBrains Mono', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"

BG = "#0d1117"
BORDER = "#30363d"
DIM = "#8b949e"
TEXT = "#e6edf3"
GREEN = "#3fb950"
BLUE = "#58a6ff"
ORANGE = "#ff9a3c"
CYAN = "#5ad7ff"
PURPLE = "#d2a8ff"

# (kind, text, color). "cmd" lines are typed character by character; "out" lines appear at once.
LINES = [
    ("cmd", "whoami", None),
    ("out", "masood ahmed · ai engineer · islamabad (utc+5), remote", TEXT),
    ("cmd", "cat focus.txt", None),
    ("out", "llm agents · voice & speech · causal ml · evals that hold up", TEXT),
    ("cmd", "ls ~/shipped", None),
    ("out", "uplift-targeting/      roman-urdu-retrieval/", BLUE),
    ("out", "agentic-rag-evals/     realtime-voice-agent/", BLUE),
    ("out", "receipt-slm/           freight-rate-prediction/", BLUE),
    ("cmd", "head -1 papers.bib", None),
    ("out", "Roman Urdu Breaks Dense Retrieval (2026)", PURPLE),
    ("out", "doi:10.5281/zenodo.24384589", PURPLE),
]
X0, Y0, LH, FS = 40, 92, 31, 16.5
CHAR_T = 0.045  # seconds per typed character
PAUSE = 0.45  # pause after each command before its output


def terminal():
    parts, t = [], 0.6
    y = Y0
    for kind, text, color in LINES:
        if kind == "cmd":
            # one line of SVG: with white-space: pre, newlines between tspans would render as gaps
            line = (
                f'<text x="{X0}" y="{y}" class="t"><tspan fill="{GREEN}" class="c" '
                f'style="animation-delay:{t:.2f}s">❯</tspan>'
            )
            t += 0.15
            for ch in " " + text:
                line += f'<tspan class="c" style="animation-delay:{t:.2f}s">{html.escape(ch)}</tspan>'
                t += CHAR_T
            parts.append(line + "</text>")
            t += PAUSE
        else:
            parts.append(
                f'<text x="{X0}" y="{y}" class="t o" fill="{color}" '
                f'style="animation-delay:{t:.2f}s">{html.escape(text)}</text>'
            )
            t += 0.12
        y += LH
    # final prompt with a blinking cursor
    parts.append(
        f'<text x="{X0}" y="{y}" class="t"><tspan fill="{GREEN}" class="c" '
        f'style="animation-delay:{t:.2f}s">❯</tspan></text>'
    )
    parts.append(
        f'<rect x="{X0 + 20}" y="{y - 14}" width="9" height="18" fill="{TEXT}" class="cur" '
        f'style="animation-delay:{t:.2f}s"/>'
    )
    return "\n".join(parts), t


def network(start):
    rng = random.Random(7)
    layers = [4, 6, 6, 3]
    x0, x1 = 720, 950
    xs = [x0 + (x1 - x0) * i / (len(layers) - 1) for i in range(len(layers))]
    nodes = []
    for L, n in enumerate(layers):
        top, bot = 110, H - 80
        span = (bot - top) * (0.55 + 0.45 * n / max(layers))
        mid = (top + bot) / 2
        nodes.append([(xs[L], mid - span / 2 + span * i / max(n - 1, 1)) for i in range(n)])
    parts = ['<g class="net">']
    edges = []
    for L in range(len(layers) - 1):
        for a in nodes[L]:
            for b in nodes[L + 1]:
                edges.append((L, a, b))
                parts.append(
                    f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                    f'stroke="#27324a" stroke-width="1"/>'
                )
    # signals: a forward pass that repeats, layer by layer
    period = 3.6
    for L in range(len(layers) - 1):
        layer_edges = [e for e in edges if e[0] == L]
        for _, a, b in rng.sample(layer_edges, k=min(9, len(layer_edges))):
            color = ORANGE if rng.random() < 0.55 else BLUE
            begin = start + L * 0.9 + rng.random() * 0.35
            path = f"M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}"
            parts.append(
                f'<circle r="2.6" fill="{color}" opacity="0">'
                f'<animateMotion dur="{period}s" begin="{begin:.2f}s" repeatCount="indefinite" '
                f'keyPoints="0;1;1" keyTimes="0;0.25;1" calcMode="linear" path="{path}"/>'
                f'<animate attributeName="opacity" dur="{period}s" begin="{begin:.2f}s" '
                f'repeatCount="indefinite" values="0;1;1;0;0" keyTimes="0;0.02;0.22;0.26;1"/>'
                f"</circle>"
            )
    for L, col in enumerate(nodes):
        for i, (x, y) in enumerate(col):
            r = 6 if L in (0, len(layers) - 1) else 5.5
            delay = start + L * 0.9 + 0.8
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 5}" fill="{CYAN}" opacity="0">'
                f'<animate attributeName="opacity" dur="{period}s" begin="{delay:.2f}s" '
                f'repeatCount="indefinite" values="0;0.28;0;0" keyTimes="0;0.08;0.3;1"/></circle>'
            )
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#122033" stroke="{CYAN}" '
                f'stroke-width="1.4"/>'
            )
    labels = ["x", "h₁", "h₂", "ŷ"]
    for L, x in enumerate(xs):
        parts.append(
            f'<text x="{x:.1f}" y="{H - 40}" text-anchor="middle" class="lbl">{labels[L]}</text>'
        )
    parts.append("</g>")
    return "\n".join(parts)


def main():
    term, t_end = terminal()
    net = network(start=0.8)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Masood Ahmed, AI engineer: LLM agents, voice and speech, causal ML. Shipped: uplift-targeting, roman-urdu-retrieval, agentic-rag-evals, realtime-voice-agent, receipt-slm, freight-rate-prediction.">
<style>
  .t {{ font-family: {FONT}; font-size: {FS}px; fill: {TEXT}; white-space: pre; }}
  .lbl {{ font-family: {FONT}; font-size: 13px; fill: {DIM}; }}
  .title {{ font-family: {FONT}; font-size: 13px; fill: {DIM}; }}
  .c, .o {{ opacity: 0; animation: show 0.01s linear forwards; }}
  .cur {{ opacity: 0; animation: show 0.01s linear forwards, blink 1.05s steps(1) {t_end:.2f}s infinite; }}
  @keyframes show {{ to {{ opacity: 1; }} }}
  @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .c, .o, .cur {{ animation: none; opacity: 1; }}
  }}
</style>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<circle cx="36" cy="34" r="6.5" fill="#ff5f57"/><circle cx="58" cy="34" r="6.5" fill="#febc2e"/><circle cx="80" cy="34" r="6.5" fill="#28c840"/>
<text x="{W / 2}" y="39" text-anchor="middle" class="title">masood@lab: ~</text>
<line x1="8" y1="56" x2="{W - 8}" y2="56" stroke="{BORDER}"/>
<line x1="680" y1="76" x2="680" y2="{H - 30}" stroke="{BORDER}" stroke-dasharray="3 5"/>
{term}
{net}
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(OUT, round(len(svg) / 1024, 1), "KB, typing ends at", round(t_end, 1), "s")


if __name__ == "__main__":
    main()
