# Editing the website

All paths in this guide are relative to the `source/` folder, which becomes the repository root if you later choose to use GitHub. Make changes here, then rebuild or use the local server described in `README.md`.

## The editing model

The website separates content from presentation:

- **Markdown files** hold research pages, talks, news and surrounding page text. Their opening block between `---` lines contains named settings, called front matter; the text below is the page body.
- **YAML files** hold the public profile, settings and lists, including people, anonymous MSc topics, gallery items and research animations.
- **BibTeX** is the source for publications. A small Python importer creates the data and citation downloads that Jekyll uses.
- **HTML/CSS templates** control the layout. Routine content updates do not require changes to them.

Use spaces, not tabs, for YAML indentation. Quote text that contains punctuation such as a colon. Write `true` and `false` without quotes for boolean settings. Stored dates use `YYYY-MM-DD`; talk `date_precision` controls whether a day, month or year is displayed. Save text as UTF-8. Replace all example wording before adding a template to a live content folder.

### File map

| File or directory | What it controls |
| --- | --- |
| `_config.yml` | Name, role, institution, contact links, portrait, CV, site address, analytics and indexing |
| `index.html` | Homepage headline and introductory text; other sections are assembled from content |
| `_data/public_profile.yml` | Biography, research overview, areas of expertise, education and distinctions |
| `about/index.md` | About-page surrounding text |
| `_bibliography/papers.bib` | Master publication list |
| `_research/*.md` | Individual research themes, their order and related publications |
| `_data/people.yml` | Current researcher and alumni profiles |
| `_data/msc_topics.yml` | Anonymous MSc topic archive: year, course and topic only |
| `_data/gallery.yml` | Gallery items, categories, captions and credits |
| `_data/animations.yml` | Research animation links, captions, awards and credits |
| `_talks/*.md` | Individual talks and their event dates |
| `_news/*.md` | Dated announcements; the homepage shows the three most recent |
| `_data/navigation.yml` | Menu labels and destination paths |
| `assets/images/` | Portraits and scientific images |
| `assets/files/` | CV, slides and other files you choose to offer |
| `examples/` | Copyable templates; these are excluded from the built website |
| `SOURCE_NOTES.md` | Public-safe source register and unresolved bibliographic review items |
| `scripts/build_public_cv.py`, `requirements-cv.txt` | Automatic public-CV regeneration in GitHub builds; optional local rebuilding |
| `_layouts/`, `_includes/`, `assets/css/site.css`, `assets/js/site.js` | Presentation and interactive behaviour |

`_data/publications.yml`, `assets/bibtex/` and `_site/` are generated output. Edit the source files above rather than changing that output directly. The supplied `.gitignore` keeps generated publication files and build output out of version control; the workflow recreates them.

## Name, biography, portrait and CV

Update the appropriate fields in `_config.yml`. For example, after adding real files:

```yaml
profile:
  name: "Panagiotis Tsoutsanis"
  familiar_name: "Takis"
  role: "Professor of Computational Fluid Dynamics"
  institution: "Cranfield University"
  email: "panagiotis.tsoutsanis@cranfield.ac.uk"
  portrait: "/assets/images/portrait.jpg"
  cv: "/assets/files/panagiotis-tsoutsanis-public-cv.pdf"
```

Keep the existing institutional, ORCID and Scholar fields in that same `profile` block. Do not replace the whole block with this shortened example. Leave `portrait` or `cv` as `""` until the corresponding file is present; their links or image are then omitted.

If the preferred display name changes, update both `title` and `profile.name` in `_config.yml`, and review `_data/public_profile.yml`. The homepage introduction is in `index.html`. The site-wide header and footer read the name from configuration.

The main biography, research overview, expertise list, education and distinctions are maintained in `_data/public_profile.yml`. Edit its existing fields instead of maintaining a second biography in the original private CV. The public CV generator reads this same public data, alongside publications, people, talks and the anonymous MSc topics. Every standard GitHub Actions build regenerates the public PDF after importing the bibliography and validating content, before building the website. Future data edits therefore update the PDF automatically in that build.

Local regeneration is optional when you are only reviewing the prebuilt package. To regenerate the public PDF on your computer:

