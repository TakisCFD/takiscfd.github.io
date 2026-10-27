"""Meaningful end-to-end importer checks; run with Python's unittest module."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_publications.py"
spec = importlib.util.spec_from_file_location("publication_importer", SCRIPT)
importer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = importer
spec.loader.exec_module(importer)


class ImporterTests(unittest.TestCase):
    def invoke(self, source: Path, output: Path, bibtex: Path) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), "--source", str(source), "--output", str(output), "--bibtex-dir", str(bibtex)], text=True, capture_output=True)

    def test_real_three_entries_and_exact_downloads(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = ROOT / "tests" / "fixtures" / "three-publications.bib"
            output, bibtex = directory / "data/publications.yml", directory / "downloads"
            result = self.invoke(source, output, bibtex)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = yaml.safe_load(output.read_text())
            self.assertEqual([row["year"] for row in rows], [2026, 2025, 2022])
            self.assertEqual([row["type"] for row in rows], ["preprint", "journal", "journal"])
            self.assertEqual(rows[1]["doi_url"], "https://doi.org/10.1016/j.jcp.2024.113653")
            self.assertIn("Xesús Nogueira", rows[2]["authors"])
            self.assertTrue(all(row["selected"] for row in rows))
            self.assertEqual((bibtex / "publications.bib").read_bytes(), source.read_bytes())
            blocks, _ = importer.raw_entries(source.read_text())
            for block in blocks:
                self.assertEqual((bibtex / (importer.safe_key(block.key) + ".bib")).read_text(), block.text)
            before = output.read_bytes()
            self.assertEqual(self.invoke(source, output, bibtex).returncode, 0)
            self.assertEqual(output.read_bytes(), before)

    def test_accents_groups_corporate_authors_and_string_macros(self):
        citation = r'''@string{venue = "Journal of Numerical Methods"}
@article{accent:2024,
  author = {Nogueira, Xes{\'{u}}s and Müller, Jörg and {Research and Development Group}},
  title = {A {CFD} study of {\"o}scillations and {NASA} flows},
  journal = venue,
  year = {2024},
  keywords = {Methods; Turbulence, Methods},
  selected = {false},
  pdf = {/assets/files/study.pdf}
}'''
        rows, downloads = importer.prepare_import(citation.encode(), "/assets/bibtex")
        self.assertEqual(rows[0]["title"], "A CFD study of öscillations and NASA flows")
        self.assertEqual(rows[0]["authors"], "Xesús Nogueira, Jörg Müller, and Research and Development Group")
        self.assertEqual(rows[0]["venue"], "Journal of Numerical Methods")
        self.assertEqual(rows[0]["topics"], ["Methods", "Turbulence"])
        self.assertEqual(rows[0]["bibtex_url"], "/assets/bibtex/accent-2024.bib")
        self.assertIn(r"Xes{\'{u}}s", downloads["accent-2024.bib"].decode())
        self.assertIn('@string{venue = "Journal of Numerical Methods"}', downloads["accent-2024.bib"].decode())
        self.assertEqual(downloads["publications.bib"], citation.encode())

    def test_invalid_input_does_not_touch_existing_outputs(self):
        valid = '@article{same,title={A paper},author={Doe, Jane},year={2024}}\n'
        cases = {
            "duplicate": valid + valid,
            "invalid year": valid.replace("{2024}", "{forthcoming}"),
            "missing title": '@article{missing,author={Doe, Jane},year={2024}}',
            "unsafe URL": valid.replace("year={2024}", "year={2024},url={javascript:alert(1)}"),
            "unterminated": valid.rstrip()[:-1],
            "silently malformed": valid + '@article{bad,title=,author={Doe, Jane},year={2024}}',
        }
        for name, content in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                source, output, bibtex = directory / "input.bib", directory / "data.yml", directory / "bibtex"
                source.write_text(content)
                output.write_bytes(b"KEEP ORIGINAL YAML\n")
                bibtex.mkdir()
                (bibtex / "publications.bib").write_bytes(b"KEEP ORIGINAL BIB\n")
                before = {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("*") if path.is_file() and path != source}
                result = self.invoke(source, output, bibtex)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("Publication import failed:", result.stderr)
                after = {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("*") if path.is_file() and path != source}
                self.assertEqual(after, before)

    def test_no_outputs_created_for_invalid_new_collection(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "input.bib"
            source.write_text('@article{broken,title={No year},author={Doe, Jane}}')
            output, bibtex = directory / "data/publications.yml", directory / "assets/bibtex"
            self.assertEqual(self.invoke(source, output, bibtex).returncode, 2)
            self.assertFalse(output.parent.exists())
            self.assertFalse(bibtex.exists())

    def test_download_directory_cannot_overwrite_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "original.bib"
            original = b"% This source comment must survive.\n@article{original,author={Doe, Jane},title={A paper},year={2024}}\n"
            source.write_bytes(original)
            output = directory / "data/publications.yml"
            result = self.invoke(source, output, directory)
            self.assertEqual(result.returncode, 2)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse(output.parent.exists())

    def test_link_precedence_local_files_and_published_arxiv(self):
        citation = '''@article{links, author={Doe, Jane},title={A paper},year={2023},
        journal={A Journal}, eprint={2301.12345},archivePrefix={arXiv},
        html={https://example.org/paper},url={https://example.org/other},
        pdf={/assets/files/paper.pdf},code={https://github.com/example/code},doi={10.1234/example}}
        @misc{arxiv,author={Doe, Jane},title={B paper},year={2023},eprint={2301.54321},archivePrefix={arXiv}}'''
        rows, _ = importer.prepare_import(citation.encode(), "/assets/bibtex")
        self.assertEqual(rows[0]["url"], "https://example.org/paper")
        self.assertEqual(rows[0]["type"], "journal")
        self.assertEqual(rows[0]["preprint_url"], "https://arxiv.org/abs/2301.12345")
        self.assertEqual(rows[1]["url"], "https://arxiv.org/abs/2301.54321")
        self.assertEqual(rows[1]["type"], "preprint")
        self.assertEqual(rows[1]["preprint_url"], "https://arxiv.org/abs/2301.54321")

    def test_unsafe_schemes_and_local_traversal_are_rejected(self):
        for url in ["javascript:alert(1)", "data:text/html,test", "//example.org/file", "java%73cript:alert(1)", "javascript&#58;alert(1)", "/assets/%2e%2e/private", "https://user:password@example.org/file", "https://example.org/line%0abreak"]:
            with self.subTest(url=url), self.assertRaises(importer.PublicationImportError):
                importer.safe_url(url, field="url", key="example")

    def test_safe_filename_collisions_fail(self):
        citation = '''@article{a:b,author={Doe, Jane},title={A paper},year={2020}}
        @article{a/b,author={Doe, Jane},title={B paper},year={2021}}'''
        with self.assertRaisesRegex(importer.PublicationImportError, "same safe filename"):
            importer.prepare_import(citation.encode(), "/assets/bibtex")

    def test_conference_presentations_reports_and_withdrawn_status(self):
        citation = '''@misc{talk,author={Doe, Jane},title={An invited contribution},year={2024},
          entrysubtype={conference presentation},howpublished={The {CFD} Conference}}
        @techreport{report,author={Doe, Jane},title={A technical report},year={2023},institution={SAE International}}
        @inproceedings{withdrawn,author={Doe, Jane},title={Withdrawn: A paper},year={2022},
          booktitle={Conference proceedings},status={withdrawn}}'''
        rows, _ = importer.prepare_import(citation.encode(), "/assets/bibtex")
        self.assertEqual([row["type"] for row in rows], ["conference presentation", "report", "conference"])
        self.assertEqual(rows[0]["venue"], "The CFD Conference")
        self.assertEqual(rows[2]["status"], "withdrawn")
        self.assertEqual(rows[0]["status"], "")
        with self.assertRaisesRegex(importer.PublicationImportError, "status must be"):
            importer.prepare_import(citation.replace("status={withdrawn}", "status={unknown}").encode(), "/assets/bibtex")

    def test_parenthesized_entries_quoted_braces_and_line_comments(self):
        citation = '''% An ignored comment mentioning @article{not-a-record
        @article(quoted, author="Doe, Jane", title="A {CFD} paper", year=2020)
        @article{braced, author={Doe, Jane}, title={A "quoted" title}, year={2021}}
        '''
        rows, downloads = importer.prepare_import(citation.encode(), "/assets/bibtex")
        self.assertEqual([row["id"] for row in rows], ["braced", "quoted"])
        self.assertEqual(rows[1]["title"], "A CFD paper")
        self.assertTrue(downloads["quoted.bib"].startswith(b"@article("))


if __name__ == "__main__":
    unittest.main()
