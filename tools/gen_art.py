#!/usr/bin/env python3
"""
Procedural scenery generator for the Andamana tourism site.

Builds cinematic, layered SVG seascapes - limestone karst towers, hazy
depth-of-field ridges, reflective water, palm silhouettes and a film grade -
so the site ships with its own artwork instead of hotlinking stock photos.

    python3 tools/gen_art.py             # write every scene to assets/img/
    python3 tools/gen_art.py --list      # print the scene manifest
    python3 tools/gen_art.py --only hero-phiphi

Scenes are deterministic: a given name always renders identically, so
regenerating never churns the repository.
"""

from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "img")


# --------------------------------------------------------------------------
# colour
# --------------------------------------------------------------------------

def rgba(color: str, alpha: float) -> str:
    c = color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{round(alpha, 3)})"


def mix(a: str, b: str, t: float) -> str:
    a, b = a.lstrip("#"), b.lstrip("#")
    t = max(0.0, min(1.0, t))
    out = ""
    for i in (0, 2, 4):
        ca, cb = int(a[i:i + 2], 16), int(b[i:i + 2], 16)
        out += f"{round(ca + (cb - ca) * t):02x}"
    return "#" + out


@dataclass(frozen=True)
class Palette:
    key: str
    sky: tuple[str, ...]      # zenith -> horizon
    glow: str                 # sun / moon bloom
    glow_a: float
    haze: str                 # atmospheric scatter
    rock: str                 # base limestone
    foliage: str
    water: tuple[str, str]    # horizon, foreground
    shallow: str
    foam: str
    ink: str                  # silhouettes
    grade: str                # colour-grade wash
    sun: tuple[float, float]  # position 0..1


PALETTES: dict[str, Palette] = {
    "lagoon": Palette(
        "lagoon",
        sky=("#071b23", "#0d323c", "#1c5c64", "#57a8a4", "#a9dcd3"),
        glow="#e8fff8", glow_a=0.34, haze="#8ecac4",
        rock="#22484c", foliage="#12362c",
        water=("#63c6c1", "#04222b"), shallow="#8ceadb", foam="#f2fffc",
        ink="#04100f", grade="#0e5f6b", sun=(0.68, 0.22),
    ),
    "ember": Palette(
        "ember",
        sky=("#160b12", "#3d1622", "#8a3524", "#d97a3f", "#f4c07a"),
        glow="#ffe0ad", glow_a=0.46, haze="#cd7748",
        rock="#4a2c2b", foliage="#2b1a18",
        water=("#d9924f", "#150c12"), shallow="#e9b880", foam="#ffe9cd",
        ink="#0b0508", grade="#8c3f22", sun=(0.31, 0.40),
    ),
    "abyss": Palette(
        "abyss",
        sky=("#03060d", "#071120", "#0f2a41", "#255d7c", "#79b3c9"),
        glow="#d8ecff", glow_a=0.26, haze="#4c86a2",
        rock="#1b3947", foliage="#0d2a2b",
        water=("#3d8fa0", "#020f16"), shallow="#54b3b8", foam="#dcf1f8",
        ink="#01070b", grade="#0d3a55", sun=(0.24, 0.16),
    ),
    "jade": Palette(
        "jade",
        sky=("#0a1513", "#153027", "#2d5c47", "#6ba382", "#bcd9c1"),
        glow="#f0fbe9", glow_a=0.36, haze="#9cc0a6",
        rock="#2c4f43", foliage="#153629",
        water=("#7fbda6", "#07211d"), shallow="#a5dcc1", foam="#f2fbf5",
        ink="#040b09", grade="#1d5c47", sun=(0.56, 0.18),
    ),
    "dawn": Palette(
        "dawn",
        sky=("#150e1c", "#361a33", "#77324e", "#c46b6c", "#f0ae96"),
        glow="#ffe6d9", glow_a=0.40, haze="#c9808f",
        rock="#43303f", foliage="#20203a",
        water=("#d99a95", "#120c19"), shallow="#f2c2b2", foam="#fff2ea",
        ink="#06040e", grade="#7a3550", sun=(0.40, 0.34),
    ),
    "gold": Palette(
        "gold",
        sky=("#100c08", "#302113", "#775021", "#c99348", "#f0cf8e"),
        glow="#fff0c2", glow_a=0.44, haze="#c99a5c",
        rock="#4a3c28", foliage="#26261a",
        water=("#d3aa66", "#120e07"), shallow="#e8cf95", foam="#fff6dd",
        ink="#070503", grade="#8a641f", sun=(0.63, 0.34),
    ),
}


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------

def f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def poly(pts: list[tuple[float, float]]) -> str:
    return " ".join(f"{f(x)},{f(y)}" for x, y in pts)