```bash
python -m pip install -r requirements.txt -r requirements-cv.txt
python scripts/import_publications.py
python scripts/build_public_cv.py
```

Install XeLaTeX and the packages listed in `README.md` to compile the CV locally. The generator writes both `assets/files/panagiotis-tsoutsanis-public-cv.pdf` and its `.tex` source, using TeX Gyre Pagella or Latin Modern Roman. A standalone copy needs the `.tex` file and the supplied portrait named `portrait.png` beside it. Run `xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error panagiotis-tsoutsanis-public-cv.tex` twice in that folder.

The `research_overview` field contains a list of paragraphs. Each `expertise` entry has `name` and `description` fields. These feed both the research page and the public CV. Edit them in `_data/public_profile.yml` so both outputs stay aligned. Article and conference entries remain unnumbered; years and page numbers are retained.

GitHub's Ubuntu build installs the Python requirements and XeLaTeX dependencies automatically. No local installation is needed for routine edits made through GitHub's browser editor. The generated PDF is included in the build without committing it back to the repository.
Keep the original private CV and extraction/QA documents outside the repository and package. Approved public data omits funded-project descriptions, monetary values, internal university roles and MSc student names.

## Publications: one source of truth

Add or update entries in `_bibliography/papers.bib`. A UTF-8 BibTeX export from your reference manager can be used as the starting point. Each entry needs a unique citation key and nonempty `title`, `author` and four-digit `year` fields. Authors use BibTeX's `and` separator.

The current collection contains **90 records**: 38 journal articles, 24 proceedings records including one marked withdrawn, 21 conference presentations, five reports and two preprints. All 44 source conference contributions and one added proceedings citation carry `conference = {true}`, giving 45 conference records. Here is an existing selected entry, shortened to its display and website fields:

```bibtex
@article{tsoutsanis2025adda,
  author   = {Tsoutsanis, Panagiotis and Nogueira, Xesus},
  title    = {Arbitrary-order unstructured finite-volume methods for implicit large eddy simulation of turbulent flows with adaptive dissipation/dispersion adjustment ({ADDA})},
  journal  = {Journal of Computational Physics},
  year     = {2025},
  doi      = {10.1016/j.jcp.2024.113653},
  keywords = {High-order methods, Turbulence},
  selected = {true}
}
```

The supplied bibliography already contains this entry; edit it rather than appending a duplicate.

| Field | Website behaviour |
| --- | --- |
| `selected = {true}` | Makes a paper eligible for the homepage's three selected-publication positions |
| BibTeX entry type | `@article` becomes journal, `@inproceedings` becomes conference, and `@techreport` becomes report; arXiv preprints are classified separately |
| `entrysubtype = {conference presentation}` | Marks an `@misc` entry as a presentation without claiming a published proceedings paper |
| `conference = {true}` | Includes a record in the conference archive while preserving its bibliographic type |
| `status = {withdrawn}` or `{retracted}` | Displays an explicit status badge; omit the field for ordinary records |
| `eventyear` | Records a verified event year separately from the publication citation year |
| `keywords` | Adds topic tags and filter options; separate topics with commas or semicolons |
| `doi` | Adds a DOI link; accepts a bare DOI or a `https://doi.org/…` URL |
| `html` or `url` | Links the publication title; `html` takes priority |
| `pdf` | Adds a PDF link, such as a repository URL or `/assets/files/papers/paper.pdf` |
| `code` | Adds a research-code link |
| `eprint` with `archivePrefix = {arXiv}` | Adds a separate preprint link; journal records remain classified as journal articles |
| `journal`, `booktitle`, `howpublished`, `school`, `institution` or `publisher` | Supplies the venue, according to entry type and available fields |

Keep topic wording consistent: `High-order methods` and `High order methods` would appear as separate filter choices. Papers are displayed by descending year, then title; the homepage takes the first three entries marked as selected. A paper with a journal venue remains a journal paper when an arXiv identifier is also present.

After editing, run:

```bash
python scripts/import_publications.py
```

This generates `_data/publications.yml`, one BibTeX download per entry in `assets/bibtex/`, and `assets/bibtex/publications.bib`. The full download preserves the source bibliography bytes; display text is decoded for the web. The importer validates the complete input before replacing output, so malformed entries, duplicate keys or missing required fields produce an error instead of silently dropping papers. It does not retrieve missing metadata from the internet.

