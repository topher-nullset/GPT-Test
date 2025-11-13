import io
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import lyric_matcher


class TestLyricMatcher(unittest.TestCase):
    def test_read_words_normalizes_and_filters(self):
        with TemporaryDirectory() as tmpdir:
            lyrics_path = Path(tmpdir) / "lyrics.txt"
            lyrics_path.write_text("Hello, HELLO! It's me?", encoding="utf-8")

            words = lyric_matcher.read_words(lyrics_path)

            self.assertEqual(words, ["hello", "hello", "it's", "me"])

    def test_extract_name_words(self):
        words = lyric_matcher.extract_name_words("01-Hello_World!!.mp3")
        self.assertEqual(words, ["01", "hello", "world", "mp3"])

    def test_find_matches(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "hello_world.txt").write_text("", encoding="utf-8")
            (root / "sub").mkdir()
            (root / "sub" / "HELLO-planet.txt").write_text("", encoding="utf-8")
            (root / "sub" / "notes.md").write_text("", encoding="utf-8")

            matches = lyric_matcher.find_matches(root, ["hello", "planet"])

            self.assertEqual(
                [(path.relative_to(root), counts) for path, counts in matches],
                [
                    (Path("hello_world.txt"), {"hello": 1}),
                    (Path("sub/HELLO-planet.txt"), {"hello": 1, "planet": 1}),
                ],
            )

    def test_main_prints_matches(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            lyrics_path = root / "lyrics.txt"
            lyrics_path.write_text("hello planet", encoding="utf-8")

            search_root = root / "files"
            search_root.mkdir()
            (search_root / "planet_hello.txt").write_text("", encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = lyric_matcher.main([str(search_root), str(lyrics_path)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                textwrap.dedent(
                    f"""
                    {search_root / 'planet_hello.txt'}: hello×1, planet×1
                    """
                ).lstrip(),
                buffer.getvalue(),
            )

    def test_main_reports_no_matches(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            lyrics_path = root / "lyrics.txt"
            lyrics_path.write_text("goodbye", encoding="utf-8")

            search_root = root / "files"
            search_root.mkdir()
            (search_root / "hello.txt").write_text("", encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = lyric_matcher.main([str(search_root), str(lyrics_path)])

            self.assertEqual(exit_code, 0)
            self.assertEqual("No matches found.\n", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
