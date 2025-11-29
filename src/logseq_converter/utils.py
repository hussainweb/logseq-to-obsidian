import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Optional


def validate_output_directory(path: Path) -> None:
    """
    Validates that the output directory is empty if it exists.
    Raises FileExistsError if not empty.
    """
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Output directory '{path}' is not empty.")


def copy_assets(source_assets: Path, dest_assets: Path) -> None:
    """
    Copies assets from source to destination.
    """
    if not source_assets.exists():
        return

    if not dest_assets.exists():
        dest_assets.mkdir(parents=True)

    for item in source_assets.iterdir():
        if item.is_file():
            shutil.copy2(item, dest_assets / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest_assets / item.name, dirs_exist_ok=True)


def log_progress(message: str) -> None:
    """
    Logs progress to stderr.
    """
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()


def log_warning(message: str) -> None:
    """
    Logs a warning to stderr.
    """
    sys.stderr.write(f"WARNING: {message}\n")
    sys.stderr.flush()


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to be safe for file systems.
    Removes Markdown links and Logseq tags.
    """
    # 1. Remove Markdown links: [text](url)
    filename = re.sub(r"\[.*?\]\(.*?\)", "", filename)

    # 2. Remove Logseq tags: #tag
    filename = re.sub(r"#\w+", "", filename)

    # Existing basic sanitization, now allowing periods
    return "".join(
        c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")
    ).strip()


def generate_content_filename(description: str, max_words: int = 10) -> str:
    """
    Generates a filename from a content description by filtering filler words
    and limiting to the first max_words meaningful words.

    Args:
        description: The content description text
        max_words: Maximum number of words to include (default: 10)

    Returns:
        A sanitized filename suitable for file systems
    """
    # Common filler words to filter out
    filler_words = {
        "is",
        "to",
        "but",
        "and",
        "or",
        "the",
        "a",
        "an",
        "in",
        "on",
        "at",
        "for",
        "with",
        "from",
        "by",
        "of",
        "see",
        "are",
        "about",
        "as",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "if",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "must",
        "can",
    }

    # Split into words and filter
    words = description.split()
    meaningful_words = [word for word in words if word.lower() not in filler_words]

    # Take first max_words
    selected_words = meaningful_words[:max_words]

    # Join and sanitize
    filename_base = " ".join(selected_words)
    return sanitize_filename(filename_base)


def handle_filename_collision(path: Path) -> Path:
    """
    Handles filename collisions by appending a unique suffix.
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1

    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def parse_journal_date(filename: str) -> Optional[date]:
    """
    Parses a Logseq journal filename (YYYY_MM_DD.md or YYYY-MM-DD.md)
    into a date object.
    """
    from datetime import datetime

    stem = Path(filename).stem
    formats = ["%Y_%m_%d", "%Y-%m-%d"]

    for fmt in formats:
        try:
            return datetime.strptime(stem, fmt).date()
        except ValueError:
            continue

    return None


def is_markdown_empty(content: str) -> bool:
    """
    Checks if markdown content is empty or nearly-empty.
    Removes frontmatter, then checks if remaining content only has hyphens/whitespace.
    """
    if not content or not content.strip():
        return True

    lines = content.split("\n")

    # Skip frontmatter if present
    start_idx = 0
    if lines and lines[0].strip() == "---":
        # Find closing ---
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start_idx = i + 1
                break

    # Get content after frontmatter
    body_content = "\n".join(lines[start_idx:])

    # Remove characters we want to ignore
    cleaned = (
        body_content.replace("-", "")
        .replace("\n", "")
        .replace(" ", "")
        .replace("\t", "")
    )
    return len(cleaned) == 0
