TakisCFD website update

Copy EVERYTHING inside this folder into the root of your local takiscfd.github.io repository, replacing files when asked.
Important: show hidden files in Finder (Command+Shift+.) so .github and .gitignore are copied.
Do NOT replace or delete the repository's .git folder.

This update:
- tracks a 90-record _data/publications.yml fallback
- keeps BibTeX regeneration in GitHub Actions
- fails the Pages build if publication data or rendered publication cards are missing
- makes Pages builds fast by removing CV/TeX installation
- adds a separate manual CV workflow with texlive-fonts-recommended
- removes Panagiotis Tsoutsanis self-credit text from gallery images/videos
