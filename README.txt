TakisCFD website update v2 — corrected

This package fixes the failed validation shown on GitHub Actions:
- restores the COMPLETE _data folder, including people.yml, navigation.yml, msc_topics.yml and public_profile.yml;
- keeps the 90-record publications.yml fallback;
- removes Panagiotis Tsoutsanis self-credit fields from gallery images/videos;
- makes gallery/video credit optional in scripts/validate_content.py;
- renders credit text only when a real credit exists;
- retains the fast Pages workflow and separate CV workflow.

Copy EVERYTHING inside this folder into the root of your local takiscfd.github.io repository. Do not touch .git.
Because this package contains the complete _data folder, choosing Replace for _data is safe this time.
Commit and Push origin in GitHub Desktop.
