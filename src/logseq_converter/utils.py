import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Optional


def validate_output_directory(path: Path, force: bool = False) -> None:
    """
    Validates that the output directory is empty if it exists.
    Raises FileExistsError if not empty and force is False.
    """
    if force:
        return

    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Output directory '{path}' is not empty.")


def validate_logseq_source(path: Path) -> None:
    """
    Validates that the source directory appears to be a valid LogSeq graph.
    Checks for existence of 'pages' or 'journals' subdirectories.
    """
    if not path.exists():
        raise FileNotFoundError(f"Source directory '{path}' does not exist.")

    if not path.is_dir():
        raise NotADirectoryError(f"Source path '{path}' is not a directory.")

    pages_dir = path / "pages"
    journals_dir = path / "journals"

    if not pages_dir.exists() and not journals_dir.exists():
        raise ValueError(
            f"Source directory '{path}' does not appear to be a "
            "valid LogSeq graph. Missing 'pages' or 'journals' directories."
        )


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
    return "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")).strip()


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
    cleaned = body_content.replace("-", "").replace("\n", "").replace(" ", "").replace("\t", "")
    return len(cleaned) == 0


def trim_empty_bullets(content: str) -> str:
    """
    Trims leading and trailing empty bullet points (- or *) from markdown content.
    Preserves any page frontmatter if present.
    """
    if not content:
        return content

    # 1. Separate frontmatter if present
    frontmatter = ""
    body = content

    lines = content.split("\n")
    if lines and lines[0].strip() == "---":
        # Find closing ---
        closing_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_idx = i
                break
        if closing_idx != -1:
            frontmatter = "\n".join(lines[: closing_idx + 1]) + "\n"
            body = "\n".join(lines[closing_idx + 1 :])

    # 2. Trim leading and trailing empty bullets/lines from body
    body_lines = body.split("\n")

    start_idx = 0
    while start_idx < len(body_lines):
        line = body_lines[start_idx]
        if not line.strip() or re.match(r"^\s*[-*]\s*$", line):
            start_idx += 1
        else:
            break

    end_idx = len(body_lines)
    while end_idx > start_idx:
        line = body_lines[end_idx - 1]
        if not line.strip() or re.match(r"^\s*[-*]\s*$", line):
            end_idx -= 1
        else:
            break

    trimmed_body = "\n".join(body_lines[start_idx:end_idx])

    # Ensure exactly one trailing newline if the body is not empty
    if trimmed_body:
        trimmed_body = trimmed_body.strip("\n") + "\n"

    return frontmatter + trimmed_body


IGNORE_EXACT_PAGES = {
    "Readwise.md",
    "author.md",
    "category.md",
    "url.md",
    "full-title.md",
    "contents.md",
}

IGNORE_PREFIX_PAGES = (
    "articles___Highlights___",
    "books___Highlights___",
    "podcasts___Highlights___",
    "tweets___Highlights___",
    "hls__",
)


def should_ignore_page(filename: str) -> bool:
    """
    Checks whether a page filename should be excluded from conversion
    (e.g., Readwise highlight dumps, metadata helper pages).
    """
    if filename in IGNORE_EXACT_PAGES:
        return True
    if filename.startswith(IGNORE_PREFIX_PAGES):
        return True
    return False


def transform_tasks_and_schedules(content: str) -> str:
    """
    Transforms Logseq task keywords (TODO, DOING, LATER, NOW, DONE, CANCELLED, WAITING)
    into standard Markdown checkboxes and converts SCHEDULED/DEADLINE metadata into
    standard task emoji format (⏳ for scheduled, 📅 for due/deadline).
    """
    if not content:
        return content

    task_map = {
        "TODO": "[ ]",
        "LATER": "[ ]",
        "DOING": "[/]",
        "NOW": "[/]",
        "DONE": "[x]",
        "CANCELLED": "[-]",
        "CANCELED": "[-]",
        "WAITING": "[?]",
    }

    lines = content.split("\n")
    processed_lines = []

    # 1. Convert task state keywords on list items
    for line in lines:
        match = re.match(
            r"^(\s*[-*]\s+)(TODO|DOING|LATER|NOW|DONE|CANCELLED|CANCELED|WAITING)\b\s*",
            line,
        )
        if match:
            prefix = match.group(1)
            state = match.group(2)
            rest = line[match.end() :]
            checkbox = task_map.get(state, "[ ]")
            line = f"{prefix}{checkbox} {rest}"
        processed_lines.append(line)

    # 2. Process SCHEDULED and DEADLINE
    final_lines: list[str] = []
    for line in processed_lines:
        sched_match = re.search(r"SCHEDULED:\s*<(\d{4}-\d{2}-\d{2})[^>]*>", line)
        dead_match = re.search(r"DEADLINE:\s*<(\d{4}-\d{2}-\d{2})[^>]*>", line)

        if sched_match or dead_match:
            sched_tag = f"⏳ {sched_match.group(1)}" if sched_match else ""
            dead_tag = f"📅 {dead_match.group(1)}" if dead_match else ""
            tags = " ".join(t for t in [dead_tag, sched_tag] if t)

            # Strip SCHEDULED and DEADLINE from the line
            cleaned_line = re.sub(r"SCHEDULED:\s*<[^>]+>\s*", "", line)
            cleaned_line = re.sub(r"DEADLINE:\s*<[^>]+>\s*", "", cleaned_line)

            # If current line is already a list item or task:
            if re.match(r"^\s*[-*]\s+", line):
                base = re.sub(r"SCHEDULED:\s*<[^>]+>\s*", "", line)
                base = re.sub(r"DEADLINE:\s*<[^>]+>\s*", "", base).rstrip()
                final_lines.append(f"{base} {tags}".rstrip())
            elif (
                final_lines
                and re.match(r"^\s*[-*]\s+", final_lines[-1])
                and (not cleaned_line.strip() or cleaned_line.strip() in {"-", "*"})
            ):
                # Indented line with ONLY dates -> attach to previous item
                final_lines[-1] = f"{final_lines[-1]} {tags}".rstrip()
            else:
                if cleaned_line.strip():
                    final_lines.append(f"{cleaned_line.rstrip()} {tags}".rstrip())
                else:
                    final_lines.append(tags)
        else:
            final_lines.append(line)

    return "\n".join(final_lines)