Keep citation keys stable: `_research/*.md` uses them in `publication_ids`. If you rename a key, update those references too. The three selected homepage keys remain `tsoutsanis2026exascale`, `tsoutsanis2025adda` and `antoniadis2022ucns3d`; the complete collection now contains 90 records. The source register documents 14 owner-supplied presentations without an independently verified exact record and the remaining author-order or possible-duplicate questions. Update a citation when evidence resolves an issue, then update its source note. Do not transfer a DOI to a similar title without confirming that it is the same work.

## Research themes

Copy an existing file in `_research/`, using a descriptive filename such as `new-theme.md`. Its filename determines the address `/research/new-theme/`.

```markdown
---
title: "Your research theme"
short_title: "Short menu title"
order: 5
summary: "One sentence for the homepage card."
description: "A short introduction for the research listing and detail page."
publication_ids:
  - tsoutsanis2025adda
  - antoniadis2022ucns3d
---
## Research focus

Write the page in normal Markdown. Explain the question, the methods and why
it matters. Replace the example citation keys with the papers relevant here.
```

`order` controls the position of research cards. Use `publication_ids: []` when there are no related publications yet. The four starter research descriptions can be revised without changing their filenames or addresses.

## Current researchers and alumni

The file `_data/people.yml` contains **19 records: 5 current research students and 14 alumni**. Edit the existing person instead of adding a duplicate. The owner confirmed on **27 October 2026** that **Aaron Feria Alanis has graduated and is an alumnus**, while **Yiren Tong remains current**. That date records the confirmation, not a graduation date. Keep a person's supplied research period separate from any exact graduation date, and do not infer completion from a listed end year alone. A completed record follows this schema:

```yaml
- name: "Actual full name"
  role: "PhD researcher"
  status: "alumni"
  years: "2021–2025"
  research_topic: "One sentence about the person's research."
  profile_url: ""
  photo: ""
  thesis_url: ""
  first_destination: ""
```

Use `status: "current"` for current researchers and `status: "alumni"` for former members. Required fields are `name`, `role`, `status` and `research_topic`. The `years` field is display text; it can say `2024–present` when accurate.

Optional `profile_url` and `thesis_url` accept full HTTP(S) links. For a photograph, place the file in `assets/images/people/` and set `photo` to a path such as `/assets/images/people/person-name.jpg`. For alumni, `first_destination` records the role and organisation after leaving, when known. Records appear in file order within their section. Use `[]` again if the list is empty.

## Anonymous MSc topics

The teaching archive in `_data/msc_topics.yml` contains **92 anonymous topics**. Each record has exactly three fields:

```yaml
- year: "2025-26"
  course: "MSc in CFD"
  topic: "Actual research topic"
```

Add only the year, course and topic. The validator rejects additional fields in this archive, including names. The named people collection is reserved for the authorised research-student and alumni records.

## Talks

There are **15 existing talk records** in `_talks/`. They use month precision because their source dates did not establish an exact day. Edit an existing record to add slides or recordings; for a new talk, copy `examples/talk.md` into `_talks/` with a descriptive filename.

```markdown
---
title: "Actual presentation title"
event: "Actual event or host institution"
event_date: "2027-01-01"
date_precision: month
talk_type: "Invited seminar"
location: ""
summary: "One or two sentences describing the presentation."
slides_url: ""
recording_url: ""
event_url: ""
---
Write a short abstract here, and add any useful links to related work.
```

The example date and text must be replaced. Use **`event_date`**, not `date`, for the talk date. Set `date_precision: day` only when the exact day is known, `month` when only the month/year is known, or `year` when that is all the source establishes. For month-only dates, the stored first day is a sorting convention and is not shown as a real event day. Future events can be listed before they happen. Talks appear in descending event-date order and each receives its own page.

`slides_url` can be a full external URL or, after adding the PDF, a local path such as `/assets/files/talks/your-talk.pdf`. `recording_url` can link to a recording hosted elsewhere. Keep either field empty when the material is unavailable. The links appear automatically when values are supplied.

## Gallery images

Place an image in `assets/images/`, then append a record to `_data/gallery.yml`. Copy `examples/gallery-item.yml` or use this schema:

