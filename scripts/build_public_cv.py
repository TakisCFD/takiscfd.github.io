#!/usr/bin/env python3
"""Build a genuine LaTeX public CV using only the website's public data.

Run scripts/import_publications.py first. Then:
    python scripts/build_public_cv.py
    python scripts/build_public_cv.py --tex-only

The generated .tex is self-contained except for an optional portrait. For a
portable bundle, put portrait.png beside it and compile twice with:
    xelatex -no-shell-escape panagiotis-tsoutsanis-public-cv.tex

XeLaTeX is preferred; LuaLaTeX and pdfLaTeX are supported alternatives.
No original private CV, shell escape, network service or ReportLab is used.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote, urlsplit

import yaml


class CVBuildError(ValueError):
    """Public content or local LaTeX compilation could not be completed."""


TEX_CHARACTERS = {
    "\\": r"\textbackslash{}",
    "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%",
    "$": r"\$", "#": r"\#", "_": r"\_",
    "^": r"\textasciicircum{}", "~": r"\textasciitilde{}",
    "\u00a0": "~", "\u2010": "-", "\u2011": "-", "\u2012": "--",
    "\u2013": "--", "\u2014": "---", "\u2212": r"\ensuremath{-}",
    "\u2018": "'", "\u2019": "'", "\u201c": chr(96) * 2, "\u201d": "''",
    "\u00b7": r"\,\textperiodcentered{}\,",
    "\u03b1": r"\ensuremath{\alpha}", "\u03b2": r"\ensuremath{\beta}",
    "\u03b3": r"\ensuremath{\gamma}", "\u03b4": r"\ensuremath{\delta}",
    "\u03b5": r"\ensuremath{\varepsilon}", "\u03b8": r"\ensuremath{\theta}",
    "\u03bb": r"\ensuremath{\lambda}", "\u03bc": r"\ensuremath{\mu}",
    "\u03c0": r"\ensuremath{\pi}", "\u03c1": r"\ensuremath{\rho}",
    "\u03c3": r"\ensuremath{\sigma}", "\u03c4": r"\ensuremath{\tau}",
    "\u03c6": r"\ensuremath{\phi}", "\u03c9": r"\ensuremath{\omega}",
    "\u0394": r"\ensuremath{\Delta}", "\u03a9": r"\ensuremath{\Omega}",
    "\u2080": r"\textsubscript{0}", "\u2081": r"\textsubscript{1}",
    "\u2082": r"\textsubscript{2}", "\u2083": r"\textsubscript{3}",
    "\u00b0": r"\ensuremath{^\circ}",
}


def tex(value: object) -> str:
    """Escape plain public text; data can never introduce TeX commands."""
    text = " ".join(str(value).split())
    if any(ord(char) < 32 for char in text):
        raise CVBuildError("A public text field contains a control character.")
    return "".join(TEX_CHARACTERS.get(char, char) for char in text)


def checked_url(value: object, config: dict) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    if any(ord(char) <= 32 for char in value) or "\\" in value:
        raise CVBuildError("A public link contains whitespace or a backslash.")
    if value.startswith("/") and not value.startswith("//"):
        origin = str(config.get("url") or "").rstrip("/")
        if not origin:
            return ""
        value = origin + str(config.get("baseurl") or "").rstrip("/") + value
    parsed = urlsplit(value)
    if parsed.scheme not in {"https", "http", "mailto"}:
        raise CVBuildError("CV links must use https, http or mailto.")
    if parsed.scheme in {"https", "http"}:
        if not parsed.netloc or parsed.username is not None or parsed.password is not None:
            raise CVBuildError("A public link has no host or contains credentials.")
    elif "@" not in parsed.path:
        raise CVBuildError("A mailto link needs an email address.")
    return quote(value, safe=":/?#[]@!$&'()*+,;=%-._~")


def link(label: object, value: object, config: dict) -> str:
    url = checked_url(value, config)
    if not url:
        return ""
    escaped = "".join("\\" + c if c in "%#_&$" else c for c in url)
    return r"\href{" + escaped + "}{" + tex(label) + "}"


def read_yaml(root: Path, name: str, expected: type):
    try:
        data = yaml.safe_load((root / name).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CVBuildError(f"Cannot read {name}: {exc}") from exc
    if not isinstance(data, expected):
        raise CVBuildError(f"{name} must contain a {expected.__name__}.")
    return data


def paragraphs(value: object) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return [item for item in value if item.strip()]
    raise CVBuildError("Research overview and biography must be text or a list of paragraphs.")


def require_text(record: dict, keys: tuple[str, ...], label: str) -> None:
    for key in keys:
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise CVBuildError(f"{label}: {key} must contain text.")


def entry(title: str, detail: str = "", meta: str = "", links: str = "", year: str = "") -> str:
    """Keep each entry and its optional year heading together."""
    lines = [r"\begin{cventry}"]
    if year:
        lines.append(r"\cvyear{" + tex(year) + "}")
    lines.append(r"\cvtitle{" + title + "}")
    if detail:
        lines.append(r"\cvdetail{" + detail + "}")
    if meta:
        lines.append(r"\cvmeta{" + meta + "}")
    if links:
        lines.append(r"\cvlinks{" + links + "}")
    lines.append(r"\end{cventry}")
    return "\n".join(lines)


def section(title: str, new_page: bool = False) -> str:
    return (r"\clearpage" + "\n" if new_page else "") + r"\cvsection{" + tex(title) + "}"


def talk_date(record: dict) -> str:
    try:
        value = date.fromisoformat(str(record["event_date"]))
    except (KeyError, ValueError) as exc:
        raise CVBuildError("A talk has an invalid event_date.") from exc
    precision = record.get("date_precision", "day")
    patterns = {"month": "%B %Y", "year": "%Y", "day": "%d %B %Y"}
    if precision not in patterns:
        raise CVBuildError("Talk date_precision must be day, month or year.")
    return value.strftime(patterns[precision])


PREAMBLE = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[a4paper,left=22mm,right=22mm,top=23mm,bottom=23mm,
            headheight=14pt,headsep=6mm,footskip=11mm]{geometry}
\usepackage{iftex}
\ifPDFTeX
  \usepackage[T1]{fontenc}
  \usepackage[utf8]{inputenc}
  \IfFileExists{tgpagella.sty}{\usepackage{tgpagella}}{\usepackage{lmodern}}
\else
  \usepackage{fontspec}
  \defaultfontfeatures{Ligatures=TeX}
  \IfFontExistsTF{TeX Gyre Pagella}
    {\setmainfont{TeX Gyre Pagella}}
    {\setmainfont{Latin Modern Roman}[SmallCapsFont={Latin Modern Roman Caps}]}
  \setsansfont{Latin Modern Sans}
\fi
\usepackage[english]{babel}
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{ragged2e}
\usepackage{needspace}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage[unicode]{hyperref}
\usepackage{bookmark}
\definecolor{Ink}{HTML}{203039}
\definecolor{Teal}{HTML}{245D60}
\definecolor{Muted}{HTML}{58666D}
\definecolor{Rule}{HTML}{C8D3D3}
\hypersetup{colorlinks=true,urlcolor=Teal,linkcolor=Teal,
            pdfauthor={%%AUTHOR%%},
            pdftitle={%%AUTHOR%% -- Academic CV},
            pdfsubject={Research, publications, teaching and supervision}}
\urlstyle{same}
\color{Ink}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{2em}
\clubpenalty=10000
\widowpenalty=10000
\raggedbottom
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textsc{%%AUTHOR%%}}
\fancyhead[R]{\small\color{Muted}\nouppercase{\leftmark}}
\fancyfoot[L]{\footnotesize\color{Muted}\textsc{Curriculum vitae}}
\fancyfoot[R]{\footnotesize\color{Muted}\thepage\,/\,\pageref*{LastPage}}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{opening}{
  \fancyhf{}
  \fancyfoot[L]{\footnotesize\color{Muted}\textsc{Curriculum vitae}}
  \fancyfoot[R]{\footnotesize\color{Muted}\thepage\,/\,\pageref*{LastPage}}
  \renewcommand{\headrulewidth}{0pt}
}
\titleformat{\section}
  {\Large\bfseries\color{Ink}}{}{0pt}{}
  [\vspace{3pt}{\color{Rule}\titlerule[0.45pt]}]
\titlespacing*{\section}{0pt}{17pt}{11pt}
\newcommand{\cvsection}[1]{%
  \par\Needspace{10\baselineskip}\section*{#1}\markboth{#1}{}}
\newlength{\cventrysep}
\setlength{\cventrysep}{7pt}
\newenvironment{cventry}{%
  \par\noindent\begin{minipage}{\linewidth}
  \RaggedRight\fontsize{9.8}{12.5}\selectfont
}{\end{minipage}\par\addvspace{\cventrysep}}
\newcommand{\cvtitle}[1]{{\bfseries #1\par}\vspace{1pt}}
\newcommand{\cvdetail}[1]{{#1\par}\vspace{1pt}}
\newcommand{\cvmeta}[1]{{\fontsize{9}{11.5}\selectfont\color{Muted}#1\par}\vspace{1pt}}
\newcommand{\cvlinks}[1]{{\fontsize{9}{11.5}\selectfont #1\par}}
\newcommand{\cvyear}[1]{{\color{Teal}\bfseries\fontsize{11}{13}\selectfont #1\par}\vspace{6pt}}
\newcommand{\cvsubheading}[1]{%
  \par\Needspace{7\baselineskip}{\large\bfseries\color{Teal}#1\par}\vspace{6pt}}
\begin{document}
\thispagestyle{opening}
"""


