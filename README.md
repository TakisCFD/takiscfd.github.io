# Personal academic website

A working personal website for Panagiotis (Takis) Tsoutsanis, with research, publications, conference contributions, people and alumni, an image and animation gallery, talks, teaching, news, and contact information. It is a lightweight custom Jekyll site following the proposed design. It does not require al-folio or a database.

**This is an unpublished starter.** No personal GitHub repository or hosting account has been connected. The supplied GitHub workflow checks the site but keeps deployment disabled until a separate, deliberate publication decision.

## See the website first

The download contains two folders:

| Folder | Purpose |
| --- | --- |
| `preview/` | A built copy for reviewing the design. Open `preview/index.html` in a browser; its internal links work without installing anything. |
| `source/` | The editable Jekyll project. This README belongs in this folder. |

Extract the ZIP before opening the preview. The preview is a snapshot: editing `source/` does not automatically change `preview/`. Use the local preview instructions below when working on the source. External links to papers and other websites need an internet connection.

## What is already prepared

- A responsive homepage with classic serif headings, your selected Schardin visualisation, a shared research overview, six areas of expertise and four detailed research themes.
- A collection of **90 publication and conference records**, with search and type, year and topic filters, three selected homepage papers, and individual and complete BibTeX downloads.
- A dedicated conference archive covering **45 records**: 44 from the supplied list and one additional verified proceedings citation.
- **19 people records**: 5 current research students and 14 alumni.
- A gallery of **41 images/figures**, including 30 uploaded stills, nine rendered PDF figures and two retained UCNS3D images, with category filters and enlargement. Eight animations include six playable local MP4s and two linked award videos.
- **15 talk records**, displayed with month precision where an exact day was not supplied, with links for available recordings and room to add slides.
- Teaching content and **92 anonymous MSc research topics**, without student names.
- A public profile and education/recognition data, and a public CV built from the same approved website content.
- Existing institutional, ORCID, Google Scholar and UCNS3D links.
- Optional GoatCounter integration, disabled in this starter and in development previews.

The bibliography combines all 82 uncommented journal/conference citations from the supplied list, the retained GPU preprint, one independently verified newer 2026 journal paper, and six further verified citations found in the primary-source audit. These additions comprise one journal article, one preprint, one proceedings paper and three technical reports. Google Scholar returned an access error, so this is not a complete comparison against the Scholar profile. It distinguishes journal articles, proceedings, presentations, reports and preprints; one withdrawn conference paper is visibly marked. Fourteen presentation citations remain owner-supplied without an exact independently verified primary-source record. This is a reconciled collection of the supplied material, not a claim of a complete career bibliography. Corrections, source links and remaining metadata questions are recorded in `SOURCE_NOTES.md`.

The original private CV and extraction/QA files are excluded from this project and its download package. Public content omits funded-project descriptions, monetary values, internal university roles and MSc student names. The new research-media collection uses the supplied Schardin image on the home page. The 30 uploaded stills, nine original PDF figures and two uploaded MP4s are copied unchanged. Each PDF has a rendered preview and an original-file link. Three older-format videos and the larger aircraft MP4 have browser-compatible MP4 derivatives; their uploaded originals remain unchanged. The two original UCNS3D images retain their team credits.

## GitHub account and remaining details