```yaml
- id: "your-image-name"
  title: "Actual image title"
  category: "Flow visualisations"
  image: "/assets/images/your-image.png"
  alt: "A short description of the visual information in the image."
  caption: "What it shows, with verified conditions or methods if useful."
  credit: "Actual creator or team credit"
  source_url: ""
  project_path: "/research/high-order-methods/"
```

The current gallery contains 41 images/figures. Every `id` must be unique and use lowercase letters, digits and hyphens. The image file must exist at the stated path. Required text includes `title`, `category`, `alt`, `caption` and `credit`. Categories automatically become filter buttons.

`alt` describes the image for someone who cannot see it; `caption` explains its scientific context. `source_url` is an optional link to the original image. `project_path` is an optional path to a related research page. Set either optional field to `""` when unused. Preserve creator credits and use captions you can substantiate.

An optional `original_url` can link a rendered figure to its original PDF, for example `/assets/files/research/zoom2.pdf`. Optional `width` and `height` record pixel dimensions. The original UCNS3D images retain their source credits. You can revise captions, replace images or add selected scientific images. Upload additional files individually or in a ZIP, with captions and creator credits where available. A local folder path such as `/Users/takis/Dropbox` does not transfer media into this workspace.

## Research animations

Eight research animations are listed in `_data/animations.yml`: six local MP4s with browser controls and two links to externally hosted award videos. The records preserve their research context and source credits. Add an external animation using these fields:

```yaml
- id: your-animation
  title: "Actual animation title"
  year: 2026
  caption: "What the animation shows."
  award: ""
  url: "https://example.org/your-video"
  source_url: ""
  credit: "Actual creator or team"
  research_path: "/research/high-order-methods/"
```

Replace the example URL and wording. `id`, `title`, `caption`, `url` and `credit` are required. Keep `award` empty unless an award is verified. For a local MP4, set `type: video`, set `url` to the path under `assets/videos/`, and provide a local `poster` image plus `width` and `height`. The existing `jet-comparison` record is a complete example. The player uses native browser controls and starts only when the visitor chooses to play. The offline preview includes the video and poster; no external video account is required. Keep individual media files suitable for the eventual GitHub repository.

## News and internal links

Copy `examples/news.md` to `_news/YYYY-MM-DD-short-title.md`, with a real date and announcement:

```markdown
---
title: "Actual announcement title"
date: 2026-10-27
summary: "One sentence for the homepage."
---
Add the announcement, including links to the relevant paper, project or event.
```

The homepage shows the latest three announcements. There is no need to maintain a regular posting schedule.

For links inside Markdown, use Jekyll's `relative_url` filter so the same page works as either a user site or a project site:

```markdown
[High-order methods]({{ '/research/high-order-methods/' | relative_url }})
```

In the YAML fields described above, use the plain site path, such as `/assets/images/portrait.jpg`; the templates handle the site prefix. Use complete `https://…` addresses for external pages.

## A short check after an update

From the source root, with your Python environment active:

```bash
python scripts/import_publications.py
python scripts/validate_content.py
bundle exec jekyll build --strict_front_matter
python scripts/check_site.py _site
```

Then inspect the changed page in your local preview. If an error names a record or citation key, correct that source record and rerun the commands. Typical fixes are YAML indentation, a missing file, an invalid date or a duplicated citation key. These commands build and check locally; they do not publish anything.

### Routine edits in GitHub, once a repository is set up

You can update the website entirely through GitHub's browser interface, without installing Ruby or Python:

1. Open the source file from the table at the top of this guide, choose Edit, and change its content.
2. For a new talk or news item, create a file using the complete path, such as `_talks/seminar-title.md`, then paste and complete the relevant template. Upload new images or PDFs into their asset folders before linking to them.
3. Commit the change with a short description, such as “Add seminar slides”.
4. Review the resulting Actions run. It imports the bibliography, validates content, regenerates the public CV, and runs the tests and website build checks automatically.

These are the same source files used by a local editor. While `PUBLISH_SITE` is unset or `false`, the workflow only checks the update. Once publication is deliberately enabled later, pushes to `main` also update the public website. The deployment switch and optional analytics settings are explained in `README.md`.
