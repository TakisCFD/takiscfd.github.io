#!/usr/bin/env python3
"""Validate editable content before building or enabling publication."""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--for-publish", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)

    def read_yaml(path: str):
        try:
            return yaml.safe_load((root / path).read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            fail(f"{path}: {exc}")
            return None

    def required(record: dict, fields: list[str], label: str) -> None:
        for field in fields:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"{label}: {field} must contain text.")
            elif value.lower() in {"full name", "image title", "creator name", "event or host institution"} or value.startswith("Replace with"):
                fail(f"{label}: replace the example value in {field}.")

    def url(value, label: str, local: bool = False, must_exist: bool = False) -> None:
        if value in (None, ""):
            return
        if not isinstance(value, str):
            fail(f"{label}: expected a URL string.")
            return
        parts = urlsplit(value)
        if parts.scheme in {"http", "https"} and parts.netloc and not parts.username and not parts.password:
            return
        if local and value.startswith("/") and not value.startswith("//") and ".." not in Path(parts.path).parts:
            if must_exist and not (root / parts.path.lstrip("/")).is_file():
                fail(f"{label}: file does not exist: {parts.path}")
            return
        fail(f"{label}: use an http(s) URL" + (" or a site path beginning with /." if local else "."))

    config = read_yaml("_config.yml")
    if not isinstance(config, dict):
        fail("_config.yml must contain a mapping.")
        config = {}
    profile = config.get("profile", {})
    if not isinstance(profile, dict):
        fail("profile must be a mapping.")
        profile = {}
    required(profile, ["name", "role", "institution", "email"], "profile")
    if isinstance(profile.get("email"), str) and profile.get("email") and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", profile["email"]):
        fail("profile.email must be a valid email address.")
    for field in ["institutional_url", "orcid", "scholar"]:
        url(profile.get(field), f"profile.{field}")
    for field in ["portrait", "cv"]:
        url(profile.get(field), f"profile.{field}", local=True, must_exist=True)

    site_url = config.get("url", "")
    baseurl = config.get("baseurl", "")
    if site_url:
        parsed = urlsplit(str(site_url))
        if parsed.scheme != "https" or not parsed.netloc or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            fail("url must be an HTTPS origin, e.g. https://username.github.io; put a project path in baseurl.")
        if parsed.username or parsed.password:
            fail("url must not contain credentials.")
    if not isinstance(baseurl, str) or (baseurl and (not baseurl.startswith("/") or baseurl.startswith("//") or baseurl.endswith("/") or ".." in baseurl or "?" in baseurl or "#" in baseurl or "\\" in baseurl)):
        fail("baseurl must be empty or a path such as /personal-website without a trailing slash.")
    username = config.get("github_username", "")
    if username and (not isinstance(username, str) or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username)):
        fail("github_username must be the account name, not a full URL.")
    if args.for_publish:
        if not site_url:
            fail("Set url in _config.yml before publishing.")
        if not username:
            fail("Set github_username in _config.yml before publishing.")
        if "YOUR-USERNAME" in str(site_url).upper():
            fail("Replace the example GitHub address before publishing.")
    if not isinstance(config.get("indexable"), bool):
        fail("indexable must be true or false, without quotes.")

    analytics = config.get("analytics", {})
    if not isinstance(analytics, dict):
        fail("analytics must be a mapping.")
        analytics = {}
    if not isinstance(analytics.get("enabled"), bool):
        fail("analytics.enabled must be true or false, without quotes.")
    code = analytics.get("goatcounter_code", "")
    if code and (not isinstance(code, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9-]*", code)):
        fail("analytics.goatcounter_code must be a site code, not a URL, password or API token.")
    if analytics.get("enabled") and not code:
        fail("Set analytics.goatcounter_code before enabling analytics.")

    for filename, required_fields in [
        ("_data/people.yml", ["name", "role", "research_topic"]),
        ("_data/gallery.yml", ["id", "title", "category", "image", "alt", "caption"]),
    ]:
        records = read_yaml(filename)
        if not isinstance(records, list):
            fail(f"{filename} must contain a list; use [] for an empty collection.")
            continue
        seen = set()
        for index, record in enumerate(records, 1):
            label = f"{filename} record {index}"
            if not isinstance(record, dict):
                fail(f"{label}: expected a mapping.")
                continue
            required(record, required_fields, label)
            if filename.endswith("people.yml"):
                if record.get("status") not in {"current", "alumni"}:
                    fail(f"{label}: status must be current or alumni.")
                for field in ["profile_url", "thesis_url"]:
                    url(record.get(field), f"{label}.{field}")
                url(record.get("photo"), f"{label}.photo", local=True, must_exist=True)
            else:
                identifier = record.get("id")
                if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", identifier):
                    fail(f"{label}: id must contain lowercase letters, digits and hyphens.")
                elif identifier in seen:
                    fail(f"{label}: duplicate id {identifier}.")
                if isinstance(identifier, str):
                    seen.add(identifier)
                url(record.get("image"), f"{label}.image", local=True, must_exist=True)
                url(record.get("source_url"), f"{label}.source_url")
                url(record.get("original_url"), f"{label}.original_url", local=True, must_exist=True)
                url(record.get("project_path"), f"{label}.project_path", local=True)

    for collection in ["_research", "_talks", "_news"]:
        for path in sorted((root / collection).glob("*.md")):
            label = str(path.relative_to(root))
            try:
                content = path.read_text(encoding="utf-8")
                if not content.startswith("---\n"):
                    fail(f"{label}: missing YAML metadata at the top of the file.")
                    continue
                metadata = yaml.safe_load(content.split("---", 2)[1])
                if not isinstance(metadata, dict):
                    fail(f"{label}: metadata must be a mapping.")
                    continue
                required(metadata, ["title"], label)
                if collection == "_talks":
                    required(metadata, ["event"], label)
                    try:
                        dt.date.fromisoformat(str(metadata.get("event_date", "")))
                    except ValueError:
                        fail(f"{label}: event_date must be YYYY-MM-DD.")
                    if metadata.get("date_precision", "day") not in {"day", "month", "year"}:
                        fail(f"{label}: date_precision must be day, month or year.")
                    for field in ["slides_url", "recording_url", "event_url"]:
                        url(metadata.get(field), f"{label}.{field}", local=True)
            except (OSError, yaml.YAMLError, IndexError) as exc:
                fail(f"{label}: {exc}")

    topics = read_yaml("_data/msc_topics.yml")
    if not isinstance(topics, list):
        fail("_data/msc_topics.yml must contain a list.")
    else:
        for index, record in enumerate(topics, 1):
            label = f"_data/msc_topics.yml record {index}"
            if not isinstance(record, dict) or set(record) != {"year", "course", "topic"}:
                fail(f"{label}: use only year, course and topic; this archive is anonymous.")
            else:
                required(record, ["year", "course", "topic"], label)
    animations = read_yaml("_data/animations.yml")
    if not isinstance(animations, list):
        fail("_data/animations.yml must contain a list.")
    else:
        for index, record in enumerate(animations, 1):
            label = f"_data/animations.yml record {index}"
            if not isinstance(record, dict):
                fail(f"{label}: expected a mapping.")
                continue
            required(record, ["id", "title", "caption", "url"], label)
            is_local_video = record.get("type") == "video"
            url(record.get("url"), f"{label}.url", local=is_local_video, must_exist=is_local_video)
            url(record.get("source_url"), f"{label}.source_url")
            if is_local_video:
                required(record, ["poster"], label)
                url(record.get("poster"), f"{label}.poster", local=True, must_exist=True)
            url(record.get("research_path"), f"{label}.research_path", local=True)

    if errors:
        print("Content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Editable content is valid." + (" Publication settings are present." if args.for_publish else " Publication remains disabled by default."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
