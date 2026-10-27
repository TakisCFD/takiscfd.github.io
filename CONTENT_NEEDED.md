# Remaining details for the website

The unpublished site now includes the supplied public profile, **90 publication/conference records**, **19 people records (5 current and 14 alumni)**, **15 talks with month-precision dates**, **92 anonymous MSc topics**, 41 gallery images/figures and eight animations (six inline MP4s and two external links). The three selected homepage papers remain unchanged. You do not need to supply the original CV or the same lists again.

## GitHub account now provided

The account is **[TakisCFD](https://github.com/TakisCFD)**. The intended personal-site repository is **`TakisCFD/takiscfd.github.io`**, and the future website address is **https://takiscfd.github.io/**. No further username is needed. Repository availability has not been checked, and this work has not created a remote repository or published a website.

The prepared configuration uses `url: "https://takiscfd.github.io"`, an empty `baseurl`, and `github_username: "TakisCFD"`. Publishing remains disabled and `indexable` remains `false`. If the intended repository already exists, review its contents before using it for this site.

## Remaining personal details

**Any preferred display-name change is optional.** The site uses Panagiotis Tsoutsanis with Takis as the familiar name. No change is needed unless you prefer another form.

The institutional profile, ORCID, Google Scholar and UCNS3D links are already included. No GitHub password, access token or recovery code is needed in chat or in the project.

The people-status review is complete: **Aaron Feria Alanis has graduated and is listed as alumni; Yiren Tong remains current**. The owner confirmed these statuses on **27 October 2026**. This is a confirmation date only; no graduation date is assigned.

## Material that would improve the next version

| Section | Useful input |
| --- | --- |
| Gallery and animations | Both batches, comprising 26 stills, nine PDF figures and four animations, are integrated. Scientific captions and creator credits can be refined; additional images can follow. The selected Schardin image is on the home page. Animation records are in `_data/animations.yml`. |
| Publications | Corrections, newer references or a current BibTeX export if it adds information. The import already contains 90 records; three are selected for the homepage. `SOURCE_NOTES.md` identifies remaining metadata questions. |
| People and alumni | Optionally add profile/thesis links, photographs or first destinations. The 19 records now comprise 5 current students and 14 alumni; Aaron's and Yiren's statuses are confirmed. |
| Talks | Slides, recording URLs, event links or exact dates for the 15 existing records. Month-only dates will remain month-only unless you provide an exact day. |
| Public profile | Corrections to the biography, research overview, areas of expertise, education or distinctions in `_data/public_profile.yml`. |
| Research | Corrections to the four themes or additional public research descriptions with relevant papers and images. |
| Teaching | Corrections or additional anonymous MSc topics. The archive uses year, course and topic only; student names stay excluded. |
| News | Any real dated announcements you want highlighted. Regular news updates are optional. |

The path `/Users/takis/Dropbox` is local to your computer and is not accessible from this workspace. **Upload selected media directly, or upload a ZIP** containing the chosen files and captions. A local path alone does not provide the files; an external storage connection is not required.

## Bibliography decisions to review

The collection distinguishes published proceedings from presentations and explicitly marks one withdrawn conference paper. Fourteen presentation citations remain owner-supplied without an independently verified exact source. The main unresolved questions are the author order of the 2015 RANS conference paper, whether two similarly named Cambridge contributions are the same work, and whether a five-author setup/validation presentation corresponds to a different seven-author proceedings record. The records remain separate where a merge would require an assumption.

The withdrawn record retains `status = {withdrawn}` and its withdrawal-notice link. A status is preserved even when a record remains in the archive. No ordinary published status is inferred from inclusion in the bibliography.

## Public CV and content boundaries

The downloadable public CV is generated from the approved website data. Optional regeneration uses `scripts/build_public_cv.py`, the separate `requirements-cv.txt` dependencies and XeLaTeX; instructions are in `README.md` and `EDITING.md`. The generator produces both a PDF and a standalone LaTeX source document. It does not read the original private CV. Articles and conference entries are unnumbered.

Keep the original private CV and extraction/QA files outside the project and package. Public content excludes funded-project descriptions, all monetary values, internal university roles and MSc student names. Names of the authorised research students and alumni remain in the people section.

## Choices for later

- **Address:** the intended address is **https://takiscfd.github.io/**; a personal domain can be added later.
- **Analytics:** leave tracking disabled, or later enable GoatCounter with its public site code.
- **Editing:** use GitHub's browser editor once a repository is set up, or a local editor and Git.
- **Publication:** make a separate decision after reviewing the content and address. The workflow remains build-only while `PUBLISH_SITE` is unset or `false`.

`EDITING.md` contains the actual field names and copyable templates for publications, people, anonymous topics, talks, gallery items and animations.

The account-specific launch sequence is in `README.md`: place the contents of `source/`, including `.github/`, at the repository root on `main`; choose **GitHub Actions** in Pages settings; and, when ready to publish, set the repository Actions variable **`PUBLISH_SITE=true`** and run the workflow with its **`publish`** checkbox selected. These are future setup steps, not actions already performed.

## Research-group leadership wording

The owner asked whether CFD group leadership should be included. The recommended optional sentence is: “I lead the Computational Fluid Dynamics Group at Cranfield University.” The current institutional biography supports this wording. It has not been inserted in the public biography or CV because the earlier instruction excluded university roles; a concise scientific-leadership line is available for the owner's decision. Administrative appointments and committee roles remain excluded.

## Google Scholar comparison

The provided Scholar profile could not be retrieved by the research tool (HTTP 403). A primary-source audit has been carried out using publisher metadata, arXiv and institutional records. It should not be described as a complete comparison against Scholar. A current BibTeX export from the profile would allow the remaining record-by-record comparison without changing access permissions.


## First media batch

The 18 individually uploaded still images, `zoom2.pdf` and `jet_2d_all.mp4` were accessible and integrated. The earlier `Archive.zip` was unavailable and was not read or used. The owner selected `schardin_dg_p3_cw3_4.png` for the home page. All original stills and the uploaded MP4s remain unchanged in the delivered site. PDF previews and video posters were generated, and the OGV and MPG animations have MP4 web copies. The public captions describe visible content and avoid unverified Mach numbers, simulation conditions or performance comparisons. For more specific scientific captions, provide the quantity shown, case name, methods, conditions and creator credit where relevant.

The second batch adds eight still images, eight PDF figures and three animations.
All nine uploaded PDFs are single-page figures with previews and original-file links.
The two legacy video formats (`bestone.ogv` and `CYLINDER_TRANSONIC.mpg`) have H.264
MP4 web copies; their uploaded originals remain unchanged. The chosen Schardin
image remains the home-page research image.
