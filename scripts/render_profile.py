#!/usr/bin/env python3
"""Render the README and both theme cards: python scripts/render_profile.py.

Edit profile.json to update the content, then run this script. Standard library
only; all image data is embedded so GitHub can display each SVG independently.
Layout reference: Jitmisra/Jitmisra at 24dd71c93cf04a6877e0810a807dfa4a4035a131.
The reference's portrait, biography and achievements are not included.
"""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PROFILE = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
THEMES = {
    "dark": {
        "background": "#0d1117", "border": "#30363d", "muted": "#8b949e",
        "text": "#c9d1d9", "green": "#7ee88a", "cyan": "#5ad3e0",
        "gold": "#ecc86e", "rule": "#3f4c57", "chip": "#161b22",
        "gradient": ("#2FBF71", "#5ad3e0"),
    },
    "light": {
        "background": "#ffffff", "border": "#d0d7de", "muted": "#57606a",
        "text": "#24292f", "green": "#1a7f37", "cyan": "#0a7285",
        "gold": "#9a6700", "rule": "#d0d7de", "chip": "#f6f8fa",
        "gradient": ("#0a7d3b", "#0e7490"),
    },
}


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, color, size=13, weight=None, anchor=None):
    attrs = f'x="{x}" y="{y}" fill="{color}" font-size="{size}"'
    if weight:
        attrs += f' font-weight="{weight}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    return f'<text {attrs} xml:space="preserve">{esc(value)}</text>'


