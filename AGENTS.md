# Website working instructions

## Scope

Maintain Panagiotis (Takis) Tsoutsanis's personal academic website. Keep it private
and available for offline review until the owner explicitly asks to publish it.
Do not push to GitHub, enable Pages deployment, or create public media links as
part of routine editing.

## Source access

The owner's media source is
`/Users/takis/Dropbox/TRANSFER_MATERIAL/videes/` when that folder is available in
a local session. Read and inspect files there only. Never edit, rename, move,
delete or reorganise its contents. Copy selected material into this website's
working directory before making website-specific derivatives. Do not browse
other Dropbox folders. The folder is not accessible in the cloud session that
prepared this package.

The user declined the Dropbox plugin for this task. Use direct file uploads or
approved local folder access instead. A folder path in a prompt does not itself
grant access or create an enforced sandbox boundary.

## Public content

- Keep funded-project descriptions and monetary values out of every deliverable.
- Omit internal university administrative and leadership roles. The professional
  identity Professor of Computational Fluid Dynamics, Cranfield University is
  retained.
- Keep MSc taught-project records anonymous: only `year`, `course` and `topic`.
- Named PhD, EngD, MPhil and MRes research supervisees are allowed. Use explicit
  owner-confirmed status rather than inferring completion from date ranges.
- Never copy or commit the original private CV, its excluded sections, or private
  extraction/review files into this source tree or a downloadable archive.
- Build the public PDF only from the public website data with
  `scripts/build_public_cv.py`.
- Distinguish journal articles, reports, preprints, proceedings and conference
  presentations. Keep verified withdrawal labels visible.
- Display article and conference entries without reference numbering, including
  in the downloadable public CV.
- Preserve source credits and verify publication metadata against primary sources.

## Working files

`README.md`, `EDITING.md`, `CONTENT_NEEDED.md` and `SOURCE_NOTES.md` explain the
build, editable data and remaining review points. The bibliography is in
`_bibliography/papers.bib`; generated publication YAML and BibTeX downloads are
rebuilt by `scripts/import_publications.py`.
