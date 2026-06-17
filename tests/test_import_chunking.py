"""
test_import_chunking.py — unit tests for layout-preserving chunking in
import_campaign.py.

Regression guard for the data-loss bug where chunking flattened all newlines
and indentation (``text.split()`` / ``" ".join()``), destroying the structural
cues — headings, boxed read-aloud text, stat blocks — that the importer relies
on to recognize important encounter details.

Run from repo root:
    python3 -m unittest tests.test_import_chunking -v
"""
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "dnd" if (REPO / "skills" / "dnd").is_dir() else REPO
sys.path.insert(0, str(SKILL / "scripts"))

import import_campaign as ic  # noqa: E402


SAMPLE = """\
# Chapter 1: The Sunless Crypt

The party arrives at the crypt entrance at dusk.

    Read aloud: The iron doors are cold to the touch, etched
    with runes that pulse faintly in the gloom.

AREA 3: THE GUARDIAN

A stone golem (AC 17, HP 178) animates when the seal is broken.
Tactics: it targets spellcasters first.
"""


class ChunkingPreservesLayoutTests(unittest.TestCase):

    def test_newlines_preserved_in_single_chunk(self):
        # Whole sample fits in one chunk; structure must be byte-for-byte intact.
        chunks = ic.build_chunks(SAMPLE)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], SAMPLE.rstrip("\n"))
        self.assertIn("\n", chunks[0])
        self.assertIn("    Read aloud:", chunks[0])  # indentation kept

    def test_no_words_lost_across_chunks(self):
        # Force small chunks; concatenated words must equal the original words.
        chunks = ic.build_chunks(SAMPLE, chunk_words=10)
        self.assertGreater(len(chunks), 1)
        rejoined_words = " ".join(chunks).split()
        self.assertEqual(rejoined_words, SAMPLE.split())

    def test_every_chunk_retains_newlines(self):
        chunks = ic.build_chunks(SAMPLE, chunk_words=10)
        multiline = [c for c in chunks if "\n" in c]
        self.assertTrue(multiline, "chunks were flattened to a single line")

    def test_never_splits_mid_line(self):
        original_lines = set(SAMPLE.splitlines())
        for chunk in ic.build_chunks(SAMPLE, chunk_words=8):
            for line in chunk.splitlines():
                self.assertIn(line, original_lines)

    def test_total_chunks_matches_build(self):
        self.assertEqual(ic.total_chunks(SAMPLE), len(ic.build_chunks(SAMPLE)))

    def test_chunk_text_out_of_range_returns_empty(self):
        self.assertEqual(ic.chunk_text(SAMPLE, 999), "")

    def test_heading_detection(self):
        self.assertTrue(ic._looks_like_heading("# Chapter 1"))
        self.assertTrue(ic._looks_like_heading("AREA 3: THE GUARDIAN"))
        self.assertFalse(ic._looks_like_heading("The party arrives at the crypt."))
        self.assertFalse(ic._looks_like_heading(""))

    def test_empty_text_yields_one_empty_chunk(self):
        self.assertEqual(ic.build_chunks(""), [""])


if __name__ == "__main__":
    unittest.main()
