"""Genera dist/top-langs.svg (tema oscuro) con los lenguajes de los repos propios."""
import json
import os
import urllib.request
from html import escape

USER = os.environ["GITHUB_USER"]
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Colores de GitHub Linguist
COLORS = {
    "HTML": "#e34c26", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "CSS": "#563d7c", "Java": "#b07219", "C++": "#f34b7d", "C#": "#178600",
    "Batchfile": "#C1F12E", "TypeScript": "#3178c6", "PHP": "#4F5D95",
}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


totals = {}
for repo in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"):
    if repo["fork"]:
        continue
    for lang, size in get(repo["languages_url"]).items():
        totals[lang] = totals.get(lang, 0) + size

top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
total = sum(totals.values()) or 1

W, BAR_X, BAR_W = 420, 25, 370
rows = []
x = BAR_X
for lang, size in top:
    w = BAR_W * size / total
    rows.append(f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="10" fill="{COLORS.get(lang, "#8b949e")}"/>')
    x += w

legend = []
for i, (lang, size) in enumerate(top):
    col, row = i % 2, i // 2
    lx, ly = BAR_X + col * 190, 38 + row * 24
    legend.append(
        f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{COLORS.get(lang, "#8b949e")}"/>'
        f'<text x="{lx + 16}" y="{ly}" class="t">{escape(lang)} {100 * size / total:.1f}%</text>'
    )

height = 100 + ((len(top) + 1) // 2) * 24
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}">
<style>
.h{{font:600 18px 'Segoe UI',Ubuntu,sans-serif;fill:#2ea44f}}
.t{{font:400 13px 'Segoe UI',Ubuntu,sans-serif;fill:#c9d1d9}}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="6" fill="#0d1117" stroke="#30363d"/>
<text x="25" y="35" class="h">Lenguajes más usados</text>
<g transform="translate(0,52)">
<clipPath id="c"><rect x="{BAR_X}" y="0" width="{BAR_W}" height="10" rx="5"/></clipPath>
<g clip-path="url(#c)">{"".join(rows)}</g>
</g>
<g transform="translate(0,66)">{"".join(legend)}</g>
</svg>'''

os.makedirs("dist", exist_ok=True)
with open("dist/top-langs.svg", "w", encoding="utf-8") as f:
    f.write(svg)