def card(theme):
    p = THEMES[theme]
    gradient = "pgd" if theme == "dark" else "pgl"
    terminal = f'{PROFILE["terminal_name"]}@{PROFILE["username"]} — neofetch'
    avatar = ROOT / PROFILE["avatar"]
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}[avatar.suffix.lower()]
    image_data = base64.b64encode(avatar.read_bytes()).decode("ascii")
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="753" height="542" viewBox="0 0 753 542" role="img" '
        'aria-labelledby="profile-title profile-description" '
        'font-family="\'JetBrains Mono\',\'SFMono-Regular\',Consolas,\'Liberation Mono\',monospace">',
        f'<title id="profile-title">{esc(PROFILE["name"])} — {esc(PROFILE["headline"])}</title>',
        f'<desc id="profile-description">{esc(PROFILE["accessible_summary"])}</desc>',
        '<defs>',
        f'<linearGradient id="{gradient}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{p["gradient"][0]}"/>'
        f'<stop offset="1" stop-color="{p["gradient"][1]}"/></linearGradient>',
        f'<clipPath id="avatar-{gradient}"><rect x="26" y="66" width="300" height="300" rx="22"/></clipPath>',
    ]
    if theme == "dark":
        out += [
            f'<filter id="glow-{gradient}" x="-60%" y="-60%" width="220%" height="220%">'
            '<feGaussianBlur stdDeviation="14" result="b"/>'
            '<feColorMatrix in="b" type="matrix" '
            'values="0 0 0 0 0.18  0 0 0 0 0.75  0 0 0 0 0.5  0 0 0 0.55 0"/></filter>'
        ]
    out += [
        '</defs>',
        f'<rect x="1" y="1" width="751" height="540" rx="16" fill="{p["background"]}" '
        f'stroke="{p["border"]}" stroke-width="1.4"/>',
    ]
    for x, color in [(28, "#ff5f56"), (48, "#ffbd2e"), (68, "#27c93f")]:
        out.append(f'<circle cx="{x}" cy="24" r="6" fill="{color}"/>')
    out += [
        f'<line x1="1" y1="45" x2="752" y2="45" stroke="{p["border"]}" stroke-width="1.2"/>',
        text(376.5, 27, terminal, p["muted"], anchor="middle"),
    ]
    if theme == "dark":
        out.append(f'<rect x="20" y="60" width="312" height="312" rx="26" fill="none" '
                   f'stroke="url(#{gradient})" stroke-width="10" filter="url(#glow-{gradient})" opacity="0.7"/>')
    else:
        out.append('<rect x="30" y="72" width="300" height="300" rx="22" fill="#000000" opacity="0.08"/>')
    out += [
        f'<image x="26" y="66" width="300" height="300" preserveAspectRatio="xMidYMid slice" '
        f'clip-path="url(#avatar-{gradient})" xlink:href="data:{mime};base64,{image_data}"/>',
        f'<rect x="26" y="66" width="300" height="300" rx="22" fill="none" '
        f'stroke="url(#{gradient})" stroke-width="3"/>',
    ]
    for row_number, badges in enumerate(PROFILE["badges"]):
        x, y = 26.0, 388 + row_number * 37
        for badge in badges:
            width = round(len(badge) * 6.9 + 28, 1)
            if x + width > 332:
                raise ValueError(f"Badge row does not fit: {badges}")
            out += [
                f'<rect x="{x}" y="{y}" width="{width}" height="27" rx="13.5" '
                f'fill="{p["chip"]}" stroke="url(#{gradient})" stroke-width="1.3"/>',
                text(round(x + width / 2, 1), y + 18, badge, p["text"], 11.5, "600", "middle"),
            ]
            x += width + 10

    name = PROFILE["terminal_name"]
    name_width = len(name) * 7.8
    out += [
        text(360, 79, name, p["green"], weight="700"),
        text(round(360 + name_width, 1), 79, "@", p["muted"]),
        text(round(367.8 + name_width, 1), 79, PROFILE["username"], p["cyan"], weight="700"),
        text(360, 94.2, PROFILE["headline"], p["muted"]),
        f'<line x1="376" y1="104.5" x2="688" y2="104.5" stroke="{p["rule"]}"/>',
    ]

    def rows(items, y):
        for index, (label, value, tone) in enumerate(items):
            # Keep every value inside the reference card's right-hand column.
            if len(label) > 9 or len(value) > 35:
                raise ValueError(f"Profile field is too long: {label}: {value}")
            baseline = round(y + index * 15.2, 1)
            out.extend([
                text(376, baseline, label, p["cyan"], weight="700"),
                text(455.6, baseline, value, p[tone],
                     weight="700" if tone in ("gold", "green") and y in (215.8, 307, 474.2) else None),
            ])

    def section(label, y, rule_x):
        out.extend([
            text(376, y, label, p["gold"], weight="700"),
            f'<line x1="{rule_x}" y1="{y - 5}" x2="690" y2="{y - 5}" stroke="{p["rule"]}"/>',
        ])

    rows(PROFILE["overview"], 124.6)
    rows(PROFILE["stack"], 215.8)
    rows(PROFILE["now"], 307)
    section("Contact", 352.6, 439)
    rows(PROFILE["contact"], 367.8)
    section("Highlights", 459, 463.4)
    rows(PROFILE["highlights"], 474.2)
    out.append("</svg>")
    return "\n".join(out) + "\n"


def readme():
    username = PROFILE["username"]
    bullets = "\n".join("- " + item for item in PROFILE["currently"])
    return f"""<!-- Layout reference: https://github.com/Jitmisra/Jitmisra
     Edit profile.json and run python scripts/render_profile.py to regenerate. -->
<div align="center">

<a href="https://github.com/{esc(username)}">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/dark_mode.svg">
    <img alt="{esc(PROFILE['accessible_summary'])}" src="./assets/light_mode.svg" width="860">
  </picture>
</a>

</div>

---

### 🌱 Currently

{bullets}

<div align="center">
<br/>
<i>“{esc(PROFILE["mission"])}”</i>
</div>
"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for theme_name in THEMES:
        (ASSETS / f"{theme_name}_mode.svg").write_text(card(theme_name), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")
    print("Generated README.md, assets/dark_mode.svg and assets/light_mode.svg")

