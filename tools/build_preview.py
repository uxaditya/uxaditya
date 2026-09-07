#!/usr/bin/env python3
"""
Bundle the four-page site into one self-contained HTML file.

Useful where only a single file can be hosted or shared — a Claude artifact,
a pasted snippet, an email attachment. Everything is inlined: stylesheets,
scripts, the webfonts as base64 and every scene as a data URI. Page
navigation becomes client-side routing over `?page=`, so the internal links,
the `?slug=` detail pages and the `?tag=` filters all keep working.

    python3 tools/build_preview.py [-o dist/andamana.html]

The multi-page site under version control stays the source of truth; this is a
derived artifact and is not committed.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = {"home": "index.html", "tours": "tours.html", "tour": "tour.html", "about": "about.html"}
FOOTER_MARK = "<!-- ============================================================ footer -->"
TITLE = "Andamana Island Tours"


def read(*parts: str) -> str:
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def slice_between(text: str, start: str, end: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[a:b]


def svg_data_uri(svg: str) -> str:
    """Percent-encode only what would break an attribute or a CSS url()."""
    for a, b in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), ('"', "%22")):
        svg = svg.replace(a, b)
    return "data:image/svg+xml;charset=utf-8," + svg.replace("\n", "")


def inline_fonts(css: str) -> str:
    """Swap each url("../fonts/x.woff2") for a base64 data URI."""
    def sub(m: re.Match[str]) -> str:
        raw = open(os.path.join(ROOT, "assets", "fonts", m.group(1)), "rb").read()
        return 'url("data:font/woff2;base64,%s")' % base64.b64encode(raw).decode()
    return re.sub(r'url\("\.\./fonts/([^"]+)"\)', sub, css)


def js_string(value: object) -> str:
    """JSON for embedding in a <script>: never emit a literal </script>."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


RUNTIME = r"""
(function () {
  "use strict";
  var IMG = window.ANDAMANA_IMG || {};
  var VIEWS = window.ANDAMANA_VIEWS || {};
  var REF = /assets\/img\/([\w.-]+\.svg)/g;

  var one = function (url) {
    var m = /assets\/img\/([\w.-]+\.svg)/.exec(url || "");
    return m && IMG[m[1]] ? IMG[m[1]] : url;
  };

  // Point every local image reference at its inlined copy.
  var resolve = function (root) {
    Array.prototype.forEach.call(root.querySelectorAll("img[src]"), function (el) {
      var s = el.getAttribute("src");
      if (s && s.indexOf("assets/img/") === 0) el.setAttribute("src", one(s));
    });
    Array.prototype.forEach.call(root.querySelectorAll('[style*="assets/img/"]'), function (el) {
      el.setAttribute("style", el.getAttribute("style").replace(REF, function (whole, name) {
        return IMG[name] || whole;
      }));
    });
  };

  (window.ANDAMANA_TOURS || []).forEach(function (t) {
    t.img = one(t.img);
    t.gallery = (t.gallery || []).map(one);
  });

  var host = document.getElementById("view");
  var current = function () {
    var p = new URLSearchParams(location.search).get("page");
    return VIEWS[p] ? p : "home";
  };

  var mark = function (page) {
    var file = page === "home" ? "index.html" : page + ".html";
    Array.prototype.forEach.call(document.querySelectorAll(".nav__link[href]"), function (a) {
      a.classList.toggle("is-active", a.getAttribute("href") === file);
    });
  };

  var render = function (page, hash) {
    host.innerHTML = VIEWS[page] || VIEWS.home;
    resolve(host);
    mark(page);
    if (window.ANDAMANA && window.ANDAMANA.remount) window.ANDAMANA.remount();
    var target = hash && document.getElementById(hash);
    if (target) target.scrollIntoView();
    else window.scrollTo({ top: 0, behavior: "instant" });
  };

  // Internal links become history entries over ?page=, which keeps
  // location.search readable by the catalogue and detail-page code.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a || a.target === "_blank") return;
    var m = /^(index|tours|tour|about)\.html(?:\?([^#]*))?(?:#(.*))?$/.exec(a.getAttribute("href") || "");
    if (!m) return;
    e.preventDefault();
    var page = m[1] === "index" ? "home" : m[1];
    history.pushState({}, "", "?page=" + page + (m[2] ? "&" + m[2] : "") + (m[3] ? "#" + m[3] : ""));
    render(page, m[3]);
  });
  window.addEventListener("popstate", function () { render(current(), null); });

  resolve(document);
  mark(current());
  if (current() !== "home") render(current(), (location.hash || "").slice(1));
})();
"""

NOTE = """
<!-- Single-file build of a four-page static site (tools/build_preview.py).
     Styles, scripts, fonts and artwork are inlined; page navigation runs
     client-side over ?page=. Source: the multi-page site in the repository. -->
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", default=os.path.join(ROOT, "dist", "andamana.html"))
    args = ap.parse_args()

    index = read("index.html")
    chrome = slice_between(index, '<a class="skip"', '<main id="main">')
    footer = slice_between(index, FOOTER_MARK, '<script type="application/ld+json">')

    views = {}
    for key, filename in PAGES.items():
        page = read(filename)
        views[key] = slice_between(page, '<main id="main"', FOOTER_MARK).strip()

    images = {}
    img_dir = os.path.join(ROOT, "assets", "img")
    for name in sorted(os.listdir(img_dir)):
        if name.endswith(".svg"):
            images[name] = svg_data_uri(read("assets", "img", name))

    css = inline_fonts(read("assets", "css", "fonts.css")) + "\n" + read("assets", "css", "style.css")

    parts = [
        f"<title>{TITLE}</title>",
        NOTE.strip(),
        f"<style>\n{css}\n</style>",
        chrome,
        '<div id="view">',
        views["home"],
        "</div>",
        footer,
        f"<script>window.ANDAMANA_IMG={js_string(images)};</script>",
        f"<script>window.ANDAMANA_VIEWS={js_string(views)};</script>",
        f"<script>\n{read('assets', 'js', 'tours.js')}\n</script>",
        f"<script>{RUNTIME}</script>",
        f"<script>\n{read('assets', 'js', 'main.js')}\n</script>",
    ]
    html = "\n".join(parts)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"{os.path.relpath(args.out, ROOT)}  {len(html.encode()) / 1024 / 1024:.2f} MB")
    print(f"  {len(views)} views, {len(images)} scenes inlined, {len(css) / 1024:.0f} KB css")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