@dataclass
class Scene:
    w: int
    h: int
    pal: Palette
    rng: random.Random
    defs: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    mirrors: list[str] = field(default_factory=list)   # queued water reflections
    n: int = 0

    def uid(self, p: str) -> str:
        self.n += 1
        return f"{p}{self.n}"

    def add(self, s: str) -> None:
        self.body.append(s)

    def define(self, s: str) -> None:
        self.defs.append(s)

    def blur(self, sigma: float, pad: str = "40%") -> str:
        i = self.uid("b")
        neg = "-" + pad
        span = f"{int(pad.rstrip('%')) * 2 + 100}%"
        self.define(
            f'<filter id="{i}" x="{neg}" y="{neg}" width="{span}" height="{span}" '
            f'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{f(sigma)}"/></filter>'
        )
        return i

    def lin(self, stops: list[tuple[float, str]], x2: float = 0.0, y2: float = 1.0) -> str:
        i = self.uid("lg")
        body = "".join(f'<stop offset="{round(o, 3)}" stop-color="{c}"/>' for o, c in stops)
        self.define(f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">{body}</linearGradient>')
        return i

    # ---------------------------------------------------------------- sky
    def sky(self) -> None:
        p = self.pal
        g = self.lin([(i / (len(p.sky) - 1), c) for i, c in enumerate(p.sky)])
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="url(#{g})"/>')

    def sun(self, disc: bool = True) -> None:
        p = self.pal
        cx, cy = self.w * p.sun[0], self.h * p.sun[1]
        i = self.uid("sg")
        self.define(
            f'<radialGradient id="{i}">'
            f'<stop offset="0" stop-color="{rgba(p.glow, p.glow_a)}"/>'
            f'<stop offset="0.28" stop-color="{rgba(p.glow, p.glow_a * 0.5)}"/>'
            f'<stop offset="0.62" stop-color="{rgba(p.glow, p.glow_a * 0.16)}"/>'
            f'<stop offset="1" stop-color="{rgba(p.glow, 0)}"/></radialGradient>'
        )
        r = max(self.w, self.h) * 0.7
        self.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(r)}" ry="{f(r * 0.82)}" fill="url(#{i})"/>')
        if disc:
            bl = self.blur(self.w * 0.006)
            rr = self.w * 0.019
            self.add(
                f'<g filter="url(#{bl})">'
                f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rr * 2.1)}" fill="{rgba(p.glow, 0.28)}"/>'
                f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rr)}" fill="{rgba(p.glow, 0.92)}"/></g>'
            )

    def clouds(self, count: int, band: tuple[float, float]) -> None:
        p, rng = self.pal, self.rng
        bl = self.blur(self.h * 0.028, pad="90%")
        parts = []
        for _ in range(count):
            cx = rng.uniform(-0.12, 1.12) * self.w
            cy = rng.uniform(*band) * self.h
            rx = rng.uniform(0.12, 0.36) * self.w
            ry = rx * rng.uniform(0.035, 0.10)
            tone = mix(p.haze, p.glow, rng.uniform(0.05, 0.85))
            parts.append(
                f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" '
                f'fill="{rgba(tone, rng.uniform(0.05, 0.22))}"/>'
            )
        self.add(f'<g filter="url(#{bl})">{"".join(parts)}</g>')

    def birds(self, count: int) -> None:
        rng, p = self.rng, self.pal
        s0 = self.w / 1600
        parts = []
        for _ in range(count):
            x, y = rng.uniform(0.08, 0.92) * self.w, rng.uniform(0.10, 0.36) * self.h
            s = rng.uniform(0.6, 1.5) * s0
            parts.append(
                f'<path d="M{f(x)} {f(y)}q{f(8 * s)} {f(-6 * s)} {f(15 * s)} {f(-1 * s)}'
                f'q{f(7 * s)} {f(-5 * s)} {f(14 * s)} {f(1 * s)}" fill="none" '
                f'stroke="{rgba(p.ink, rng.uniform(0.25, 0.6))}" stroke-width="{f(1.7 * s)}" '
                f'stroke-linecap="round"/>'
            )
        self.add("".join(parts))

    # -------------------------------------------------------------- karst
    def _tower_shape(self, cx: float, base: float, ht: float,
                     half: float) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
        """Polygon of a limestone tower: sheer bulging walls, jagged crown."""
        rng = self.rng
        n1, n2, n3, n4 = (rng.uniform(0, 12) for _ in range(4))
        steps = 18
        left: list[tuple[float, float]] = []
        right: list[tuple[float, float]] = []
        for i in range(steps + 1):
            t = i / steps
            # near-vertical walls that bulge (and so undercut) around mid-height
            prof = 1 - 0.24 * t ** 2.4 + 0.11 * math.sin(math.pi * t)
            if t < 0.12:                       # tidal undercut at the waterline
                prof *= 0.80 + 1.7 * t
            wl = 1 + 0.06 * math.sin(t * 7.3 + n1) + 0.035 * math.sin(t * 19.1 + n2)
            wr = 1 + 0.06 * math.sin(t * 6.1 + n3) + 0.035 * math.sin(t * 16.7 + n4)
            y = base - ht * t
            left.append((cx - half * prof * wl, y))
            right.append((cx + half * prof * wr, y))
        # crown: a few sharp pinnacles across the summit
        lx, rx = left[-1][0], right[-1][0]
        crown = []
        peaks = rng.randint(3, 6)
        for j in range(peaks + 1):
            u = j / peaks
            dome = math.sin(math.pi * min(max(u, 0.02), 0.98)) ** 0.5
            spike = rng.uniform(0.3, 1.0) if j % 2 else rng.uniform(0.0, 0.3)
            y = base - ht - ht * (0.02 * dome + 0.075 * spike)
            crown.append((lx + (rx - lx) * u, y))
        return left + crown + right[::-1], crown

    def _canopy(self, ridge: list[tuple[float, float]], thickness: float,
                tone: str, rng: random.Random) -> str:
        """A filled, lumpy vegetation mass sitting on a ridge polyline."""
        if len(ridge) < 2:
            return ""
        top: list[tuple[float, float]] = []
        for i, (x, y) in enumerate(ridge):
            lump = thickness * rng.uniform(0.35, 1.45)
            top.append((x + rng.uniform(-thickness, thickness) * 0.5, y - lump))
            if i < len(ridge) - 1:                     # a lump between each pair
                mx = (x + ridge[i + 1][0]) / 2
                my = (y + ridge[i + 1][1]) / 2
                top.append((mx, my - thickness * rng.uniform(0.5, 1.7)))
        d = f"M{f(ridge[0][0])} {f(ridge[0][1])} " + \
            " ".join(f"L{f(x)} {f(y)}" for x, y in top) + \
            " " + " ".join(f"L{f(x)} {f(y + thickness * 0.6)}" for x, y in reversed(ridge)) + " Z"
        blobs = "".join(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(thickness * rng.uniform(0.3, 0.85))}" fill="{tone}"/>'
            for x, y in top
        )
        return f'<g fill="{tone}"><path d="{d}"/>{blobs}</g>'

    def tower(self, cx: float, base: float, ht: float, half: float, depth: float,
              foliage: bool = True, reflect: bool = True) -> None:
        """depth: 1 = far and hazy, 0 = near and dark."""
        p, rng = self.pal, self.rng
        shape, crown = self._tower_shape(cx, base, ht, half)
        pts = poly(shape)

        dark = mix(p.rock, "#000000", 0.34 + 0.48 * (1 - depth))
        lit = mix(mix(p.rock, p.glow, 0.22), p.haze, 0.30 * depth)
        left_sun = p.sun[0] < 0.5
        stops = [(0.0, lit), (0.45, mix(lit, dark, 0.7)), (1.0, dark)]
        if not left_sun:
            stops = [(0.0, dark), (0.55, mix(lit, dark, 0.7)), (1.0, lit)]
        g = self.lin(stops, x2=1.0, y2=0.0)
        self.add(f'<polygon points="{pts}" fill="url(#{g})"/>')

        cid = self.uid("tc")
        self.define(f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>')
        inner: list[str] = []

        # limestone striation / weathering
        for _ in range(int(half / 9) + 6):
            sx = rng.uniform(cx - half, cx + half)
            sh = rng.uniform(0.3, 0.95) * ht
            tint = p.glow if rng.random() < 0.5 else "#000000"
            inner.append(
                f'<rect x="{f(sx)}" y="{f(base - sh)}" width="{f(rng.uniform(1.5, 5.5))}" '
                f'height="{f(sh)}" fill="{rgba(tint, rng.uniform(0.015, 0.05))}"/>'
            )
        # crevices
        for _ in range(rng.randint(2, 4)):
            sx = rng.uniform(cx - half * 0.8, cx + half * 0.8)
            inner.append(
                f'<path d="M{f(sx)} {f(base)} Q{f(sx + rng.uniform(-14, 14))} {f(base - ht * 0.5)} '
                f'{f(sx + rng.uniform(-24, 24))} {f(base - ht * 0.92)}" fill="none" '
                f'stroke="{rgba("#000000", rng.uniform(0.10, 0.22))}" '
                f'stroke-width="{f(rng.uniform(2, 7))}"/>'
            )
        # vegetated crown and shoulders
        if foliage:
            tint = mix(p.foliage, p.haze, 0.40 * depth)
            inner.append(self._canopy(crown, ht * 0.055, tint, rng))
            # a little scrub clinging lower down the walls
            wall_pts = [pt for pt in shape if base - ht * 0.62 < pt[1] < base - ht * 0.12]
            for _ in range(int(half / 7) + 4):
                fx, fy = rng.choice(wall_pts) if wall_pts else (cx, base - ht * 0.4)
                r = rng.uniform(0.05, 0.13) * half
                inner.append(
                    f'<ellipse cx="{f(fx)}" cy="{f(fy)}" rx="{f(r)}" ry="{f(r * 0.75)}" '
                    f'fill="{rgba(tint, 0.75)}"/>'
                )
        # contact shadow at the waterline
        inner.append(
            f'<rect x="{f(cx - half * 1.3)}" y="{f(base - ht * 0.045)}" width="{f(half * 2.6)}" '
            f'height="{f(ht * 0.06)}" fill="{rgba("#000000", 0.42)}"/>'
        )
        self.add(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')

        if reflect:
            s = 0.40
            self.mirrors.append(
                f'<g transform="translate(0,{f(base * (1 + s))}) scale(1,{f(-s)})" '
                f'opacity="{round(0.22 - 0.10 * depth, 3)}">'
                f'<polygon points="{pts}" fill="{mix(dark, p.water[1], 0.35)}"/></g>'
            )
        # foam collar
        bl = self.blur(half * 0.10)
        self.add(
            f'<ellipse cx="{f(cx)}" cy="{f(base + ht * 0.005)}" rx="{f(half * 1.05)}" '
            f'ry="{f(max(2.0, ht * 0.012))}" fill="{rgba(p.foam, 0.30 - 0.12 * depth)}" '
            f'filter="url(#{bl})"/>'
        )

    def ridge(self, base: float, layers: int) -> None:
        """Stacked karst layers: far ones blurred, paler and veiled by haze."""
        rng, p = self.rng, self.pal
        for li in range(layers):
            depth = 1 - li / max(1, layers - 1)
            y = base - self.h * 0.012 * (layers - 1 - li)
            sigma = depth * self.w * 0.0022
            group: list[str] = []
            sub = Scene(self.w, self.h, p, rng, self.defs, group, self.mirrors, self.n)
            count = rng.randint(2, 4) if depth < 0.6 else rng.randint(3, 5)
            for k in range(count):
                cx = (k + rng.uniform(0.05, 0.95)) / count * self.w
                scale = 0.7 + 0.55 * (1 - depth)
                if rng.random() < 0.4:                    # slender spire
                    half = rng.uniform(0.028, 0.055) * self.w * scale
                    ht = rng.uniform(0.30, 0.52) * self.h * (0.6 + 0.7 * (1 - depth))
                else:                                     # broad mesa
                    half = rng.uniform(0.07, 0.14) * self.w * scale
                    ht = rng.uniform(0.18, 0.34) * self.h * (0.6 + 0.7 * (1 - depth))
                sub.tower(cx, y, ht, half, depth, reflect=depth < 0.5)
            self.n = sub.n
            wrap = f'filter="url(#{self.blur(sigma)})"' if sigma > 0.35 else ""
            self.add(f"<g {wrap}>{''.join(group)}</g>")
            # aerial perspective: haze thickest at the waterline
            if depth > 0.02:
                peak = 0.035 + 0.12 * depth
                g = self.lin([
                    (0.0, rgba(p.haze, 0.0)),
                    (0.62, rgba(p.haze, peak * 0.45)),
                    (0.93, rgba(p.haze, peak)),
                    (1.0, rgba(p.haze, peak * 0.55)),
                ])
                top = max(0.0, y - self.h * 0.5)
                self.add(f'<rect x="0" y="{f(top)}" width="{self.w}" height="{f(y - top)}" fill="url(#{g})"/>')

    # -------------------------------------------------------------- water
    def sea(self, horizon: float) -> None:
        p, rng = self.pal, self.rng
        depth = self.h - horizon
        near_h = mix(p.water[0], p.haze, 0.32)
        g = self.lin([
            (0.0, near_h),
            (0.10, p.water[0]),
            (0.38, mix(p.water[0], p.water[1], 0.34)),
            (0.72, mix(p.water[0], p.water[1], 0.78)),
            (1.0, p.water[1]),
        ])
        self.add(f'<rect x="0" y="{f(horizon)}" width="{self.w}" height="{f(depth)}" fill="url(#{g})"/>')

        # queued island reflections, then wave lines that break them up
        if self.mirrors:
            bl = self.blur(depth * 0.012)
            clip = self.uid("wc")
            self.define(
                f'<clipPath id="{clip}"><rect x="0" y="{f(horizon)}" width="{self.w}" '
                f'height="{f(depth)}"/></clipPath>'
            )
            self.add(
                f'<g clip-path="url(#{clip})" filter="url(#{bl})">{"".join(self.mirrors)}</g>'
            )
            self.mirrors = []

        # soft horizon: a blurred band hides the hard rect edge
        bl = self.blur(depth * 0.02)
        self.add(
            f'<rect x="{f(-self.w * 0.1)}" y="{f(horizon - depth * 0.03)}" width="{f(self.w * 1.2)}" '
            f'height="{f(depth * 0.06)}" fill="{rgba(near_h, 0.75)}" filter="url(#{bl})"/>'
        )

        # shallow reef patches
        bl = self.blur(depth * 0.045)
        reef = []
        for _ in range(rng.randint(4, 7)):
            cx = rng.uniform(-0.05, 1.05) * self.w
            t = rng.uniform(0.04, 0.6)
            cy = horizon + t * depth
            rx = rng.uniform(0.10, 0.32) * self.w
            reef.append(
                f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(rx * (0.10 + t * 0.14))}" '
                f'fill="{rgba(p.shallow, rng.uniform(0.10, 0.30))}"/>'
            )
        self.add(f'<g filter="url(#{bl})">{"".join(reef)}</g>')

        # specular path under the sun
        cx = self.w * p.sun[0]
        gp = self.lin([
            (0.0, rgba(p.glow, 0)), (0.35, rgba(p.glow, p.glow_a * 0.55)),
            (0.5, rgba(p.glow, p.glow_a * 0.95)), (0.65, rgba(p.glow, p.glow_a * 0.55)),
            (1.0, rgba(p.glow, 0)),
        ], x2=1.0, y2=0.0)
        bl = self.blur(depth * 0.006)
        spec = []
        rows = max(10, int(depth / 10))
        for i in range(rows):
            t = i / (rows - 1)
            if rng.random() < 0.42:
                continue
            y = horizon + (t ** 1.25) * depth
            half = (0.03 + t * 0.34) * self.w
            spec.append(
                f'<rect x="{f(cx - half)}" y="{f(y)}" width="{f(half * 2)}" '
                f'height="{f(1 + t * 5.5)}" rx="{f(0.5 + t * 2)}" fill="url(#{gp})" '
                f'opacity="{round(rng.uniform(0.3, 1.0), 2)}"/>'
            )
        self.add(f'<g filter="url(#{bl})">{"".join(spec)}</g>')

        # wave crests, larger and sparser as they come forward
        crests = []
        for _ in range(int(depth / 9)):
            t = rng.random() ** 1.5
            y = horizon + t * depth
            x = rng.uniform(-0.06, 1.02) * self.w
            wl = rng.uniform(0.015, 0.13) * self.w * (0.35 + t * 1.6)
            crests.append(
                f'<rect x="{f(x)}" y="{f(y)}" width="{f(wl)}" height="{f(0.8 + t * 3.4)}" '
                f'rx="{f(0.6 + t * 1.6)}" fill="{rgba(p.foam, rng.uniform(0.05, 0.26))}"/>'
            )
        self.add("".join(crests))

    def beach(self, y: float) -> None:
        p = self.pal
        sand = mix(p.foam, p.haze, 0.30)
        g = self.lin([
            (0.0, rgba(p.foam, 0.9)),
            (0.16, rgba(sand, 0.95)),
            (1.0, rgba(mix(sand, "#000000", 0.62), 0.97)),
        ])
        self.add(
            f'<path d="M0 {self.h} L0 {f(y + self.h * 0.05)} '
            f'C {f(self.w * 0.28)} {f(y - self.h * 0.035)} {f(self.w * 0.66)} {f(y + self.h * 0.045)} '
            f'{self.w} {f(y - self.h * 0.015)} L{self.w} {self.h} Z" fill="url(#{g})"/>'
        )
        bl = self.blur(self.h * 0.006)
        self.add(
            f'<path d="M0 {f(y + self.h * 0.05)} '
            f'C {f(self.w * 0.28)} {f(y - self.h * 0.035)} {f(self.w * 0.66)} {f(y + self.h * 0.045)} '
            f'{self.w} {f(y - self.h * 0.015)}" fill="none" stroke="{rgba(p.foam, 0.8)}" '
            f'stroke-width="{f(self.h * 0.006)}" filter="url(#{bl})"/>'
        )

    # -------------------------------------------------------------- props
    def longtail(self, cx: float, cy: float, s: float, flip: bool = False) -> None:
        p = self.pal
        hull = (
            f"M{f(-40 * s)} 0 C{f(-30 * s)} {f(5.5 * s)} {f(28 * s)} {f(6 * s)} {f(42 * s)} {f(-1 * s)} "
            f"C{f(30 * s)} {f(-3.2 * s)} {f(-26 * s)} {f(-3.6 * s)} {f(-40 * s)} 0 Z"
        )
        bits = (
            f'<rect x="{f(-15 * s)}" y="{f(-8 * s)}" width="{f(25 * s)}" height="{f(7.5 * s)}" '
            f'rx="{f(1.5 * s)}" fill="{p.ink}"/>'
            f'<path d="M{f(-40 * s)} {f(-0.5 * s)} L{f(-50 * s)} {f(-16 * s)}" stroke="{p.ink}" '
            f'stroke-width="{f(2 * s)}" stroke-linecap="round"/>'
            f'<path d="M{f(32 * s)} {f(-1.5 * s)} L{f(56 * s)} {f(-15 * s)}" stroke="{p.ink}" '
            f'stroke-width="{f(1.8 * s)}" stroke-linecap="round"/>'
            f'<path d="M{f(-48 * s)} {f(-14 * s)} q{f(6 * s)} {f(3 * s)} {f(2 * s)} {f(9 * s)}" '
            f'fill="none" stroke="{p.ink}" stroke-width="{f(1.4 * s)}"/>'
        )
        bl = self.blur(4 * s)
        shade = (
            f'<ellipse cx="0" cy="{f(8 * s)}" rx="{f(38 * s)}" ry="{f(3.4 * s)}" '
            f'fill="{rgba("#000000", 0.32)}" filter="url(#{bl})"/>'
            f'<ellipse cx="0" cy="{f(15 * s)}" rx="{f(26 * s)}" ry="{f(6 * s)}" '
            f'fill="{rgba(p.ink, 0.16)}" filter="url(#{bl})"/>'
        )
        tf = f"translate({f(cx)},{f(cy)})" + (" scale(-1,1)" if flip else "")
        self.add(f'<g transform="{tf}">{shade}<path d="{hull}" fill="{p.ink}"/>{bits}</g>')

    def frond(self, x: float, y: float, ang: float, length: float, tone: str, alpha: float) -> None:
        """One palm leaf: an arched midrib carrying two serrated blades."""
        rng = self.rng
        a = math.radians(ang)
        droop = math.radians(ang + rng.uniform(30, 62))
        ex, ey = x + math.cos(droop) * length, y + math.sin(droop) * length
        cx, cy = x + math.cos(a) * length * 0.58, y + math.sin(a) * length * 0.58

        n = 26
        spine: list[tuple[float, float, float, float]] = []   # x, y, nx, ny
        for i in range(n + 1):
            t = i / n
            px = (1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t ** 2 * ex
            py = (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t ** 2 * ey
            tx = 2 * (1 - t) * (cx - x) + 2 * t * (ex - cx)
            ty = 2 * (1 - t) * (cy - y) + 2 * t * (ey - cy)
            m = math.hypot(tx, ty) or 1.0
            spine.append((px, py, -ty / m, tx / m))

        parts = []
        for sgn in (1, -1):
            d = [f"M{f(spine[0][0])} {f(spine[0][1])}"]
            for i in range(1, n + 1):
                px, py, nx, ny = spine[i]
                width = length * 0.15 * math.sin(math.pi * (i / n)) ** 0.5 * rng.uniform(0.82, 1.1)
                # leaflet tip, swept back toward the leaf base
                back = (spine[i - 1][0] - px, spine[i - 1][1] - py)
                d.append(
                    f"L{f(px + nx * sgn * width + back[0] * 1.15)} "
                    f"{f(py + ny * sgn * width + back[1] * 1.15)}"
                )
                d.append(f"L{f(px)} {f(py)}")
            parts.append(f'<path d="{" ".join(d)}Z" fill="{tone}" opacity="{round(alpha, 2)}"/>')
        parts.append(
            f'<path d="M{f(x)} {f(y)} Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}" fill="none" stroke="{tone}" '
            f'stroke-width="{f(length * 0.02)}" stroke-linecap="round" opacity="{round(alpha, 2)}"/>'
        )
        self.add("".join(parts))

    def palm_fringe(self, corner: str = "tl", scale: float = 1.0) -> None:
        """Out-of-focus palm leaves reaching in from a top corner."""
        rng, p = self.rng, self.pal
        bl = self.blur(self.w * 0.005, pad="60%")
        left = corner.endswith("l")
        d = 1 if left else -1
        ax = (-0.10 if left else 1.10) * self.w
        tone = mix(p.foliage, "#000000", 0.42)
        start = len(self.body)
        for _ in range(rng.randint(3, 5)):
            self.frond(
                ax + d * rng.uniform(0.0, 0.05) * self.w,
                rng.uniform(-0.06, 0.10) * self.h,
                (rng.uniform(-8, 55) if left else 180 - rng.uniform(-8, 55)),
                rng.uniform(0.22, 0.34) * self.w * scale,
                tone, rng.uniform(0.8, 1.0),
            )
        inner = "".join(self.body[start:])
        del self.body[start:]
        self.add(f'<g filter="url(#{bl})">{inner}</g>')

    def palm_tree(self, x: float, base_y: float, height: float, lean: float = -1.0) -> None:
        p, rng = self.pal, self.rng
        tip_x = x + lean * height * 0.28
        tip_y = base_y - height
        trunk = (
            f'<path d="M{f(x - height * 0.022)} {f(base_y)} '
            f'Q{f(x + lean * height * 0.06)} {f(base_y - height * 0.55)} {f(tip_x)} {f(tip_y)} '
            f'L{f(tip_x + height * 0.018)} {f(tip_y)} '
            f'Q{f(x + lean * height * 0.09 + height * 0.03)} {f(base_y - height * 0.55)} '
            f'{f(x + height * 0.026)} {f(base_y)} Z" fill="{p.ink}"/>'
        )
        self.add(trunk)
        for i in range(7):
            self.frond(tip_x, tip_y, -170 + i * 47 + rng.uniform(-10, 10),
                       height * rng.uniform(0.30, 0.44), p.ink, 1.0)

    def cliff_frame(self, strength: float = 1.0) -> None:
        """Near-black rock walls closing in from both edges, framing the shot."""
        rng, p = self.rng, self.pal
        w, h = self.w, self.h
        for side in ("l", "r"):
            cw = rng.uniform(0.13, 0.20) * w * strength
            sx = 0.0 if side == "l" else float(w)
            d = 1.0 if side == "l" else -1.0
            ph1, ph2, ph3 = (rng.uniform(0, 6.2) for _ in range(3))
            steps = 30
            edge = []
            for i in range(steps + 1):
                t = i / steps
                # broad sweep plus two octaves of rocky irregularity
                span = (
                    0.78
                    + 0.34 * math.sin(t * 2.1 + ph1)
                    + 0.14 * math.sin(t * 5.7 + ph2)
                    + 0.06 * math.sin(t * 13.3 + ph3)
                )
                edge.append((sx + d * cw * span, t * h))
            path = f"M{f(sx)} 0 " + " ".join(f"L{f(x)} {f(y)}" for x, y in edge) + f" L{f(sx)} {h} Z"

            rock = mix(p.rock, "#000000", 0.76)
            g = self.lin(
                [(0.0, mix(rock, p.glow, 0.12)), (0.6, rock), (1.0, mix(rock, "#000000", 0.55))],
                x2=(1.0 if side == "l" else -1.0), y2=0.25,
            )
            self.add(f'<path d="{path}" fill="url(#{g})"/>')

            cid = self.uid("cf")
            self.define(f'<clipPath id="{cid}"><path d="{path}"/></clipPath>')
            detail = []
            leaf = mix(p.foliage, "#000000", 0.5)
            inset = [(x - d * cw * 0.10, y) for x, y in edge]
            detail.append(self._canopy(inset, cw * 0.16, leaf, rng))
            for _ in range(20):                      # weathering streaks
                detail.append(
                    f'<rect x="{f(rng.uniform(min(sx, sx + d * cw * 1.2), max(sx, sx + d * cw * 1.2)))}" '
                    f'y="0" width="{f(rng.uniform(2, 9))}" height="{h}" '
                    f'fill="{rgba(p.glow, rng.uniform(0.012, 0.04))}"/>'
                )
            self.add(f'<g clip-path="url(#{cid})">{"".join(detail)}</g>')

            # a couple of fronds hanging into the frame from the top corner
            for _ in range(2):
                self.frond(
                    sx + d * cw * rng.uniform(0.5, 0.9), rng.uniform(-0.02, 0.08) * h,
                    (rng.uniform(5, 50) if side == "l" else 180 - rng.uniform(5, 50)),
                    rng.uniform(0.10, 0.16) * w, mix(p.foliage, "#000000", 0.55), 0.95,
                )

    # ------------------------------------------------------------- grade
    def grade(self, vignette: float = 0.55, wash: float = 0.16, fade: float = 0.0) -> None:
        p = self.pal
        # duotone wash: cool shadows, warm highlights
        g = self.lin([
            (0.0, rgba(mix(p.grade, "#000010", 0.4), wash * 1.1)),
            (0.5, rgba(p.grade, wash * 0.35)),
            (1.0, rgba(mix(p.grade, "#000008", 0.55), wash)),
        ])
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="url(#{g})" '
                 f'style="mix-blend-mode:soft-light"/>')
        if fade > 0:
            gf = self.lin([
                (0.0, rgba("#04080a", 0)), (0.6, rgba("#04080a", fade * 0.45)),
                (1.0, rgba("#04080a", fade)),
            ])
            self.add(f'<rect y="{f(self.h * 0.45)}" width="{self.w}" height="{f(self.h * 0.55)}" '
                     f'fill="url(#{gf})"/>')
        i = self.uid("vg")
        self.define(
            f'<radialGradient id="{i}" cx="0.5" cy="0.46" r="0.78">'
            f'<stop offset="0.35" stop-color="rgba(0,0,0,0)"/>'
            f'<stop offset="0.72" stop-color="{rgba("#000208", vignette * 0.33)}"/>'
            f'<stop offset="1" stop-color="{rgba("#000208", vignette)}"/></radialGradient>'
        )
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="url(#{i})"/>')

    def grain(self, amount: float = 0.5) -> None:
        """Film grain as translucent speckle (works with or without blend modes)."""
        for sign, tone, freq in ((1, "1", 0.85), (-1, "0", 0.7)):
            i = self.uid("gr")
            k = 0.34 * sign
            off = 0.34 if sign > 0 else 0.30
            self.define(
                f'<filter id="{i}" x="0" y="0" width="100%" height="100%" '
                f'color-interpolation-filters="sRGB">'
                f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" '
                f'seed="{self.n}" stitchTiles="stitch" result="n"/>'
                f'<feColorMatrix in="n" type="matrix" values="'
                f'0 0 0 0 {tone} 0 0 0 0 {tone} 0 0 0 0 {tone} '
                f'{k} {k} {k} 0 {-off if sign > 0 else off}"/>'
                f"</filter>"
            )
            self.add(
                f'<rect width="{self.w}" height="{self.h}" filter="url(#{i})" '
                f'opacity="{round(amount * (0.5 if sign > 0 else 0.42), 3)}"/>'
            )

    # ------------------------------------------------------------ output
    def render(self, title: str) -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'preserveAspectRatio="xMidYMid slice" role="img" aria-label="{title}">'
            f"<title>{title}</title><defs>{''.join(self.defs)}</defs>{''.join(self.body)}</svg>"
        )


# --------------------------------------------------------------------------
# compositions
# --------------------------------------------------------------------------

def compose(kind: str, w: int, h: int, pal: Palette, seed: int, title: str) -> str:
    rng = random.Random(seed)
    sc = Scene(w, h, pal, rng)

    if kind == "hero":
        horizon = h * 0.58
        sc.sky()
        sc.sun(disc=False)
        sc.clouds(9, (0.04, 0.46))
        sc.birds(6)
        sc.ridge(horizon, layers=4)
        sc.sea(horizon)
        sc.longtail(w * 0.33, horizon + (h - horizon) * 0.26, w / 1800 * 0.85)
        sc.longtail(w * 0.60, horizon + (h - horizon) * 0.14, w / 1800 * 0.55, flip=True)
        sc.longtail(w * 0.46, horizon + (h - horizon) * 0.56, w / 1800 * 1.4)
        sc.cliff_frame(1.0)
        sc.grade(vignette=0.62, wash=0.12, fade=0.72)
        sc.grain(0.55)

    elif kind == "card":
        # every card shuffles its own framing so a grid of them never repeats
        horizon = h * rng.uniform(0.50, 0.66)
        shore = rng.random() < 0.68
        sc.sky()
        sc.sun(disc=rng.random() < 0.5)
        sc.clouds(rng.randint(4, 7), (0.05, 0.5))
        sc.birds(rng.randint(2, 5))
        sc.ridge(horizon, layers=3)
        sc.sea(horizon)
        for k in range(rng.randint(1, 2)):
            sc.longtail(
                w * rng.uniform(0.18, 0.72),
                horizon + (h - horizon) * rng.uniform(0.16, 0.44),
                w / 1000 * rng.uniform(0.55, 0.95),
                flip=rng.random() < 0.5,
            )
        if shore:
            sc.beach(h * rng.uniform(0.84, 0.93))
        if rng.random() < 0.42:
            right = rng.random() < 0.7
            sc.palm_tree(
                w * (1.01 if right else -0.01), h * rng.uniform(1.0, 1.08),
                h * rng.uniform(0.34, 0.50), lean=(-1.15 if right else 1.15),
            )
        if rng.random() < 0.45:
            sc.palm_fringe("tl" if rng.random() < 0.5 else "tr", rng.uniform(0.7, 1.05))
        sc.grade(vignette=rng.uniform(0.45, 0.6), wash=0.11, fade=rng.uniform(0.2, 0.38))
        sc.grain(0.5)

    else:  # banner
        horizon = h * 0.56
        sc.sky()
        sc.sun()
        sc.clouds(8, (0.05, 0.48))
        sc.birds(5)
        sc.ridge(horizon, layers=3)
        sc.sea(horizon)
        sc.longtail(w * 0.26, horizon + (h - horizon) * 0.44, w / 1800 * 1.1)
        sc.longtail(w * 0.72, horizon + (h - horizon) * 0.20, w / 1800 * 0.6, flip=True)
        sc.palm_fringe("tr", 0.55)
        sc.grade(vignette=0.5, wash=0.11, fade=0.22)
        sc.grain(0.5)

    return sc.render(title)


MANIFEST: list[tuple[str, str, str, int, str]] = [
    ("hero-phiphi",     "hero",   "lagoon", 1017, "Long-tail boats anchored in the turquoise bay of Phi Phi Leh"),
    ("hero-krabi",      "hero",   "ember",  2311, "Sunset over the limestone headlands of Krabi"),
    ("hero-lipe",       "hero",   "dawn",   3907, "First light across the Koh Lipe archipelago"),
    ("card-mayabay",    "card",   "lagoon", 4101, "Maya Bay framed by sheer limestone cliffs"),
    ("card-pileh",      "card",   "jade",   4212, "The still emerald water of Pileh Lagoon"),
    ("card-bamboo",     "card",   "lagoon", 4323, "White sand and shallow reef at Bamboo Island"),
    ("card-hongisle",   "card",   "jade",   4434, "A hidden lagoon inside the Hong Islands"),
    ("card-jamesbond",  "card",   "abyss",  4545, "Limestone towers rising from Phang Nga Bay"),
    ("card-similan",    "card",   "abyss",  4656, "A dive boat above the Similan reef wall"),
    ("card-sunsetsail", "card",   "gold",   4767, "A catamaran cruising into a golden-hour sky"),
    ("card-kayak",      "card",   "jade",   4878, "Sea kayaks threading a mangrove channel"),
    ("card-lantasunset","card",   "ember",  4989, "The sunset viewpoint on the west coast of Koh Lanta"),
    ("card-kohtao",     "card",   "abyss",  5010, "Granite boulders and clear water at Koh Tao"),
    ("card-lipe",       "card",   "dawn",   5121, "Pastel dawn over the Koh Lipe sandbar"),
    ("banner-story",    "banner", "gold",   6001, "A long-tail boat crossing an open golden bay"),
    ("banner-journal",  "banner", "jade",   6002, "Morning mist between the karsts"),
    ("banner-cta",      "banner", "ember",  6003, "A wide sunset panorama of the Andaman Sea"),
]

SIZES = {"hero": (2200, 1400), "card": (900, 1200), "banner": (2000, 900)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="print the manifest and exit")
    ap.add_argument("--only", action="append", default=None, help="render just these scene names")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    if args.list:
        for name, kind, pal, seed, title in MANIFEST:
            print(f"{name:18} {kind:7} {pal:7} seed={seed:<6} {title}")
        return 0

    os.makedirs(args.out, exist_ok=True)
    total = 0
    for name, kind, pal_name, seed, title in MANIFEST:
        if args.only and name not in args.only:
            continue
        w, h = SIZES[kind]
        svg = compose(kind, w, h, PALETTES[pal_name], seed, title)
        with open(os.path.join(args.out, f"{name}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        total += len(svg)
        print(f"{name}.svg  {len(svg) / 1024:6.1f} KB")
    print(f"total {total / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
