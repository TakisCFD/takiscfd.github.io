#!/usr/bin/env python3
"""Check generated HTML, local links, images and page anchors without network access."""
from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicate_ids: list[str] = []
        self.references: list[str] = []
        self.baseurl: str = ""
        self.images_without_alt = 0
        self.title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        identifier = attributes.get("id")
        if identifier:
            if identifier in self.ids:
                self.duplicate_ids.append(identifier)
            self.ids.add(identifier)
        if tag == "meta" and attributes.get("name") == "site-baseurl":
            self.baseurl = attributes.get("content", "")
        if tag == "title":
            self.title = True
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt += 1
        for field in ("href", "src", "poster"):
            if attributes.get(field):
                self.references.append(attributes[field])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, nargs="?", default=Path("_site"))
    args = parser.parse_args()
    root = args.site.resolve()
    errors: list[str] = []
    if not (root / "index.html").is_file():
        print(f"Missing homepage: {root / 'index.html'}", file=sys.stderr)
        return 1
    pages: dict[Path, Page] = {}
    for path in root.rglob("*.html"):
        page = Page()
        text = path.read_text(encoding="utf-8")
        page.feed(text)
        pages[path] = page
        label = str(path.relative_to(root))
        if not page.title:
            errors.append(f"{label}: missing page title.")
        if page.images_without_alt:
            errors.append(f"{label}: {page.images_without_alt} image(s) missing alt text.")
        if page.duplicate_ids:
            errors.append(f"{label}: duplicate IDs: {page.duplicate_ids}")
        if "{%" in text or "{{ site." in text or "{{ page." in text:
            errors.append(f"{label}: unrendered template markup.")
    for path, page in pages.items():
        label = str(path.relative_to(root))
        for reference in page.references:
            parts = urlsplit(reference)
            if parts.scheme or parts.netloc:
                if parts.scheme.lower() in {"javascript", "vbscript"}:
                    errors.append(f"{label}: unsafe link scheme.")
                continue
            decoded = unquote(parts.path)
            if not decoded:
                target = path
            elif decoded.startswith("/"):
                if page.baseurl:
                    if decoded == page.baseurl or decoded.startswith(page.baseurl + "/"):
                        decoded = decoded[len(page.baseurl):] or "/"
                    else:
                        errors.append(f"{label}: URL misses baseurl {page.baseurl}: {reference}")
                        continue
                target = root / decoded.lstrip("/")
            else:
                target = path.parent / decoded
            target = target.resolve()
            if not target.is_relative_to(root):
                errors.append(f"{label}: link escapes the site: {reference}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"{label}: missing local target: {reference}")
                continue
            if parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                errors.append(f"{label}: missing anchor: {reference}")
    for private in ["Gemfile", "Gemfile.lock", "requirements.txt", "README.md", "CONTENT_NEEDED.md", "SOURCE_NOTES.md", "EDITING.md", "scripts", "tests", "examples", ".github", ".openai", "_config.deploy.yml"]:
        if (root / private).exists():
            errors.append(f"Internal project material would be published: {private}")
    if errors:
        print("Generated-site checks failed:", file=sys.stderr)
        for error in errors[:80]:
            print("  - " + error, file=sys.stderr)
        return 1
    print(f"Checked {len(pages)} HTML pages: local links, assets, anchors and publication contents are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
