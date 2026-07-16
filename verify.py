#!/usr/bin/env python3
"""Verify the generated Spa Creek Marina preview's critical static guarantees."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
PAGES = [
    "index.html",
    "additional-slips.html",
    "pelicans-roost-rental.html",
    "knot10-yacht-sales.html",
    "contact.html",
    "privacy-policy.html",
]
ORIGINAL_SITE_URL = "https://www.spacreekmarina.net/"
EXPECTED_WORDING = "This is a free concept redesign — Spa Creek Marina, LLC's actual site is at"

assert sorted(p.name for p in PUBLIC.glob("*.html")) == sorted(PAGES)
for name in PAGES:
    page = PUBLIC / name
    text = page.read_text(encoding="utf-8")
    banners = re.findall(r'<div class="concept-banner">(.*?)</div>', text, re.I | re.S)
    assert len(banners) == 1, (name, "concept banner count", len(banners))
    plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", banners[0])).strip()
    assert EXPECTED_WORDING in plain, (name, plain)
    assert re.findall(r'href="([^"]+)"', banners[0], re.I) == [ORIGINAL_SITE_URL], name
    assert re.search(r'<body[^>]*>\s*<div class="concept-banner">', text, re.I), name
    assert len(re.findall(r"<h1[\s>]", text, re.I)) == 1, name
    for ref in re.findall(r'(?:href|src)="([^"]+)"', text, re.I):
        if ref.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        target = PUBLIC / ref.split("#", 1)[0]
        assert target.exists(), (name, ref)

css = (PUBLIC / "css/shared.css").read_text(encoding="utf-8")
assert ".concept-banner {" in css
assert (PUBLIC / "_redirects").read_text(encoding="utf-8") == "/scan / 302\n"
assert "/scan" not in (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
print("PASS: 6 pages with mandatory top-of-body concept banners, exact original-site link, shared CSS, static links, headings, and /scan rule")