def build_tex(root: Path, tex_path: Path) -> tuple[str, dict[str, int]]:
    config = read_yaml(root, "_config.yml", dict)
    profile = read_yaml(root, "_data/public_profile.yml", dict)
    people = read_yaml(root, "_data/people.yml", list)
    topics = read_yaml(root, "_data/msc_topics.yml", list)
    publications = read_yaml(root, "_data/publications.yml", list)
    identity = config.get("profile", {})
    require_text(identity, ("name", "role", "institution", "email"), "Profile")

    for person in people:
        require_text(person, ("name", "role", "research_topic"), "Research supervisee")
        if person.get("status") not in {"current", "alumni"}:
            raise CVBuildError("Every research supervisee needs current or alumni status.")
        if re.search(r"\bMSc\b", person["role"], re.IGNORECASE):
            raise CVBuildError("Named MSc taught-student records are not permitted in this CV.")
    for item in topics:
        if not isinstance(item, dict) or set(item) != {"year", "course", "topic"}:
            raise CVBuildError("MSc records must contain only year, course and topic.")
        require_text(item, ("year", "course", "topic"), "MSc topic")
    ids = set()
    for publication in publications:
        require_text(publication, ("id", "title", "authors", "type"), "Publication")
        if publication["id"] in ids:
            raise CVBuildError("The publication data contains duplicate IDs.")
        ids.add(publication["id"])
        if not re.fullmatch(r"[1-9]\d{3}", str(publication.get("year", ""))):
            raise CVBuildError("Each publication needs a four-digit citation year.")
    publications.sort(key=lambda p: (-int(p["year"]), p["title"].casefold(), p["id"]))

    talks = []
    for path in sorted((root / "_talks").glob("*.md")):
        try:
            raw = path.read_text(encoding="utf-8")
            record = yaml.safe_load(raw.split("---", 2)[1])
        except (OSError, IndexError, yaml.YAMLError) as exc:
            raise CVBuildError(f"Cannot read talk metadata from {path.name}.") from exc
        if not isinstance(record, dict):
            raise CVBuildError(f"Talk metadata in {path.name} must be a mapping.")
        require_text(record, ("title", "event"), path.name)
        talk_date(record)
        talks.append(record)
    talks.sort(key=lambda item: str(item["event_date"]), reverse=True)

    overview = paragraphs(profile.get("research_overview") or profile.get("biography", []))
    expertise = profile.get("expertise")
    if not expertise:
        expertise = [{"name": item, "description": ""} for item in profile.get("research_interests", [])]
    if not isinstance(expertise, list):
        raise CVBuildError("Areas of expertise must be a list.")
    for item in expertise:
        if not isinstance(item, dict):
            raise CVBuildError("Each expertise entry needs a name and optional description.")
        require_text(item, ("name",), "Expertise")

    portrait_value = str(identity.get("portrait") or "").strip()
    portrait = ""
    if portrait_value:
        local = (root / portrait_value.lstrip("/")).resolve()
        if not local.is_relative_to(root) or not local.is_file():
            raise CVBuildError("The configured public portrait must be a file within the site.")
        relative = Path(os.path.relpath(local, tex_path.parent)).as_posix()
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", relative):
            raise CVBuildError("Use a simple portrait filename with letters, numbers, dots or hyphens.")
        portrait = (
            r"\IfFileExists{portrait.png}{\includegraphics[width=\linewidth]{portrait.png}}"
            + r"{\IfFileExists{" + relative + r"}{\includegraphics[width=\linewidth]{"
            + relative + r"}}{}}"
        )

    contact_links = [link("ORCID", identity.get("orcid"), config),
                     link("Google Scholar", identity.get("scholar"), config),
                     link("Institutional profile", identity.get("institutional_url"), config),
                     link("UCNS3D", config.get("software", {}).get("url"), config)]
    links_line = r" \enspace\textperiodcentered{}\enspace ".join(x for x in contact_links if x)
    body = [
        r"\begin{minipage}[t]{0.78\linewidth}\vspace{0pt}",
        r"{\small\color{Teal}\textsc{Academic curriculum vitae}\par}\vspace{6pt}",
        r"{\fontsize{28}{32}\selectfont\bfseries " + tex(identity["name"]) + r"\par}",
        r"\vspace{5pt}{\large " + tex(identity["role"]) + r"\par}",
        tex(identity["institution"]) + r"\par",
        r"{\small " + link(identity["email"], "mailto:" + identity["email"], config) + r"\par}",
        r"\vspace{2pt}{\footnotesize " + links_line + r"\par}",
        r"\end{minipage}\hfill\begin{minipage}[t]{0.17\linewidth}\vspace{2pt}",
        portrait,
        r"\end{minipage}",
        section("Research overview"),
    ]
    body.extend(tex(paragraph) + "\n\n" for paragraph in overview)
    body.append(section("Areas of expertise"))
    for item in expertise:
        body.append(
            r"\par\Needspace{4\baselineskip}{\bfseries " + tex(item["name"]) + r".} "
            + tex(item.get("description", "")) + r"\par\vspace{3pt}"
        )

    body.append(section("Education and professional development", new_page=True))
    for item in profile.get("education", []):
        detail = tex(item.get("institution", ""))
        if item.get("thesis"):
            detail += r"\par{\small\itshape Thesis: " + tex(item["thesis"]) + "}"
        body.append(entry(tex(item["qualification"]), detail, tex(item.get("years", ""))))
    body.append(section("Selected distinctions"))
    for item in profile.get("distinctions", []):
        body.append(entry(tex(item["title"]), tex(item.get("work", "")),
                          tex(item.get("year", "")), link("Award record", item.get("url"), config)))
    body.append(section("Research software"))
    body.append(tex("UCNS3D is an open-source framework for high-order computational fluid dynamics "
                    "on unstructured meshes. I am its author and lead developer."))
    software = config.get("software", {})
    body.append(r"\par " + r"\enspace\textperiodcentered{}\enspace ".join(
        value for value in [link("ucns3d.com", software.get("url"), config),
                            link("Source code", software.get("repository"), config)] if value))
    body.append(section("Teaching and supervision"))
    body.append(tex("My teaching connects numerical analysis, fluid physics and scientific software. "
                    "It covers numerical methods for compressible flows and partial differential equations, "
                    "high-performance computing, turbulence modelling, mesh generation and simulation practice."))
    body.append("\n\n" + tex("I am a Fellow of the Higher Education Academy and hold a postgraduate certificate "
                             "in Academic Practice in Higher Education."))

    body.append(section("Research students and alumni", new_page=True))
    for state, label in [("current", "Current research students"), ("alumni", "Research alumni")]:
        records = [p for p in people if p["status"] == state]
        if records:
            body.append(r"\cvsubheading{" + tex(label) + "}")
        for person in records:
            meta = person["role"] + (" · " + str(person["years"]) if person.get("years") else "")
            body.append(entry(tex(person["name"]), tex(person["research_topic"]), tex(meta)))

    conference_records = [p for p in publications if p.get("conference") is True or p["type"].startswith("conference")]
    conference_ids = {p["id"] for p in conference_records}
    other_records = [p for p in publications if p["id"] not in conference_ids]
    for label, records in [("Publications", other_records), ("Conference contributions", conference_records)]:
        if not records:
            continue
        body.append(section(label, new_page=True))
        intro = ("Journal articles, preprints and reports, arranged by citation year. "
                 "Publication status is retained where relevant." if label == "Publications" else
                 "Conference papers and presentations, arranged by citation year. "
                 "An event year is shown separately when it differs.")
        body.append(r"{\small\color{Muted}" + tex(intro) + "}\n")
        last_year = None
        for pub in records:
            venue = tex(pub.get("venue", ""))
            details = tex(pub.get("citation_details", ""))
            citation = (r"\textit{" + venue + "}" if venue else "")
            if details:
                citation += (", " if citation else "") + details
            kind = {"journal": "Journal article", "conference": "Conference paper",
                    "conference presentation": "Conference presentation"}.get(pub["type"], pub["type"].capitalize())
            if pub.get("status"):
                kind += " · " + str(pub["status"]).upper()
            meta = tex(kind)
            if pub.get("event_year") and str(pub["event_year"]) != str(pub["year"]):
                meta += tex(" · Event year: " + str(pub["event_year"]))
            if citation:
                meta = citation + r"\par " + meta
            target = pub.get("doi_url") or pub.get("url")
            target_label = "DOI" if pub.get("doi_url") else "Preprint" if pub["type"] == "preprint" else "Publication / event record"
            publication_links = [link(target_label, target, config)]
            if pub.get("preprint_url") and pub["preprint_url"] != target:
                publication_links.append(link("Preprint", pub["preprint_url"], config))
            body.append(entry(tex(pub["title"]), tex(pub["authors"]), meta,
                              r"\enspace\textperiodcentered{}\enspace ".join(x for x in publication_links if x),
                              str(pub["year"]) if pub["year"] != last_year else ""))
            last_year = pub["year"]

    body.append(section("Invited talks and seminars", new_page=True))
    for talk in talks:
        event = talk["event"] + (" · " + talk["location"] if talk.get("location") else "")
        meta = talk_date(talk) + " · " + talk.get("talk_type", "Seminar")
        talk_links = [link(label, talk.get(key), config)
                      for label, key in [("Recording", "recording_url"), ("Slides", "slides_url"), ("Event", "event_url")]]
        body.append(entry(tex(talk["title"]), tex(event), tex(meta),
                          r"\enspace\textperiodcentered{}\enspace ".join(value for value in talk_links if value)))

    body.append(section("MSc research topics", new_page=True))
    body.append(r"\setlength{\cventrysep}{5pt}")
    body.append(r"{\small\color{Muted}" + tex(
        "Topics from individual and group MSc research projects, organised by academic year.") + "}\n")
    years = defaultdict(list)
    for topic in topics:
        years[topic["year"]].append(topic)
    for year in sorted(years, reverse=True):
        for index, topic in enumerate(years[year]):
            body.append(entry(tex(topic["topic"]), "", tex(topic["course"]), year=year if index == 0 else ""))
    body.append(r"\end{document}")

    summary = {"publications": len(publications), "conference_contributions": len(conference_records),
               "people": len(people), "talks": len(talks), "msc_topics": len(topics)}
    comment = (
        "% Generated from the website's public data only. Edit the public YAML/BibTeX\n"
        "% source if you want changes to survive the next generator run.\n"
        "% Portable compilation: put portrait.png next to this file (optional), then run\n"
        "% xelatex -no-shell-escape -interaction=nonstopmode panagiotis-tsoutsanis-public-cv.tex\n"
        "% twice. No shell escape or external template inputs are needed.\n"
        "% TeX Gyre Pagella is used when available; Latin Modern is the portable fallback.\n"
    )
    return comment + PREAMBLE.replace("%%AUTHOR%%", tex(identity["name"])) + "\n\n".join(body) + "\n", summary


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".public-cv-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def compile_pdf(tex_path: Path, output: Path, engine: str | None) -> str:
    selected = shutil.which(engine) if engine else next(
        (shutil.which(name) for name in ("xelatex", "lualatex", "pdflatex") if shutil.which(name)), None)
    if not selected:
        raise CVBuildError("Install XeLaTeX (TeX Live XeTeX and latex-extra), or use --tex-only.")
    with tempfile.TemporaryDirectory(prefix="public-cv-latex-") as temporary:
        command = [selected, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                   "-file-line-error", "-output-directory=" + temporary, tex_path.name]
        for _ in range(2):
            try:
                completed = subprocess.run(command, cwd=tex_path.parent, capture_output=True,
                                           text=True, encoding="utf-8", errors="replace", timeout=180)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise CVBuildError(f"LaTeX compilation could not finish: {exc}") from exc
            if completed.returncode:
                tail = "\n".join(completed.stdout.splitlines()[-45:])
                raise CVBuildError("LaTeX compilation failed; the previous PDF was retained.\n" + tail)
        log_path = Path(temporary) / (tex_path.stem + ".log")
        log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else completed.stdout
        if "Missing character:" in log:
            raise CVBuildError("The selected TeX font lacks a required character; the previous PDF was retained.")
        overfull = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", log)
        if any(float(width) > 2 for width in overfull):
            raise CVBuildError("LaTeX reported text extending beyond its line width; the previous PDF was retained.")
        result = Path(temporary) / (tex_path.stem + ".pdf")
        if not result.is_file() or result.stat().st_size == 0:
            raise CVBuildError("LaTeX did not produce a PDF.")
        atomic_write(output, result.read_bytes())
    return Path(selected).name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="PDF destination; defaults to the public site CV.")
    parser.add_argument("--tex-output", type=Path, help="TeX destination; defaults beside the PDF.")
    parser.add_argument("--engine", choices=["xelatex", "lualatex", "pdflatex"])
    parser.add_argument("--tex-only", action="store_true", help="Generate the portable TeX source without compiling.")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "assets/files/panagiotis-tsoutsanis-public-cv.pdf").resolve()
    tex_path = (args.tex_output or output.with_suffix(".tex")).resolve()
    if output == tex_path:
        parser.error("The PDF and TeX destinations must be different files.")
    try:
        document, counts = build_tex(root, tex_path)
        atomic_write(tex_path, document.encode("utf-8"))
        engine = None if args.tex_only else compile_pdf(tex_path, output, args.engine)
    except (CVBuildError, OSError) as exc:
        print(f"Public CV build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Created portable LaTeX source: {tex_path}")
    if engine:
        print(f"Compiled PDF with {engine}, shell escape disabled: {output}")
    print("Public content: " + ", ".join(f"{value} {key.replace('_', ' ')}" for key, value in counts.items()) + ".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