The supplied GitHub account is **[TakisCFD](https://github.com/TakisCFD)**. The intended personal-site repository is **`TakisCFD/takiscfd.github.io`**, with the future website at **https://takiscfd.github.io/**. Repository availability has not been checked, and this work has not created a remote repository or published a website. If that repository already exists, review its current contents before using it for this site.

No further GitHub username is needed. The site uses Panagiotis Tsoutsanis with Takis as the familiar name; provide a display-name change only if you prefer another form.

The owner confirmed on **27 October 2026** that **Aaron Feria Alanis has graduated and belongs in alumni**, while **Yiren Tong remains a current student**. This is the status-confirmation date; no graduation date is assigned. The profile, publications, people, talks and MSc topics have already been incorporated. New or corrected references, alumni destinations, talk slides and selected media can follow in any convenient format. See `CONTENT_NEEDED.md` for the remaining checklist.

Upload selected images/videos directly, or upload a ZIP containing the files and any captions. The local path `/Users/takis/Dropbox` is not accessible from this workspace; supplying a folder path alone does not transfer its files.

No GitHub password, access token, recovery code or analytics password belongs in these files or in chat.

## Run an editable preview on your computer

Local setup is optional. Opening the supplied offline preview and, later, making routine edits in GitHub’s browser editor do not require Ruby or Python on your computer. Install the tools below only if you want to build or preview source changes locally.

### Requirements

- Ruby **3.3**, with Bundler. The supplied `Gemfile.lock` was generated using Bundler **2.5.22**.
- Python **3.10 or newer**. The GitHub workflow uses Python 3.12.
- An editor of your choice. Git is useful for later version history and GitHub updates.

Use a user-managed Ruby installation with the build tools required by your operating system. Jekyll's [installation guide](https://jekyllrb.com/docs/installation/) provides operating-system instructions. The two Python dependencies are pinned in `requirements.txt`; Jekyll and WEBrick are declared in `Gemfile`.

The commands below assume a macOS/Linux terminal or WSL, starting in the extracted download:

```bash
cd source
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bundle install
python scripts/import_publications.py
python scripts/validate_content.py
bundle exec jekyll serve --host 127.0.0.1
```

If `bundle` is unavailable, install the matching Bundler into your Ruby installation with `gem install bundler -v 2.5.22`, then repeat `bundle install`. In Windows PowerShell, use `py -m venv .venv` and `.venv\Scripts\Activate.ps1` for the environment steps.

Open **http://127.0.0.1:4000/**. The server is available on your computer only. Press **Ctrl+C** to stop it. If you later set a project `baseurl`, open the corresponding path, for example `http://127.0.0.1:4000/personal-website/`.

Jekyll watches normal content edits while the server runs. After changing `_bibliography/papers.bib`, rerun `python scripts/import_publications.py` in a second terminal with the Python environment activated. After changing `_config.yml`, restart Jekyll.

### Build and check without running a server

Run these from `source/`:

```bash
python scripts/import_publications.py
python scripts/validate_content.py
bundle exec jekyll build --strict_front_matter
python scripts/check_site.py _site
```

The resulting website is in `_site/`. The checks validate editable records, generated pages, local links, images and page anchors. They do not verify the availability of external websites or the scientific accuracy of content. The packaged `preview/` has already been adjusted for opening as local files; ordinary Jekyll `_site/` output is best viewed through the local server.

### Export a fresh offline preview

After importing and checking the content, you can create another copy that opens directly from your computer:

```bash
JEKYLL_ENV=development bundle exec jekyll build --strict_front_matter
python scripts/export_preview.py --destination ../preview-new
```

Open `../preview-new/index.html`. Choose a new destination each time, outside `_site/`; the exporter refuses to overwrite an existing preview. It converts internal links to relative file links and rejects builds containing the analytics loader.

### Rebuild the public CV locally — optional

The public CV is generated from `_data/public_profile.yml`, the people and anonymous MSc-topic data, the imported bibliography, talk records and public configuration. The generator never reads the original private CV. **Every standard GitHub Actions build regenerates the PDF after publication import and content validation, before Jekyll builds the site.** Changes to those data files therefore update the PDF in that build automatically.

Opening the prebuilt preview or PDF requires no local Python packages or fonts. Install the separate CV dependencies only if you want to regenerate the PDF on your own computer:

```bash
python -m pip install -r requirements.txt -r requirements-cv.txt
python scripts/import_publications.py
python scripts/build_public_cv.py
```

This produces `assets/files/panagiotis-tsoutsanis-public-cv.pdf` and the editable, self-contained LaTeX document `assets/files/panagiotis-tsoutsanis-public-cv.tex`. The CV uses academic serif typography, a portrait, a research overview, areas of expertise, running headers and page numbers. Article and conference entries are unnumbered.

To compile it, install a TeX distribution providing **XeLaTeX** and the standard LaTeX layout packages. On Ubuntu, the same packages used by the workflow are `texlive-xetex`, `texlive-latex-extra` and `fonts-texgyre`. A full MacTeX installation is another option on macOS. The document prefers TeX Gyre Pagella when available and falls back to Latin Modern Roman. There is no custom font-directory argument.

The separate LaTeX source ZIP contains the generated `.tex`, an unchanged copy of the supplied portrait as `portrait.png`, and compile instructions. It can be edited independently, or regenerated from the website's public data. If you edit the generated `.tex` directly, keep that copy separately: running the generator will replace it. For durable updates across both website and CV, edit the public data files instead.

For local work, run the generator and rebuild the website when you want the PDF to reflect your edits. The GitHub workflow installs the Python dependencies and Ubuntu packages `texlive-xetex`, `texlive-latex-extra` and `fonts-texgyre`, regenerates the PDF and includes it in the website build. It does not commit generated files back to the repository. Builds remain unpublished while `PUBLISH_SITE` is unset or `false`.

## Keep updates simple

Most updates involve one content file and, sometimes, an image or PDF. Use `EDITING.md` for the exact fields and examples.

| Change | Edit |
| --- | --- |
| Identity, email, portrait, CV and professional links | `_config.yml` |
| Introductory homepage wording | `index.html` |
| Biography, research overview, areas of expertise, education and distinctions | `_data/public_profile.yml` |
| About-page surrounding text | `about/index.md` |
| Publications | `_bibliography/papers.bib` |
| Research pages | `_research/*.md` |
| Current researchers and alumni | `_data/people.yml` |
| Anonymous MSc topic archive | `_data/msc_topics.yml` |
| Gallery records | `_data/gallery.yml` |
| Research animation links, captions and credits | `_data/animations.yml` |
| Talks | `_talks/*.md` |
| News | `_news/*.md` |
| Images and PDFs | `assets/images/` and `assets/files/` |

Edit the source bibliography, not `_data/publications.yml` or `assets/bibtex/`: those are generated by the importer. Keep publication citation keys stable because research pages use them to select related papers. BibTeX entry types determine the displayed category; `entrysubtype` distinguishes conference presentations, `conference = {true}` includes a record in the conference archive, and `status = {withdrawn}` or `{retracted}` displays the relevant status. Use `eventyear` when the verified conference year differs from the publication citation year.

When this project is eventually placed in GitHub, the files from `source/` should be at the repository root. **The simplest routine editing route is GitHub's browser editor:** open the content file, choose Edit, make the change, and commit it with a short description. Upload an image or PDF first when the content links to a new file. No local Ruby or Python installation is needed for this workflow.

The included Actions workflow runs the importer, publication-import tests and site checks, and regenerates the public CV automatically on pushes and pull requests to `main`. The PDF is regenerated from the imported publication data and other public content before Jekyll builds the website. Its Actions run shows whether an update passed. With publication disabled, a successful run checks the update without putting it online. A local editor and Git remain available as an alternative.

## How publication is kept disabled

The workflow is `.github/workflows/pages.yml`. With repository variable `PUBLISH_SITE` absent or set to `false`, it builds a development version, checks it, and performs no Pages upload or deployment. It also checks that the preview output contains no analytics loader. Pull requests never deploy.

The account-specific configuration is:

```yaml
url: "https://takiscfd.github.io"
baseurl: ""
github_username: "TakisCFD"
indexable: false
analytics:
  enabled: false
  goatcounter_code: ""
```

`indexable: false` asks search engines not to index the site. It is not an access-control setting; keeping deployment disabled is what preserves the current unpublished state.

### Launch for TakisCFD — when ready

No publication step is needed to review or edit this starter. When you decide to launch at **https://takiscfd.github.io/**:

1. Create or choose the repository **`TakisCFD/takiscfd.github.io`**, with **`main`** as its default branch. On GitHub Free, the source repository must be public to use Pages; see [GitHub's plan requirements](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages). If the repository already exists, review its contents before replacing files.
2. Put the **contents of `source/` at the repository root**, including the **`.github/` folder** and `.github/workflows/pages.yml`. `_config.yml`, `Gemfile`, `README.md` and the asset folders should appear at the root. Do not upload the enclosing `source/` folder, the `preview/` folder or the download ZIP as the website source. Leave `PUBLISH_SITE` unset while the first build checks the upload.
3. In the repository, select **Settings → Pages → Build and deployment → Source → GitHub Actions**. The supplied workflow performs the Jekyll build and content checks. Keep `url: "https://takiscfd.github.io"` and `baseurl: ""`. Set `indexable: true` only when search-engine indexing is wanted; it remains `false` in this unpublished package.
4. After reviewing the content and a successful build, open **Settings → Secrets and variables → Actions → Variables → New repository variable**. Add **`PUBLISH_SITE`** with the value **`true`**. Setting the variable does not itself start a run.
5. Open **Actions → Build and optionally publish personal website → Run workflow**. Select **`main`**, tick the **`publish`** checkbox (labelled “Publish this build (also requires PUBLISH_SITE=true)”), and run the workflow. A successful checked deployment will make the site available at the intended address.

Once `PUBLISH_SITE` is `true`, future pushes to `main` also publish checked production builds. A manual run publishes only when its `publish` checkbox is selected; pull requests never deploy. During publication, the workflow reads GitHub Pages metadata and applies the actual origin and base path. A custom domain can be configured later.

Leaving the variable unset or `false` preserves build-only behaviour. Turning it off after an eventual launch stops future deployments; it does not remove an already published website.

## Optional visitor analytics

No analytics account has been connected. If you later choose GoatCounter, its public site code is the only value needed in the website. For an account address such as `https://my-research-site.goatcounter.com`, the configuration would be:

```yaml
analytics:
  enabled: true
  goatcounter_code: "my-research-site"
```

Use the code alone, not a URL, password or API token. The implementation in `_includes/analytics.html` only loads the script for a **production build**, with analytics enabled and a valid code, when the browser is using HTTPS on exactly the origin configured in `url`. That keeps the supplied offline preview and normal localhost development previews out of visitor counts. The public privacy page adjusts to the configured analytics state.

The site labels selected links for click measurement, including papers, PDFs, slides, recordings, BibTeX and UCNS3D. Such counts indicate visits or clicks; they do not establish that a paper was read or a file download completed. Review the relevant [GoatCounter setup guidance](https://www.goatcounter.com/help/start) when choosing the service.

GitHub's **Insights → Traffic** reports activity on the code repository, including repository visitors and clones. It is separate from visitor analytics for the academic website; see [GitHub's repository traffic documentation](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository).


## Media size and GitHub Pages limits

Measured on 27 October 2026, the complete built website is approximately **199 MB**
(189 MiB), including 41 gallery images/figures and six local MP4 animations.
The six clips total approximately **39.9 MB**. The largest individual asset is
`assets/files/research/crm-nice-q2.pdf`, approximately **24.9 MB (23.7 MiB)**.
Every current website asset is below the 25 MiB browser-upload threshold.
The download bundle is larger than the published site because it includes both
editable source and a complete offline preview; upload only the source folder
when setting up the repository, not the full ZIP or duplicate preview folder.

GitHub currently specifies a **1 GB maximum published Pages site**, a **soft
100 GB monthly bandwidth limit**, and a **10-minute deployment timeout**.
The ordinary soft limit of 10 builds per hour does not apply to a custom
GitHub Actions build-and-publish workflow such as the supplied workflow.
These are distinct from Git repository limits: GitHub warns about files above
50 MiB, blocks files above 100 MiB, and permits browser uploads up to 25 MiB
per file. It recommends keeping source repositories ideally below 1 GB.

For future media, retain original research masters separately and use compressed
MP4 copies on the website. Aim below 25 MiB per clip for easy browser uploads.
Keep large recordings in an appropriate external video or institutional service
and link to them when publication is authorised. Git LFS is not supported by
GitHub Pages. Replacing large binaries repeatedly also grows repository history,
so the repository should not become the archive for every intermediate render.

Official references, checked on 27 October 2026:

- [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [Large files and repository-size guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
- [Git LFS and its Pages limitation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)

The local preview remains unpublished, with visitor analytics disabled.
