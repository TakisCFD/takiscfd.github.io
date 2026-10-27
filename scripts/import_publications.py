#!/usr/bin/env python3
"""Build website publication data without rewriting the source bibliography.

Run from the website root:
    python scripts/import_publications.py

The complete input is validated before any output is changed. The master BibTeX
download is a byte-for-byte copy of the source. Individual downloads preserve
each original entry and prepend any original @string/@preamble declarations.
Website display text is decoded to Unicode; the original citation text is not.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import html
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from urllib.parse import quote, unquote, urlsplit

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import InvalidName, splitname
    from bibtexparser.latexenc import latex_to_unicode
    import yaml
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing publication-import dependency. Run: "
        "python -m pip install -r requirements.txt"
    ) from exc


class PublicationImportError(ValueError):
    """The input cannot safely become a complete publication collection."""


@dataclass(frozen=True)
class RawEntry:
    kind: str
    key: str
    text: str


def raw_entries(text: str) -> tuple[list[RawEntry], list[str]]:
    """Find complete entries, respecting nested braces, quotes and escapes.

    This scanner preserves source slices; bibtexparser remains responsible for
    parsing their fields. Rejecting incomplete blocks also prevents its normal
    treatment of malformed entries as comments from silently dropping papers.
    """
    entries: list[RawEntry] = []
    declarations: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "%":
            end = text.find("\n", i)
            i = len(text) if end < 0 else end + 1
            continue
        if text[i] != "@":
            i += 1
            continue
        match = re.match(r"@\s*([A-Za-z][A-Za-z0-9_-]*)\s*", text[i:])
        if not match:
            i += 1
            continue
        start, kind = i, match.group(1).lower()
        i += match.end()
        if i >= len(text) or text[i] not in "{(":
            if kind == "comment":
                end = text.find("\n", i)
                i = len(text) if end < 0 else end + 1
                continue
            line = text.count("\n", 0, start) + 1
            raise PublicationImportError(f"@{kind} on line {line} needs an opening brace or parenthesis.")
        opening = text[i]
        content_start = i + 1
        depth = 1 if opening == "{" else 0
        outer_depth = depth
        quoted = False
        i += 1
        while i < len(text):
            char = text[i]
            if char == "\\":
                i += 2
                continue
            if char == '"' and depth == outer_depth:
                quoted = not quoted
            elif not quoted:
                if char == "%" and depth == outer_depth:
                    end = text.find("\n", i)
                    i = len(text) if end < 0 else end + 1
                    continue
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if opening == "{" and depth == 0:
                        break
                    if depth < outer_depth:
                        raise PublicationImportError(f"Unmatched closing brace in @{kind} entry.")
                elif char == ")" and opening == "(" and depth == 0:
                    break
            i += 1
        if i >= len(text):
            line = text.count("\n", 0, start) + 1
            raise PublicationImportError(f"Unclosed @{kind} entry beginning on line {line}.")
        raw = text[start:i + 1]
        if kind in {"string", "preamble"}:
            declarations.append(raw)
        elif kind != "comment":
            body = text[content_start:i]
            if "," not in body:
                raise PublicationImportError(f"@{kind} is missing a citation key and comma.")
            key = body.split(",", 1)[0].strip()
            if not key or re.search(r"[\s{}()]", key):
                raise PublicationImportError(f"Invalid citation key in @{kind}: use a nonempty key without spaces.")
            entries.append(RawEntry(kind, key, raw))
        i += 1
    return entries, declarations


def safe_key(key: str) -> str:
    ascii_key = unicodedata.normalize("NFKD", key).encode("ascii", "ignore").decode("ascii")
    result = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_key).strip(".-_").lower()
    if not result or len(result) > 160:
        raise PublicationImportError(f"Citation key {key!r} needs a short ASCII filename-compatible name.")
    if result == "publications":
        raise PublicationImportError("Citation key 'publications' is reserved for the master bibliography download.")
    return result


def display_text(value: str) -> str:
    # latex_to_unicode decodes accents and removes BibTeX case-protection groups.
    # It is applied only to display strings, never to source or download bytes.
    return " ".join(latex_to_unicode(value).split())


def split_authors(value: str) -> list[str]:
    """Split top-level 'and' while keeping corporate-author groups together."""
    result: list[str] = []
    start = i = depth = 0
    while i < len(value):
        if value[i] == "\\":
            i += 2
            continue
        if value[i] == "{":
            depth += 1
        elif value[i] == "}":
            depth -= 1
        elif depth == 0:
            match = re.match(r"\s+and\s+", value[i:], re.IGNORECASE)
            if match:
                result.append(value[start:i].strip())
                i += match.end()
                start = i
                continue
        i += 1
    result.append(value[start:].strip())
    return result


def author_string(value: str, key: str) -> str:
    names: list[str] = []
    for name in split_authors(value):
        if not name:
            raise PublicationImportError(f"Entry {key!r} contains an empty author name.")
        if name.casefold() == "others":
            names.append("et al.")
            continue
        if name.startswith("{") and name.endswith("}"):
            formatted = display_text(name)
        else:
            try:
                parts = splitname(name, strict_mode=True)
            except (InvalidName, StopIteration) as exc:
                raise PublicationImportError(f"Entry {key!r} has an invalid author name: {name!r}.") from exc
            formatted = display_text(" ".join(parts["first"] + parts["von"] + parts["last"]))
            if parts["jr"]:
                formatted += ", " + display_text(" ".join(parts["jr"]))
        if not formatted:
            raise PublicationImportError(f"Entry {key!r} has an empty author after decoding.")
        names.append(formatted)
    if len(names) < 2:
        return names[0] if names else ""
    if len(names) == 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def safe_url(value: str, *, field: str, key: str) -> str:
    """Allow explicit HTTP(S) or local links, never executable URL schemes."""
    value = value.strip()
    if not value:
        return ""
    decoded = html.unescape(unquote(value))
    if any(ord(char) <= 32 or ord(char) == 127 for char in decoded) or "\\" in decoded:
        raise PublicationImportError(f"Entry {key!r}: {field} contains whitespace, a control character or a backslash.")
    if any(char in value for char in '<>"{}'):
        raise PublicationImportError(f"Entry {key!r}: {field} must be a plain URL, not HTML or a LaTeX command.")
    try:
        parsed, decoded_parsed = urlsplit(value), urlsplit(decoded)
        if parsed.scheme:
            if parsed.scheme.lower() not in {"http", "https"} or decoded_parsed.scheme.lower() not in {"http", "https"}:
                raise ValueError("unsupported scheme")
            if not parsed.hostname or parsed.username is not None or parsed.password is not None:
                raise ValueError("invalid host or embedded credentials")
            _ = parsed.port
        else:
            if parsed.netloc or decoded_parsed.netloc or decoded_parsed.scheme:
                raise ValueError("protocol-relative or encoded scheme")
            if ":" in decoded.split("/", 1)[0] or ".." in decoded_parsed.path.split("/"):
                raise ValueError("unsafe local path")
    except ValueError as exc:
        raise PublicationImportError(f"Entry {key!r}: {field} must use https/http or a safe local path.") from exc
    return value


def doi_url(value: str, key: str) -> str:
    value = value.strip()
    if not value:
        return ""
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:\s*", "", value, flags=re.IGNORECASE)
    if not re.fullmatch(r"10\.\d{4,9}/[^\s]+", value):
        raise PublicationImportError(f"Entry {key!r}: DOI should look like 10.1234/example, or a doi.org URL.")
    return safe_url("https://doi.org/" + quote(value, safe="/:;()+-._~"), field="doi", key=key)


def make_record(entry: dict[str, str], filename: str, url_prefix: str) -> dict[str, object]:
    key = entry["ID"]
    for field in ("title", "author", "year"):
        if not str(entry.get(field, "")).strip():
            raise PublicationImportError(f"Entry {key!r} is missing required field {field!r}.")
    if not re.fullmatch(r"[1-9]\d{3}", entry["year"].strip()):
        raise PublicationImportError(f"Entry {key!r}: year must be a four-digit number, such as 2026.")
    title = display_text(entry["title"])
    if not title:
        raise PublicationImportError(f"Entry {key!r} has an empty display title.")
    selected_value = entry.get("selected", "false").strip().casefold()
    if selected_value not in {"true", "false", "yes", "no", "1", "0"}:
        raise PublicationImportError(f"Entry {key!r}: selected must be true or false.")
    links = {field: safe_url(entry.get(field, ""), field=field, key=key) for field in ("html", "url", "pdf", "code")}
    doi = doi_url(entry.get("doi", ""), key)
    eprint = entry.get("eprint", "").strip()
    archive = entry.get("archiveprefix", "").strip().casefold()
    arxiv = ""
    if eprint and (archive == "arxiv" or re.fullmatch(r"\d{4}\.\d{4,5}(?:v[1-9]\d*)?", eprint)):
        if not re.fullmatch(r"(?:\d{4}\.\d{4,5}|[A-Za-z][A-Za-z0-9.-]*/\d{7})(?:v[1-9]\d*)?", eprint):
            raise PublicationImportError(f"Entry {key!r}: arXiv eprint identifier is malformed.")
        arxiv = "https://arxiv.org/abs/" + eprint
    kind = entry["ENTRYTYPE"].casefold()
    journal = entry.get("journal", "").strip()
    is_preprint = kind == "unpublished" or "arxiv" in journal.casefold() or (
        not journal and not entry.get("booktitle") and (arxiv or "preprint" in entry.get("note", "").casefold())
    )
    types = {"article": "journal", "inproceedings": "conference", "conference": "conference", "proceedings": "proceedings", "book": "book", "inbook": "book chapter", "incollection": "book chapter", "phdthesis": "thesis", "mastersthesis": "thesis", "techreport": "report", "manual": "manual", "software": "software"}
    publication_type = "preprint" if is_preprint else types.get(kind, "other")
    subtype = entry.get("entrysubtype", "").strip().casefold()
    if subtype == "conference presentation":
        publication_type = "conference presentation"
    status = entry.get("status", "").strip().casefold()
    if status not in {"", "withdrawn", "retracted"}:
        raise PublicationImportError(f"Entry {key!r}: status must be empty, withdrawn or retracted.")
    venue = journal or entry.get("booktitle") or entry.get("howpublished") or entry.get("school") or entry.get("institution") or entry.get("publisher") or ("arXiv preprint" if arxiv else "Preprint" if is_preprint else "")
    topics: list[str] = []
    for topic in re.split(r"[,;]", entry.get("keywords", "")):
        topic = topic.strip()
        if topic and topic.casefold() not in {item.casefold() for item in topics}:
            topics.append(topic)
    volume = display_text(entry.get("volume", ""))
    issue = display_text(entry.get("number", ""))
    pages = display_text(entry.get("pages", entry.get("eid", ""))).replace("--", "–")
    citation_details = volume + (("(" + issue + ")") if issue and volume else issue)
    if pages:
        citation_details += (", " if citation_details else "") + pages
    return {
        "id": key,
        "title": title,
        "authors": author_string(entry["author"], key),
        "year": int(entry["year"]),
        "venue": display_text(str(venue)),
        "citation_details": citation_details,
        "type": publication_type,
        "status": status,
        "conference": entry.get("conference", "false").strip().casefold() in {"true", "yes", "1"} or publication_type in {"conference", "conference presentation", "proceedings"},
        "event_year": entry.get("eventyear", "").strip(),
        "topics": topics,
        "selected": selected_value in {"true", "yes", "1"},
        "doi_url": doi,
        "url": links["html"] or links["url"] or arxiv or doi,
        "preprint_url": arxiv,
        "pdf": links["pdf"],
        "code": links["code"],
        "bibtex_url": url_prefix.rstrip("/") + "/" + filename + ".bib",
    }


def prepare_import(source_bytes: bytes, url_prefix: str) -> tuple[list[dict[str, object]], dict[str, bytes]]:
    try:
        text = source_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PublicationImportError("The source bibliography must use UTF-8 encoding.") from exc
    blocks, declarations = raw_entries(text)
    if not blocks:
        raise PublicationImportError("No bibliography entries found; no existing output was changed.")
    by_key: dict[str, RawEntry] = {}
    filenames: dict[str, str] = {}
    seen_filenames: dict[str, str] = {}
    for block in blocks:
        if block.key in by_key:
            raise PublicationImportError(f"Duplicate citation key {block.key!r}; each entry needs a unique ID.")
        filename = safe_key(block.key)
        if filename in seen_filenames:
            raise PublicationImportError(f"Citation keys {seen_filenames[filename]!r} and {block.key!r} map to the same safe filename; rename one.")
        seen_filenames[filename] = block.key
        filenames[block.key] = filename
        by_key[block.key] = block
    parser = BibTexParser(common_strings=True, ignore_nonstandard_types=False, homogenize_fields=False, interpolate_strings=True)
    try:
        database = bibtexparser.loads(text, parser=parser)
    except Exception as exc:
        raise PublicationImportError(f"BibTeX syntax could not be parsed: {exc}") from exc
    parsed_keys = [entry["ID"] for entry in database.entries]
    if len(parsed_keys) != len(blocks) or set(parsed_keys) != set(by_key):
        missing = sorted(set(by_key).difference(parsed_keys))
        raise PublicationImportError("BibTeX parser could not read every entry" + (": " + ", ".join(missing) if missing else ". Check entry syntax."))
    records = [make_record(entry, filenames[entry["ID"]], url_prefix) for entry in database.entries]
    records.sort(key=lambda row: (-int(row["year"]), str(row["title"]).casefold(), str(row["id"]).casefold()))
    prefix = "\n\n".join(declarations)
    if prefix:
        prefix += "\n\n"
    downloads = {filenames[block.key] + ".bib": (prefix + block.text).encode("utf-8") for block in blocks}
    downloads["publications.bib"] = source_bytes
    return records, downloads


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".publication-import-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def import_publications(source: Path, output: Path, bibtex_dir: Path, url_prefix: str = "/assets/bibtex") -> int:
    if source.resolve() == output.resolve():
        raise PublicationImportError("The YAML output must not overwrite the source bibliography.")
    safe_url(url_prefix, field="BibTeX URL prefix", key="configuration")
    prefix_parts = urlsplit(url_prefix)
    if not url_prefix.startswith("/") or prefix_parts.netloc or prefix_parts.query or prefix_parts.fragment:
        raise PublicationImportError("The BibTeX URL prefix must be a site-local absolute path, such as /assets/bibtex.")
    try:
        source_bytes = source.read_bytes()
    except OSError as exc:
        raise PublicationImportError(f"Cannot read source bibliography {source}: {exc.strerror or exc}") from exc
    records, downloads = prepare_import(source_bytes, url_prefix)
    if any(source.resolve() == (bibtex_dir / filename).resolve() for filename in downloads):
        raise PublicationImportError("The BibTeX download directory must not overwrite the source bibliography.")
    if any(output.resolve() == (bibtex_dir / filename).resolve() for filename in downloads):
        raise PublicationImportError("The YAML output path collides with a BibTeX download path.")
    rendered = yaml.safe_dump(records, allow_unicode=True, sort_keys=False, width=110).encode("utf-8")
    # All validation and serialization finish above this line. Invalid input
    # cannot create, truncate, or replace any output file or directory.
    for filename in sorted(downloads):
        atomic_write(bibtex_dir / filename, downloads[filename])
    atomic_write(output, rendered)
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=Path("_bibliography/papers.bib"))
    parser.add_argument("--output", type=Path, default=Path("_data/publications.yml"))
    parser.add_argument("--bibtex-dir", type=Path, default=Path("assets/bibtex"))
    parser.add_argument("--bibtex-url-prefix", default="/assets/bibtex", help="Public URL path, independent of --bibtex-dir's filesystem location")
    args = parser.parse_args(argv)
    try:
        count = import_publications(args.source, args.output, args.bibtex_dir, args.bibtex_url_prefix)
    except (PublicationImportError, OSError) as exc:
        print(f"Publication import failed: {exc}", file=sys.stderr)
        return 2
    print(f"Imported {count} publications into {args.output}; BibTeX downloads in {args.bibtex_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
