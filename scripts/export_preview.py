#!/usr/bin/env python3
"""Copy a Jekyll build into an offline preview with relative file links."""
from __future__ import annotations

import argparse
import html
import os
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit


class OfflineHTML(HTMLParser):
    def __init__(self, source: Path, root: Path):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.root = root
        self.baseurl = ""
        self.output: list[str] = []

    def local_link(self, value: str) -> str:
        parts = urlsplit(value)
        if not value or parts.scheme or parts.netloc or not parts.path:
            return value
        path = unquote(parts.path)
        if path.startswith("/"):
            if self.baseurl and (path == self.baseurl or path.startswith(self.baseurl + "/")):
                path = path[len(self.baseurl):] or "/"
            target = (self.root / path.lstrip("/")).resolve()
        else:
            target = (self.source.parent / path).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError(f"Local reference leaves the site: {value}")
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            raise ValueError(f"Missing local reference in {self.source}: {value}")
        relative = Path(os.path.relpath(target, self.source.parent)).as_posix()
        return urlunsplit(("", "", quote(relative, safe="/-._~"), parts.query, parts.fragment))

    def start_tag(self, tag: str, attrs, closing: str) -> None:
        values = dict(attrs)
        if tag == "meta" and values.get("name") == "site-baseurl":
            self.baseurl = values.get("content", "").rstrip("/")
        attributes = []
        for name, value in attrs:
            if value is None:
                attributes.append(name)
                continue
            if name in {"href", "src", "poster"}:
                value = self.local_link(value)
            if tag == "meta" and values.get("name") == "site-baseurl" and name == "content":
                value = ""
            attributes.append(f'{name}="{html.escape(value, quote=True)}"')
        self.output.append("<" + tag + (" " + " ".join(attributes) if attributes else "") + closing)

    def handle_starttag(self, tag, attrs):
        self.start_tag(tag, attrs, ">")

    def handle_startendtag(self, tag, attrs):
        self.start_tag(tag, attrs, " />")

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("_site"))
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    root, destination = args.source.resolve(), args.destination.resolve()
    if not (root / "index.html").is_file():
        parser.error("Build the site first; the source must contain index.html.")
    if destination == root or destination.is_relative_to(root) or root.is_relative_to(destination):
        parser.error("Choose a destination outside the generated site tree.")
    if destination.exists():
        parser.error("Choose a new destination so an existing preview is not overwritten.")
    pages: dict[Path, str] = {}
    for source in sorted(root.rglob("*.html")):
        markup = source.read_text(encoding="utf-8")
        if "gc.zgo.at/count.js" in markup:
            parser.error("Export a development build with no analytics loader.")
        document = OfflineHTML(source, root)
        document.feed(markup)
        document.close()
        pages[source.relative_to(root)] = "".join(document.output)
    shutil.copytree(root, destination)
    for relative, markup in pages.items():
        (destination / relative).write_text(markup, encoding="utf-8")
    print(f"Exported {len(pages)} pages. Open {destination / 'index.html'} in a browser.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
