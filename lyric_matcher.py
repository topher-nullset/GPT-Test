"""Command-line tool to find files whose names contain words from a lyrics file."""
from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

_WORD_PATTERN = re.compile(r"[0-9A-Za-z']+")


def read_words(source: Path) -> Sequence[str]:
    """Read and tokenize words from *source*.

    Words are normalized to lowercase and extracted using ``_WORD_PATTERN`` so
    that punctuation and spacing differences do not affect matching.
    """

    text = source.read_text(encoding="utf-8")
    return _WORD_PATTERN.findall(text.lower())


def extract_name_words(filename: str) -> Sequence[str]:
    """Tokenize a filename into comparable words."""

    return _WORD_PATTERN.findall(filename.lower())


def find_matches(search_root: Path, lyrics_words: Iterable[str]) -> list[tuple[Path, Counter[str]]]:
    """Search ``search_root`` for files whose names contain lyric words.

    Returns a list of tuples containing the file path and a counter describing
    how many times each lyric word appears within the filename.
    """

    lyric_set = set(lyrics_words)
    if not lyric_set:
        return []

    matches: list[tuple[Path, Counter[str]]] = []

    for root, _, files in os.walk(search_root):
        root_path = Path(root)
        for name in files:
            name_words = extract_name_words(name)
            filtered = [word for word in name_words if word in lyric_set]
            if not filtered:
                continue

            counts = Counter(filtered)
            matches.append((root_path / name, counts))

    matches.sort(key=lambda item: (item[0].parent, item[0].name))
    return matches


def format_match(path: Path, counts: Counter[str]) -> str:
    parts = [f"{word}×{counts[word]}" for word in sorted(counts)]
    formatted_counts = ", ".join(parts)
    return f"{path}: {formatted_counts}"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "search_root",
        type=Path,
        help="Directory to search for files",
    )
    parser.add_argument(
        "lyrics_file",
        type=Path,
        help="Path to the text file containing lyrics",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.search_root.is_dir():
        raise SystemExit(f"Search path '{args.search_root}' is not a directory")
    if not args.lyrics_file.is_file():
        raise SystemExit(f"Lyrics file '{args.lyrics_file}' does not exist")

    lyric_words = read_words(args.lyrics_file)
    matches = find_matches(args.search_root, lyric_words)

    if not matches:
        print("No matches found.")
        return 0

    for path, counts in matches:
        print(format_match(path, counts))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
